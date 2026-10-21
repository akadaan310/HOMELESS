// HD-007,048,079,080: deterministic native preparation; executed Editor evidence required.
using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Dark.Unity.Editor
{
    public static class NativeBuild
    {
        public const string ScenePath="Assets/Scenes/StreetFixture.unity";
        [MenuItem("HOMELESS/Prepare Native Fixture")]
        public static void Prepare()
        {
            Directory.CreateDirectory("Assets/Settings");
            Directory.CreateDirectory("Assets/Scenes");
            const string pipelinePath="Assets/Settings/HomelessURP.asset";
            var pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(pipelinePath);
            if(!pipeline)
            {
                var renderer=ScriptableObject.CreateInstance<UniversalRendererData>();
                AssetDatabase.CreateAsset(renderer,"Assets/Settings/HomelessRenderer.asset");
                pipeline=UniversalRenderPipelineAsset.Create(renderer);
                pipeline.name="HOMELESS Android URP";pipeline.renderScale=1;pipeline.msaaSampleCount=2;
                pipeline.shadowDistance=45;
                AssetDatabase.CreateAsset(pipeline,pipelinePath);
            }
            Directory.CreateDirectory("Assets/Resources/Fixture");
            const string materialPath="Assets/Resources/Fixture/Surface.asset";
            if(!AssetDatabase.LoadAssetAtPath<Material>(materialPath))
            {
                var lit=Shader.Find("Universal Render Pipeline/Lit");
                if(!lit)throw new InvalidOperationException("URP Lit was not imported.");
                AssetDatabase.CreateAsset(new Material(lit),materialPath);
            }
            GraphicsSettings.defaultRenderPipeline=pipeline;
            QualitySettings.renderPipeline=pipeline;
            PlayerSettings.companyName="Obex Den";PlayerSettings.productName="HOMELESS";
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,"com.obexden.homeless");
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{GraphicsDeviceType.Vulkan,GraphicsDeviceType.OpenGLES3});
            // Legacy Input is intentionally used for the development fixture. Enable both in Player settings if migrating.
            var settingAssets=AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset");
            if(settingAssets.Length>0)
            {
                var settings=new SerializedObject(settingAssets[0]);
                var input=settings.FindProperty("activeInputHandler");if(input!=null){input.intValue=0;settings.ApplyModifiedProperties();}
            }
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var root=new GameObject("HOMELESS synthetic development fixture");
            root.AddComponent<FixtureBootstrap>();root.AddComponent<FixtureInterface>();
            if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new InvalidOperationException("Could not save generated fixture scene.");
            EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(ScenePath,true)};
            AssetDatabase.SaveAssets();
            Debug.Log("HOMELESS prepared synthetic native fixture; policy "+FixtureBootstrap.PolicyDigest);
        }
        [MenuItem("HOMELESS/Build Android Development APK")]
        public static void Android()
        {
            Prepare();
            if(!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android,BuildTarget.Android))throw new InvalidOperationException("Install Android Build Support with SDK/NDK/OpenJDK for the pinned Editor.");
            Directory.CreateDirectory("Builds");
            EditorUserBuildSettings.buildAppBundle=false;
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{ScenePath},locationPathName="Builds/HOMELESS-development.apk",target=BuildTarget.Android,options=BuildOptions.Development});
            File.WriteAllText("Builds/build-report.json",JsonUtility.ToJson(new BuildEvidence{result=report.summary.result.ToString(),bytes=report.summary.totalSize,policyDigest=FixtureBootstrap.PolicyDigest,editor=Application.unityVersion},true));
            if(report.summary.result!=BuildResult.Succeeded)throw new InvalidOperationException("Android build failed: "+report.summary.result);
        }
        [Serializable] private class BuildEvidence {public string result,policyDigest,editor;public ulong bytes;}
    }
}
