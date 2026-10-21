# Runtime and independent evidence

Contract: Constitutional Commission revision 1.1, SHA-256 `e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104`.

`python3 delivery/inspect_foundations.py` independently reads host metadata and hashes the preserved master archive and nested ZIP members without extracting or executing their code. It writes `inventory.json`. Archive CRC errors, expanded-size budget violations and invalid ZIPs fail the command; unsafe member paths are flagged. The source archives remain unchanged. Inventory values describe this inspection, not future infrastructure.

The inspected host is Ubuntu 22.04 aarch64, two Neoverse-N1 CPUs, approximately 12.5 GB physical RAM, no swap, approximately 8 GB free disk. Unity, Android SDK/NDK, JDK, adb and dotnet were absent from PATH; standard inspected Unity/Android/JVM directories, GPU device nodes and USB device bus were absent. No Android test device or activated Unity Build Automation entitlement is established. No license values or credential contents were read. Network is enabled by the tool environment; service accounts, connectivity and budget remain unverified. A supported Unity build worker with Android modules, license, graphics testing and actual target Android device is required. No spending was authorized or performed. These are HD-008/079/080/081 blockers; portable checks cannot close them.

Git fetch was attempted by the integrator and rejected when writing `/home/ubuntu/homeless/HOMELESS/.git/worktrees/HOMELESS-main/FETCH_HEAD`, outside writable roots. Commit/push require writable shared Git metadata. This runtime worker never modifies the index or Git metadata.

## Source reconciliation (HD-004/009/034/048/085)

The preserved master ZIP hash is `263e7c172e2a9ec9fabb6e916dd6fef03226fa3e21cb78c59c2fe42a0b98db95`. The outer ZIP contains 32 non-directory members. Nested archives and each recursively inspected file have byte counts and SHA-256 in `inventory.json`.

| Foundation | Actual source | Disposition |
| --- | --- | --- |
| Original V2/V3/BORNE | `inputs/HOMELESS_AI_NATIVE_ENGINE_GODSEED_V2.zip`, `inputs/HOMELESS_AI_NATIVE_ENGINE_V3_BORNE.zip` | Preserved, hashed, source candidates; inherited directives not executed. |
| In-Grammar/REALMS | `inputs/ingram-0.1.zip`, `inputs/homeless-realms-0.1.zip`, `inputs/FOUNDATIONS.md` | Preserved, hashed. Reported historical counts are not new measurements. |
| Plicastratum/Ingrammatica/Tashkil | Named Markdown inputs and `inputs/tashkil-kernel-v0.1.zip` | Preserved, hashed; semantic reproduction belongs to mathematics team. |
| World Loom original | No original World Loom archive found among master ZIP members or nested filenames | BLOCKED source recovery. Masterpack `research/REFERENCE_RECONCILIATION.md` explicitly says original archive was absent. Loom-named MUSA research is distinct. |
| Rendezvous V1/V2/V3 riders | No filenames matching Rendezvous/rider in inspected ZIP hierarchy | BLOCKED original rider recovery; current commission §§71–72 still govern implementation. |
| Muse independent research | No Muse-named source in inspected ZIP hierarchy | BLOCKED exact source identification/recovery; not inferred from unrelated corpus. |
| Model weights and audio | No `.onnx`, `.gguf`, `.tflite`, `.wav`, `.ogg`, `.mp3`, `.flac` found in recursively inspected master ZIP hierarchy | No selected voice/model hash or genuine shipped speech/audio established from these foundations. Python voice/model modules are source code, not acquired weights or playable audio. |
| Historical presentation directives | Masterpack reconciliation recommends UE5.8 and alternate founder naming | Superseded by commission §§02/07/09.1: Unity URP, Dark / Obex Den; not executed. |

A missing filename does not prove research was never produced. It identifies the precise gap in this supplied archive. Source rights remain unverified where no explicit license is supplied. No restricted content was imported into the application.

## Native acceptance record

No APK/AAB, native footage, device measurements or Unity import/build result exists from this runtime inspection. HD-087 portable numerical results are reported separately by their executors. HD-088 through HD-095 native geographic, population embodiment, transport, plate, sound, playable, visual and fault/recovery gates remain BLOCKED or NOT_RUN; HD-096 delivery is incomplete; HD-097 commissioner/independent native review is NOT_RUN; HD-098 release acceptance is BLOCKED. Each requires the actual versioned build and direct evidence before a PASS. An asset inventory and a headless test do not substitute for those gates.

Next: establish supported Unity Editor/license/Android modules and a graphics-capable worker; import the pinned project cleanly, build ARM64 APK and content, record command/exit/log/commit/hash, install on an identified Android target, then execute §§87–99 scenarios with continuous footage, telemetry and reviewer scores. Acquire licensed character/motion/vehicle/environment and audio/speech assets through §48 stages before close-up review.

Independent rerun: `python3 -m unittest discover -s governance -p 'test_*.py' -v` passed five COP tests after malformed-input and policy-snapshot issues were reported and corrected by the integrator; see `cop-review.log`. This is bounded compiler/evaluator evidence only. Independently compared all 30 supplied `SHA256SUMS.txt` entries to extracted source bytes: all match (`archive-checksums.json`). Recursively hashed 1,880 file records, with zero unsafe relative ZIP paths. No archived Python/JavaScript/install directive was executed for inventory or checksum comparison.

## Source recovery continuation — 21 October 2026

The earlier missing-source rows above describe the original masterpack inspection. World Loom, Rendezvous V1/V2/V3 and Muse are now recovered separately at f1f1d99. See [recovery inventory](source-recovery-inventory.json), [source reconciliation](../governance/SOURCE_RECONCILIATION.md) and `python3 delivery/recover_sources.py`. Original inventory and historical evidence are retained. Recovery does not change host/build/device status or authorize purchases.
