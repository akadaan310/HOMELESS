// HD-041,042: consented passenger development fixture; not a full road/physics adapter.
using UnityEngine;
namespace Dark.Unity
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class FixtureCar : MonoBehaviour
    {
        public bool IsOffered;
        public bool Passenger { get; private set; }
        private bool stopping;
        private float speed,direction=1;
        private CharacterController controller;
        private const float SeatRadius=3;
        void Awake() { controller=GetComponent<CharacterController>(); }
        public void Request()
        {
            var world=FixtureBootstrap.Instance;if(!IsOffered||Passenger)return;
            if(Vector3.Distance(world.Player.transform.position,transform.position)>SeatRadius||speed>.05f)
            {world.Message="Meet the waiting car beside the crossing.";world.Emit("fixture.ride.refused","distance or motion precondition");return;}
            // This only grants a local fixture passenger mode, never founder or shared-world rights.
            Passenger=true;stopping=false;
            world.Player.GetComponent<CharacterController>().enabled=false;
            world.Player.transform.SetParent(transform,true);
            world.Player.transform.localPosition=new Vector3(-.35f,.5f,0);
            world.Message="Passenger mode. Cancel the ride whenever you like.";
            world.Emit("fixture.ride.accepted","explicit E/button consent; synthetic corridor only");
        }
        public void RequestExit()
        {
            if(!Passenger)return;stopping=true;
            FixtureBootstrap.Instance.Message="Stopping beside the walkway.";
        }
        void Update()
        {
            var world=FixtureBootstrap.Instance;if(world==null||world.Paused)return;
            var target=IsOffered?(Passenger&&!stopping?3:0):2;
            speed=Mathf.MoveTowards(speed,target,Time.deltaTime*1.5f);
            if(Passenger&&transform.position.z>=39)stopping=true;
            if(!IsOffered&&Mathf.Abs(transform.position.z)>56)direction=-direction;
            var forward=new Vector3(0,0,direction);
            controller.Move((forward*speed+Vector3.down*2)*Time.deltaTime);
            // The short authored crossing is stop-controlled; full junction planning is unimplemented.
            if(Passenger&&stopping&&speed<.01f)TryExit();
        }
        void TryExit()
        {
            var world=FixtureBootstrap.Instance;
            // Explicit witnessed relocation to the adjacent collision-ready fixture sidewalk.
            // This is NOT represented as an animated collision-safe production seat transition.
            var exit=new Vector3(-8,.25f,transform.position.z);
            if(!Physics.Raycast(exit+Vector3.up*2,Vector3.down,out _,4,~(1<<2)))
            {world.Message="The walkway is unavailable. Stay seated while we wait.";return;}
            world.Player.transform.SetParent(null,true);world.Player.transform.position=exit;
            world.Player.GetComponent<CharacterController>().enabled=true;
            Passenger=false;stopping=false;
            world.Emit("fixture.ride.exit","witnessed fixture relocation to validated sidewalk; seat animation missing");
            world.Message="Back on the walkway.";
        }
    }
}
