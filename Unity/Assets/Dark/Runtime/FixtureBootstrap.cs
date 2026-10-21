// HD-007,011,035-038,041-042,048-052,054.1,075,078-080: offline synthetic adapter.
using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Dark.Unity
{
    public sealed class FixtureBootstrap : MonoBehaviour
    {
        public const string PolicyDigest = "e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104";
        public static FixtureBootstrap Instance { get; private set; }
        public FixturePlayer Player { get; private set; }
        public FixtureCamera FollowCamera { get; private set; }
        public FixtureCar Ride { get; private set; }
        public bool ReducedMotion, Muted, Paused;
        public int Projection; // Same semantic state, sky / sign / accessible.
        public string SelectedAction = "ride.request";
        public string Message = "The street is already moving. Explore at your own pace.";
        public readonly List<FixtureEvent> History = new List<FixtureEvent>();
        private readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        private int sequence;
        private bool ready;
        private string SavePath => Path.Combine(Application.persistentDataPath, "development-street-v1.json");

        void Start()
        {
            Instance = this;
            Application.targetFrameRate = 30;
            QualitySettings.vSyncCount = 0;
            Construct();
            Restore();
            ready = true;
        }

        Material Surface(string key, Color color, float smooth = .12f)
        {
            if (materials.TryGetValue(key, out var mat)) return mat;
            var template = Resources.Load<Material>("Fixture/Surface");
            var shader = template ? template.shader : Shader.Find("Universal Render Pipeline/Lit");
            if (!shader) throw new InvalidOperationException("URP Lit missing. Run HOMELESS / Prepare Native Fixture before building.");
            mat = template ? new Material(template) : new Material(shader);
            mat.name=key;mat.color=color;
            mat.SetFloat("_Smoothness", smooth);
            materials.Add(key, mat);
            return mat;
        }

        GameObject Shape(string id, PrimitiveType type, Vector3 position, Vector3 scale, Material material, Transform parent = null)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = id;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = position;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = material;
            return go;
        }

        void Label(string text, Vector3 position, float size, Color color)
        {
            var go = new GameObject("Sign:" + text);
            go.transform.position = position;
            go.transform.rotation = Quaternion.Euler(0, 180, 0);
            var label = go.AddComponent<TextMesh>();
            label.text = text; label.characterSize = size; label.fontSize = 48;
            label.anchor = TextAnchor.MiddleCenter; label.color = color;
        }

        void Construct()
        {
            var asphalt = Surface("Asphalt fixture", new Color(.12f,.15f,.17f));
            var stone = Surface("Walkway fixture", new Color(.58f,.57f,.51f));
            var cream = Surface("Plaster fixture", new Color(.74f,.66f,.51f));
            var teal = Surface("Teal metal fixture", new Color(.08f,.28f,.28f), .4f);
            var glass = Surface("Opaque glass fixture", new Color(.18f,.32f,.37f), .7f);
            var green = Surface("Foliage fixture", new Color(.16f,.29f,.16f));
            var bark = Surface("Bark fixture", new Color(.26f,.19f,.13f));
            var white = Surface("Paint fixture", new Color(.91f,.85f,.66f));
            Shape("ground", PrimitiveType.Cube, new Vector3(0,-.3f,0), new Vector3(110,.5f,150), stone);
            Shape("street", PrimitiveType.Cube, new Vector3(0,-.025f,0), new Vector3(13,.1f,140), asphalt);
            for (int i = -6; i <= 6; i++)
                Shape("lane marking " + i, PrimitiveType.Cube, new Vector3(0,.035f,i*10), new Vector3(.13f,.01f,3.2f), white);
            for (int i = 0; i < 9; i++)
                Shape("crosswalk " + i, PrimitiveType.Cube, new Vector3(-5.6f+i*1.4f,.04f,0), new Vector3(.65f,.01f,3.5f), white);
            for (int side = -1; side <= 1; side += 2)
            {
                Shape("sidewalk " + side, PrimitiveType.Cube, new Vector3(side*10,.02f,0), new Vector3(7,.18f,140), stone);
                for (int i = -3; i <= 3; i++)
                {
                    float z = i*19;
                    float height = 7+(i+3)%3*2;
                    Shape("fictional building " + side + ":" + i, PrimitiveType.Cube, new Vector3(side*22,height/2,z), new Vector3(16,height,16), cream);
                    Shape("awning " + side + ":" + i, PrimitiveType.Cube, new Vector3(side*13.6f,3,z), new Vector3(2,.25f,12), teal);
                    for (int row=0; row<2; row++)
                    for (int col=-1; col<=1; col++)
                        Shape("window", PrimitiveType.Cube, new Vector3(side*13.94f,4.2f+row*2.5f,z+col*4), new Vector3(.08f,1.4f,2.3f), glass);
                    Shape("tree trunk", PrimitiveType.Cylinder, new Vector3(side*11.9f,1.6f,z+8), new Vector3(.3f,1.5f,.3f), bark);
                    Shape("tree crown", PrimitiveType.Sphere, new Vector3(side*11.9f,4,z+8), new Vector3(2.6f,3,2.6f), green);
                    var lamp = Shape("lamp", PrimitiveType.Cylinder, new Vector3(side*7.2f,2,z+8), new Vector3(.1f,2,.1f), teal);
                    Shape("lamp head", PrimitiveType.Sphere, new Vector3(side*7.2f,4,z+8), new Vector3(.35f,.25f,.35f), white);
                }
            }
            Shape("bench seat", PrimitiveType.Cube, new Vector3(10,.65f,6), new Vector3(1.2f,.18f,3), teal);
            Shape("bench back", PrimitiveType.Cube, new Vector3(10.5f,1.15f,6), new Vector3(.15f,1,3), teal);
            Label("COMMON GROUND\ncoffee · conversation", new Vector3(-11.5f,3.8f,-10), .12f, white.color);
            Label("NEXT DEPARTURE\nA shared street, a separate life", new Vector3(0,8,40), .14f, white.color);
            var sun = new GameObject("Late afternoon key").AddComponent<Light>();
            sun.type = LightType.Directional; sun.intensity = 1.6f; sun.color = new Color(1,.87f,.68f);
            sun.shadows = LightShadows.Soft; sun.transform.rotation = Quaternion.Euler(38,-35,0);
            RenderSettings.ambientLight = new Color(.39f,.47f,.53f);
            RenderSettings.fog = true; RenderSettings.fogColor = new Color(.63f,.72f,.75f); RenderSettings.fogDensity = .003f;
            var player = new GameObject("development-member (ordinary, unauthenticated)");
            player.layer = 2; player.transform.position = new Vector3(-9,.2f,-5);
            var cc = player.AddComponent<CharacterController>();
            cc.height = 1.8f; cc.radius = .3f; cc.center = Vector3.up*.9f; cc.stepOffset=.25f;
            Player = player.AddComponent<FixturePlayer>();
            var body = Shape("Player placeholder", PrimitiveType.Capsule, new Vector3(0,.9f,0), new Vector3(.52f,.9f,.52f), teal, player.transform);
            Destroy(body.GetComponent<Collider>()); body.layer = 2;
            var camera = new GameObject("Native follow camera");
            var cam = camera.AddComponent<Camera>(); cam.fieldOfView = 58; cam.nearClipPlane = .12f; cam.farClipPlane = 400;
            camera.tag = "MainCamera"; camera.AddComponent<AudioListener>();
            FollowCamera = camera.AddComponent<FixtureCamera>(); FollowCamera.Target = player.transform;
            for (int i=0;i<8;i++)
            {
                var actor = Shape("inhabitant " + i, PrimitiveType.Capsule, new Vector3(i%2==0?-9:9,1, -38+i*11), new Vector3(.55f,.9f,.55f), i%2==0?teal:cream);
                Destroy(actor.GetComponent<Collider>());
                var walker = actor.AddComponent<FixtureWalker>(); walker.Identity = "synthetic-street/person-"+i;
                walker.Speed = .65f+i*.07f; walker.Direction = i%2==0?1:-1;
            }
            Ride = CreateCar("synthetic-street/car-offer", new Vector3(-3, .5f,-9), teal, white, glass, true);
            CreateCar("synthetic-street/car-background", new Vector3(3,.5f,35), cream, white, glass, false);
            SpatialAudio.Attach(Ride.gameObject, "engine", .18f, true, 35);
            var cafe = new GameObject("Café spatial test ambience"); cafe.transform.position = new Vector3(-12,1,-10);
            SpatialAudio.Attach(cafe, "cafe", .2f, true, 20);
            Emit("fixture.open", "ordinary development member; synthetic geometry; no network authority");
        }

        FixtureCar CreateCar(string id, Vector3 pos, Material paint, Material trim, Material glass, bool offer)
        {
            var car = new GameObject(id); car.transform.position=pos;
            var cc=car.AddComponent<CharacterController>(); cc.height=1.2f;cc.radius=1;cc.center=Vector3.up*.3f;cc.stepOffset=.15f;
            var body = Shape("body",PrimitiveType.Cube,Vector3.zero,new Vector3(1.8f,.8f,4.2f),paint,car.transform);
            Destroy(body.GetComponent<Collider>());
            var cabin = Shape("cabin",PrimitiveType.Cube,new Vector3(0,.65f,-.1f),new Vector3(1.6f,.7f,2.1f),glass,car.transform);
            Destroy(cabin.GetComponent<Collider>());
            for(int side=-1;side<=1;side+=2)
            for(int end=-1;end<=1;end+=2)
            {
                var wheel=Shape("wheel",PrimitiveType.Cylinder,new Vector3(side*.87f,-.3f,end*1.35f),new Vector3(.48f,.16f,.48f),trim,car.transform);
                wheel.transform.localRotation=Quaternion.Euler(0,0,90);Destroy(wheel.GetComponent<Collider>());
            }
            var ride=car.AddComponent<FixtureCar>();ride.IsOffered=offer; return ride;
        }

        public void Emit(string kind, string detail)
        {
            var item = new FixtureEvent { sequence=++sequence, kind=kind, detail=detail };
            History.Add(item); if(History.Count>256)History.RemoveAt(0);
            Debug.Log("HOMELESS fixture event "+JsonUtility.ToJson(item));
        }

        void Update()
        {
            if(Input.GetKeyDown(KeyCode.Escape)) Paused=!Paused;
            AudioListener.pause=Paused;
            AudioListener.volume=Muted?0:1;
        }

        void OnApplicationPause(bool pause) { if(pause)Save(); }
        void OnApplicationQuit() { Save(); }
        public void Save()
        {
            if(!ready || Player==null) return;
            // Passenger saves resume on validated curb, never in a moving un-restored car.
            var pos=Ride.Passenger?new Vector3(-9,.2f,Ride.transform.position.z):Player.transform.position;
            var save=new FixtureSave { schema=1, policyDigest=PolicyDigest, position=pos, muted=Muted, reducedMotion=ReducedMotion, projection=Projection, selectedAction=SelectedAction, history=History.ToArray() };
            try
            {
                var temporary=SavePath+".tmp";File.WriteAllText(temporary,JsonUtility.ToJson(save,true));
                if(File.Exists(SavePath))File.Replace(temporary,SavePath,SavePath+".bak");
                else File.Move(temporary,SavePath);
            }
            catch(IOException ex) { Debug.LogWarning("Fixture save unavailable: "+ex.GetType().Name);Message="Could not save this visit. Keep playing or try again."; }
        }

        void Restore()
        {
            if(!File.Exists(SavePath))return;
            try
            {
                if(new FileInfo(SavePath).Length>1048576)throw new InvalidDataException("snapshot budget exceeded");
                var save=JsonUtility.FromJson<FixtureSave>(File.ReadAllText(SavePath));
                if(save==null||save.history==null||save.history.Length>256)throw new InvalidDataException("history budget exceeded");
                int previous=0;foreach(var item in save.history)
                {
                    if(item==null||item.sequence<=previous||item.kind==null||item.kind.Length>128||item.detail==null||item.detail.Length>2048)throw new InvalidDataException("invalid history");
                    previous=item.sequence;
                }
                if(save.schema!=1||save.policyDigest!=PolicyDigest)throw new InvalidDataException("unsupported snapshot");
                var p=save.position;
                if(float.IsNaN(p.x)||float.IsNaN(p.y)||float.IsNaN(p.z)||float.IsInfinity(p.x)||float.IsInfinity(p.y)||float.IsInfinity(p.z)||Mathf.Abs(p.x)>12||Mathf.Abs(p.z)>65||p.y<-.1f||p.y>4)throw new InvalidDataException("unsafe spawn");
                Player.GetComponent<CharacterController>().enabled=false;Player.transform.position=p;Player.GetComponent<CharacterController>().enabled=true;
                Muted=save.muted;ReducedMotion=save.reducedMotion;Projection=Mathf.Clamp(save.projection,0,2);SelectedAction=save.selectedAction;
                History.Clear();if(save.history!=null)History.AddRange(save.history);
                sequence=History.Count==0?0:History[History.Count-1].sequence;
                Emit("fixture.resume","local development snapshot, safe walking spawn");
            }
            catch(Exception ex) when(ex is IOException||ex is ArgumentException||ex is NullReferenceException)
            { Debug.LogWarning("Fixture restore rejected: "+ex.GetType().Name);Message="Saved visit unavailable. A safe starting point is ready."; }
        }

        void OnDestroy() { foreach(var material in materials.Values)Destroy(material);if(Instance==this)Instance=null; }
    }

    [Serializable] public class FixtureEvent { public int sequence; public string kind,detail; }
    [Serializable] public class FixtureSave
    {
        public int schema,projection;public string policyDigest,selectedAction;public Vector3 position;
        public bool muted,reducedMotion;public FixtureEvent[] history;
    }
}
