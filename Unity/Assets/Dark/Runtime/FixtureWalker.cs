// HD-030,035: independent bounded schedule fixture, not measured intelligence.
using UnityEngine;
namespace Dark.Unity
{
    public sealed class FixtureWalker : MonoBehaviour
    {
        public string Identity;
        public float Speed,Direction;
        private float wait;
        void Update()
        {
            var world=FixtureBootstrap.Instance;if(world==null||world.Paused)return;
            if(wait>0){wait-=Time.deltaTime;return;}
            var position=transform.position;
            position.z+=Speed*Direction*Time.deltaTime;
            if(Mathf.Abs(position.z)>52){Direction=-Direction;wait=2;}
            // Each walker has an authored sidewalk corridor, separate from traffic.
            transform.position=position;transform.rotation=Quaternion.LookRotation(new Vector3(0,0,Direction));
        }
    }
}
