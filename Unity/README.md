# HOMELESS native development fixture

This is an **uncompiled Unity source project**, not a delivered playable build or release-quality scene. No Unity Editor, supported graphics worker, Android SDK/NDK, license, or test device was available on this ARM64 CLI host. All native acceptance remains blocked. The project retains Unity/URP as required by commission §§7,79–80.

The authored synthetic street fixture supplies source for third-person walking/running, camera orbit/collision queries, a skippable arrival camera, independent sidewalk schedules, local traffic, explicit consent to a short passenger ride, cancellation/exit, sitting toggle, spatial original audio signals, touch buttons, mute/reduced motion/pause and bounded local snapshots. These behaviors have **not been observed in Unity**. Cubes/capsules, motions and synthetic sounds are development placeholders and fail the close-up art, human animation, speech and production traffic requirements. The scene is not a geographic reconstruction of Tampa. It assigns an ordinary development member and cannot authenticate or impersonate Dark / Obex Den.

The runtime is a deliberately isolated offline fixture adapter. Its state/events are not production shared-world authority and have not passed cross-language conformance with the portable Dark engine. Local save files are development snapshots; transactional recovery/backup restoration and Android kill tests remain incomplete. Seat transitions explicitly record fixture relocation and do not meet the production animation/collision gate.

## Open and build

1. Install Unity Editor **6000.0.62f1** on a supported host, with licensed access and Android Build Support, SDK/NDK/OpenJDK. Open this directory in that Editor.
2. Resolve the exact **URP 17.0.4** manifest pin. A resolved `packages-lock.json` is intentionally absent: no successful Editor/package resolution has occurred here. Record any import/API errors before changing the pin.
3. Run **HOMELESS → Prepare Native Fixture**. This regenerates only `Assets/Scenes/StreetFixture.unity` and generated rendering settings, creates a Resources material to retain URP Lit in builds, sets ARM64 IL2CPP and Vulkan/OpenGL ES3, and configures the build scene. Keep authored production scenes in separate files. Run this before Play: merely opening the handwritten bootstrap scene does not configure URP.
4. Open the generated scene and press Play. Use WASD, Shift to run, arrows or right mouse to look, Space to skip arrival, E to request the waiting car, X to stop/leave, F near the bench to toggle sitting, Escape to pause. Touch buttons provide movement/look/actions. Sitting currently changes control state only; seated animation is missing.
5. Build from **HOMELESS → Build Android Development APK**, or use the batch command below. The APK uses development signing and is not a release artifact.

```sh
/path/to/Unity -batchmode -quit -projectPath "$PWD/Unity" \
  -executeMethod Dark.Unity.Editor.NativeBuild.Android \
  -logFile "$PWD/Unity/Evidence/android-build.log"
```

Run from repository root. Output on success: `Unity/Builds/HOMELESS-development.apk` and build report. Hash the artifact, preserve Editor log and commit ID, install on an identified Android device, then run the scenario checklist. Headless build success does not certify rendering.

## Portable checks already run

```sh
python3 Unity/Tools/generate_audio.py
python3 Unity/Tools/check_fixture.py
```

Evidence in `Evidence/`: three mono PCM WAV hashes/frame counts/peak/RMS; file/meta integrity; C# tree-sitter syntax only. None is C# compilation, shader import, listening, native playback, performance, geographic acceptance, or visual review.

Version/source verification: [official 6000.0.62f1 release](https://unity.com/releases/editor/whats-new/6000.0.62f1); [official Unity issue using URP17.0.4 with 6000.0.60f1](https://issuetracker.unity.com/issues/8270/the-number-of-shader-variants-increases-from-96-to-186624-when-the-strip-unused-variants-is-set-to-0); [official 6000.0 branch API source](https://github.com/Unity-Technologies/Graphics/blob/6000.0/staging/Packages/com.unity.render-pipelines.universal/Runtime/Data/UniversalRenderPipelineAsset.cs). This establishes candidate compatibility, not successful HOMELESS import. The generic registry metadata omitted 17.0.4 and direct tar acquisition returned 404; package-resolution evidence remains required on the pinned Editor. No Unity binaries/packages were redistributed.
