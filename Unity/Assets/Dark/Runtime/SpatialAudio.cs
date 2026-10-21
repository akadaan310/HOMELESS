// HD-051,052: original synthetic audio signals; no recorded speech or production mix claim.
using UnityEngine;
using System.Collections.Generic;
namespace Dark.Unity
{
    public static class SpatialAudio
    {
        private static readonly Dictionary<string, AudioClip> Clips=new Dictionary<string, AudioClip>();
        private static AudioClip Load(string name)
        {
            if(!Clips.TryGetValue(name,out var clip)){clip=Resources.Load<AudioClip>("Audio/"+name);Clips[name]=clip;}
            return clip;
        }
        public static void Attach(GameObject host,string clip,float volume,bool loop,float distance)
        {
            var audio=host.AddComponent<AudioSource>();audio.clip=Load(clip);
            audio.spatialBlend=1;audio.rolloffMode=AudioRolloffMode.Logarithmic;
            audio.minDistance=1.5f;audio.maxDistance=distance;audio.volume=volume;
            audio.loop=loop;audio.dopplerLevel=.2f;audio.playOnAwake=false;
            if(audio.clip)audio.Play();
        }
        public static void OneShot(GameObject host,string clip,float volume)
        {
            var audio=host.GetComponent<AudioSource>();
            if(!audio){audio=host.AddComponent<AudioSource>();audio.spatialBlend=1;audio.maxDistance=18;audio.rolloffMode=AudioRolloffMode.Logarithmic;}
            var data=Load(clip);if(data)audio.PlayOneShot(data,volume);
        }
    }
}
