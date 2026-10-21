// HD-037,038,075. Presentation control for the explicitly offline development fixture.
using UnityEngine;

namespace Dark.Unity
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class FixturePlayer : MonoBehaviour
    {
        private CharacterController controller;
        private float vertical, footstep;
        private Vector2 touchMove;
        private bool sitting;
        public bool HasInput { get; private set; }
        void Awake() { controller=GetComponent<CharacterController>(); }
        public void SetTouchMove(Vector2 value) { touchMove=value; }
        public void ToggleSit()
        {
            var world=FixtureBootstrap.Instance;
            if(world.Ride.Passenger)return;
            if(!sitting&&Vector3.Distance(transform.position,new Vector3(9,.2f,6))>2)
            { world.Message="Walk beside the bench to sit.";return; }
            sitting=!sitting;
            world.Emit(sitting?"fixture.sit":"fixture.stand","development member");
        }
        void Update()
        {
            var world=FixtureBootstrap.Instance;if(world==null||world.Paused)return;
            var input=new Vector2(Input.GetKey(KeyCode.D)?1:Input.GetKey(KeyCode.A)?-1:0,Input.GetKey(KeyCode.W)?1:Input.GetKey(KeyCode.S)?-1:0)+touchMove;
            input=Vector2.ClampMagnitude(input,1);HasInput=input.sqrMagnitude>.001f;
            if(Input.GetKeyDown(KeyCode.E)) world.Ride.Request();
            if(Input.GetKeyDown(KeyCode.X)) world.Ride.RequestExit();
            if(Input.GetKeyDown(KeyCode.F))ToggleSit();
            if(world.Ride.Passenger)return;
            if(HasInput)sitting=false;
            var yaw=Quaternion.Euler(0,world.FollowCamera.Yaw,0);
            var movement=yaw*new Vector3(input.x,0,input.y);
            var speed=Input.GetKey(KeyCode.LeftShift)?4.3f:2.2f;
            if(sitting)speed=0;
            if(controller.isGrounded&&vertical<0)vertical=-2;
            vertical=Mathf.Max(vertical-9.81f*Time.deltaTime,-30);
            var target=transform.position+movement*speed*Time.deltaTime;
            if(Mathf.Abs(target.x)>12||Mathf.Abs(target.z)>65)movement=Vector3.zero;
            controller.Move((movement*speed+Vector3.up*vertical)*Time.deltaTime);
            if(movement.sqrMagnitude>.001f)
            {
                transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(movement),360*Time.deltaTime);
                footstep+=Time.deltaTime*speed;
                if(footstep>1.5f){footstep=0;SpatialAudio.OneShot(gameObject,"step",.16f);}
            }
        }
    }
}
