// HD-054.1,075: a common action and selection across fixture projections, touch fallback.
using UnityEngine;
namespace Dark.Unity
{
    public sealed class FixtureInterface : MonoBehaviour
    {
        private TextMesh projection;
        void Start()
        {
            var sign=new GameObject("Shared semantic projection");
            projection=sign.AddComponent<TextMesh>();projection.characterSize=.17f;projection.fontSize=48;
            projection.anchor=TextAnchor.MiddleCenter;projection.color=new Color(.95f,.85f,.53f);
        }
        void Update()
        {
            var world=FixtureBootstrap.Instance;if(!world||!projection||world.Player==null)return;
            projection.text=world.Ride.Passenger?"The street carries on\nYou can leave the ride":"A car is waiting\nOffer: ride along the street";
            projection.gameObject.SetActive(world.Projection!=2);
            projection.transform.position=world.Projection==0?new Vector3(0,18,25):new Vector3(-7,3,-4);
            if(Camera.main)projection.transform.rotation=Quaternion.LookRotation(projection.transform.position-Camera.main.transform.position);
        }
        void OnGUI()
        {
            var world=FixtureBootstrap.Instance;if(!world||world.Player==null)return;
            var original=GUI.matrix;float scale=Mathf.Min(Screen.width/1280f,Screen.height/720f);
            GUI.matrix=Matrix4x4.TRS(Vector3.zero,Quaternion.identity,Vector3.one*scale);
            GUI.Box(new Rect(24,20,625,88),"HOMELESS  ·  a shared street\n"+world.Message);
            if(world.Paused)
            {
                GUI.Box(new Rect(390,180,500,300),"Paused");
                if(GUI.Button(new Rect(420,225,440,52),"Resume"))world.Paused=false;
                if(GUI.Button(new Rect(420,290,440,52),"Save this visit"))world.Save();
                if(GUI.Button(new Rect(420,355,440,52),"Save and exit")){world.Save();Application.Quit();}
            }
            if(GUI.Button(new Rect(1120,20,136,48),world.Paused?"Resume":"Pause"))world.Paused=!world.Paused;
            if(GUI.Button(new Rect(24,118,160,48),"Skip arrival"))world.FollowCamera.Skip();
            if(GUI.Button(new Rect(195,118,160,48),world.Muted?"Sound off":"Sound on"))world.Muted=!world.Muted;
            if(GUI.Button(new Rect(365,118,195,48),world.ReducedMotion?"Motion reduced":"Reduce motion"))world.ReducedMotion=!world.ReducedMotion;
            if(GUI.Button(new Rect(24,177,220,48),new[]{"Sky cues","Street cues","Accessible cues"}[world.Projection]))world.Projection=(world.Projection+1)%3;
            if(world.Projection==2)GUI.Box(new Rect(260,177,450,48),world.Ride.Passenger?"Riding · stop and leave available":"A car is waiting · ride offer available");
            GUI.enabled=!world.Paused;
            if(GUI.Button(new Rect(970,490,260,60),world.Ride.Passenger?"Stop and leave [X]":"Accept ride [E]"))
            {world.SelectedAction=world.Ride.Passenger?"ride.cancel":"ride.request";if(world.Ride.Passenger)world.Ride.RequestExit();else world.Ride.Request();}
            if(GUI.Button(new Rect(970,565,260,60),"Sit / stand [F]"))world.Player.ToggleSit();
            float x=0,z=0,lx=0;
            if(GUI.RepeatButton(new Rect(112,490,76,65),"↑"))z=1;
            if(GUI.RepeatButton(new Rect(30,561,76,65),"←"))x=-1;
            if(GUI.RepeatButton(new Rect(112,561,76,65),"↓"))z=-1;
            if(GUI.RepeatButton(new Rect(194,561,76,65),"→"))x=1;
            if(GUI.RepeatButton(new Rect(785,565,75,60),"Look ←"))lx=-1;
            if(GUI.RepeatButton(new Rect(870,565,75,60),"Look →"))lx=1;
            world.Player.SetTouchMove(world.Paused?Vector2.zero:new Vector2(x,z));
            world.FollowCamera.SetTouchLook(world.Paused?Vector2.zero:new Vector2(lx,0));
            GUI.Label(new Rect(24,655,1200,48),"WASD walk · Shift run · arrows / right mouse look · Space skip · Esc pause");
            GUI.enabled=true;
            GUI.matrix=original;
        }
        void OnDestroy(){if(projection)Destroy(projection.gameObject);}
    }
}
