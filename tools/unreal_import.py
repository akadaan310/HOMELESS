"""Execute inside licensed UnrealEditor-Cmd 5.8, never CPython.

Imports actual masters and produces an explicitly incomplete source-asset QA map.
A successful import does not satisfy Tampa scene or cinematic render acceptance.
"""
import json,os,pathlib,traceback
import unreal
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPORT={'schema':'worldloom.unreal-import.v1','engine':unreal.SystemLibrary.get_engine_version(),'assets':[],'scene_kind':'source-art QA fixture; Tampa architecture/crowd/terrain incomplete','hero_scene_acceptance':False,'cooked':False,'failures':[]}
asset_tools=unreal.AssetToolsHelpers.get_asset_tools()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
registry=json.loads((ROOT/'assets/catalog.json').read_text())
def wet_surface_library():
    path='/Game/WorldLoom/Materials'
    collection=asset_tools.create_asset('MPC_WorldWeather',path,unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
    collection.set_editor_property('scalar_parameters',[
        unreal.CollectionScalarParameter(parameter_name='Wetness',default_value=0),
        unreal.CollectionScalarParameter(parameter_name='RainRate',default_value=0)])
    collection.set_editor_property('vector_parameters',[
        unreal.CollectionVectorParameter(parameter_name='WindMetersPerSecond',default_value=unreal.LinearColor(0,0,0,0))])
    material=asset_tools.create_asset('M_SourceAsphaltWeather',path,unreal.Material,unreal.MaterialFactoryNew())
    edit=unreal.MaterialEditingLibrary
    def expression(cls,x,y):return edit.create_material_expression(material,cls,x,y)
    textures={}
    for kind,file in [('Diffuse','asphalt_02_diff_2k.jpg'),('Normal','asphalt_02_nor_gl_2k.jpg'),('Roughness','asphalt_02_rough_2k.jpg')]:
        task=unreal.AssetImportTask();task.filename=str(ROOT/'assets/runtime'/file);task.destination_path=path+'/SourceTextures';task.automated=True;task.replace_existing=True;task.save=True
        asset_tools.import_asset_tasks([task])
        if not task.imported_object_paths:raise RuntimeError('Missing source road map '+file)
        tex=unreal.load_asset(task.imported_object_paths[0])
        tex.set_editor_property('srgb',kind=='Diffuse')
        if kind=='Normal':tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('flip_green_channel',True)
        sample=expression(unreal.MaterialExpressionTextureSample,-700,len(textures)*220);sample.texture=tex
        if kind=='Normal':sample.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
        elif kind=='Roughness':sample.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
        textures[kind]=sample;unreal.EditorAssetLibrary.save_loaded_asset(tex)
    weather=expression(unreal.MaterialExpressionCollectionParameter,-650,650);weather.collection=collection;weather.parameter_name='Wetness'
    mask=expression(unreal.MaterialExpressionOneMinus,-400,500);edit.connect_material_expressions(textures['Roughness'],'R',mask,'Input')
    local=expression(unreal.MaterialExpressionMultiply,-200,500);edit.connect_material_expressions(weather,'',local,'A');edit.connect_material_expressions(mask,'',local,'B')
    wet_rough=expression(unreal.MaterialExpressionLinearInterpolate,0,300);wet_rough.const_b=.055
    edit.connect_material_expressions(textures['Roughness'],'R',wet_rough,'A');edit.connect_material_expressions(local,'',wet_rough,'Alpha')
    darkening=expression(unreal.MaterialExpressionLinearInterpolate,-100,0);darkening.const_a=1;darkening.const_b=.68;edit.connect_material_expressions(local,'',darkening,'Alpha')
    color=expression(unreal.MaterialExpressionMultiply,150,0);edit.connect_material_expressions(textures['Diffuse'],'RGB',color,'A');edit.connect_material_expressions(darkening,'',color,'B')
    edit.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR);edit.connect_material_property(wet_rough,'',unreal.MaterialProperty.MP_ROUGHNESS);edit.connect_material_property(textures['Normal'],'RGB',unreal.MaterialProperty.MP_NORMAL)
    edit.recompile_material(material);unreal.EditorAssetLibrary.save_loaded_asset(material);unreal.EditorAssetLibrary.save_loaded_asset(collection)
    REPORT['weather_material']={'material':material.get_path_name(),'collection':collection.get_path_name(),'source':'PolyHaven asphalt02 actual PBR maps','normal_conversion':'OpenGL green channel flipped for Unreal','shader_test':'editor compile; buffer/image validation still required'}
    return collection
try:
    levels.new_level('/Game/WorldLoom/Maps/TampaEntry')
    weather_collection=wet_surface_library()
    for index,entry in enumerate(registry['assets']):
        source=ROOT/entry['source_file']
        task=unreal.AssetImportTask();task.filename=str(source);task.destination_path='/Game/WorldLoom/Assets/'+entry['id'];task.automated=True;task.replace_existing=True;task.save=True
        asset_tools.import_asset_tasks([task])
        paths=list(task.imported_object_paths)
        if not paths:raise RuntimeError('Importer produced no objects for '+entry['id'])
        loaded=[]
        for object_path in paths:
            obj=unreal.load_asset(object_path)
            if isinstance(obj,unreal.StaticMesh):
                settings=obj.get_editor_property('nanite_settings');settings.enabled=True;obj.set_editor_property('nanite_settings',settings)
                unreal.EditorAssetLibrary.save_loaded_asset(obj)
                actor=actors.spawn_actor_from_object(obj,unreal.Vector(index*500,0,0),unreal.Rotator())
                if actor:actor.set_actor_label('SOURCE_QA_'+entry['id'])
            loaded.append({'path':object_path,'class':obj.get_class().get_name() if obj else 'unloaded'})
        REPORT['assets'].append({'id':entry['id'],'source':entry['source_file'],'imported_objects':loaded,'source_sha256':[f['sha256'] for f in entry.get('files',[])],'status':'imported','rig_contact_test':'pending','collision_navmesh_test':'pending'})
    for cls,pos in [(unreal.DirectionalLight,unreal.Vector(0,0,1000)),(unreal.SkyAtmosphere,unreal.Vector()),(unreal.SkyLight,unreal.Vector(0,0,200)),(unreal.ExponentialHeightFog,unreal.Vector()),(unreal.PlayerStart,unreal.Vector(0,-500,200))]:
        actor=actors.spawn_actor_from_class(cls,pos)
        if isinstance(actor,unreal.DirectionalLight):actor.set_actor_rotation(unreal.Rotator(-35,-25,0),False)
    env=unreal.load_class(None,'/Script/Homeless.WorldLoomEnvironment')
    if env:
        environment=actors.spawn_actor_from_class(env,unreal.Vector())
        environment.set_editor_property('surface_parameters',weather_collection)
    levels.save_current_level()
    REPORT['map']='/Game/WorldLoom/Maps/TampaEntry';REPORT['status']='imported-qa-fixture'
except Exception as exc:
    REPORT['status']='error';REPORT['failures'].append(str(exc));unreal.log_error(traceback.format_exc())
finally:
    path=ROOT/'evidence/unreal_import.json';path.write_text(json.dumps(REPORT,indent=2)+'\n')
if REPORT['failures']:raise RuntimeError('Unreal source import failed; see evidence/unreal_import.json')
