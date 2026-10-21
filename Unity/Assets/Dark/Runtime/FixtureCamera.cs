// HD-036-038: bounded follow, skippable introduction and collision query. Native comfort NOT_RUN.
using UnityEngine;

namespace Dark.Unity
{
    public sealed class FixtureCamera : MonoBehaviour
    {
        public Transform Target;
        public float Yaw=15;
        private float pitch=19, introTime;
        private Vector3 velocity;
        private Vector2 touchLook;
        public void Skip() { introTime=6; }
        public void SetTouchLook(Vector2 value) { touchLook=value; }
        void LateUpdate()
        {
            var world=FixtureBootstrap.Instance;
            if(!Target||world==null||world.Paused)return;
            if(Input.GetKeyDown(KeyCode.Space)||world.Player.HasInput||world.ReducedMotion)Skip();
            var mouse=Input.GetMouseButton(1)?new Vector2(Input.GetAxisRaw("Mouse X"),Input.GetAxisRaw("Mouse Y"))*2:Vector2.zero;
            var keyLook=new Vector2(Input.GetKey(KeyCode.RightArrow)?1:Input.GetKey(KeyCode.LeftArrow)?-1:0,Input.GetKey(KeyCode.UpArrow)?1:Input.GetKey(KeyCode.DownArrow)?-1:0)*60*Time.deltaTime;
            var look=mouse+keyLook+touchLook*65*Time.deltaTime;
            Yaw+=Mathf.Clamp(look.x,-120*Time.deltaTime,120*Time.deltaTime);
            pitch=Mathf.Clamp(pitch-look.y,8,55);
            introTime+=Time.deltaTime;
            var subject=Target.position+Vector3.up*1.25f;
            float distance=world.ReducedMotion?5:Mathf.Lerp(9,5,Mathf.SmoothStep(0,1,introTime/6));
            var desired=subject+Quaternion.Euler(pitch,Yaw,0)*new Vector3(0,1,-distance);
            var delta=desired-subject;
            if(Physics.SphereCast(subject,.23f,delta.normalized,out var hit,delta.magnitude,~(1<<2),QueryTriggerInteraction.Ignore))
                desired=subject+delta.normalized*Mathf.Max(.35f,hit.distance-.12f);
            transform.position=world.ReducedMotion?desired:Vector3.SmoothDamp(transform.position,desired,ref velocity,.17f,100,Time.deltaTime);
            transform.LookAt(subject,Vector3.up);
        }
    }
}
