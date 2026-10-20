# Delivery targets

GitHub source and engineering prerelease use `codex/one-shot-implementation`; the original `masterpack-v1` release is preserved.

The Sites project ID is retained in `sites/.openai/hosting.json`. Its static client is a cached origin replay until a separately hosted HTTPS World Loom service is configured. It does not deploy Python, Oracle workloads, ASR workers, or an Unreal GPU host. A successful native deployment result is recorded separately; a registered project or guessed URL is not deployment evidence.

`sites/publish_source.py` packages the already-built static client when the installed cloud helper is unavailable in this executor. Credentials enter through hidden stdin, stay in process memory and child Git configuration, and are never written to the checkout or archive. The source commit and immutable archive must match before native publication. Reuse the existing project ID and preserve its owner-private audience.
