# Autonomous Mode Trigger

**This file is intentionally lightweight and declares no opt-in prompt — it never presents an opt-in question during Requirements Analysis. Its sole purpose is deferred loading of the full rules.**

The full rules file is `autonomous-mode.md` (same directory, per naming convention). Do NOT load it at workflow start. Load it IMMEDIATELY when either condition is met:

1. **Trigger phrase detected**: ANY user message, at ANY point in the conversation, semantically expresses entering/enabling autonomous mode — in any language. Examples (non-exhaustive): "进入自主模式", "开启自主模式", "启用自主模式", "enter autonomous mode", "enable autonomous mode", "turn on autonomous mode", "go autonomous".
2. **Persisted state detected**: At workflow start or session resumption (of an ACTIVE workflow round), `aidlc-docs/aidlc-state.md` contains a `## Autonomous Mode` section with `Enabled: Yes`. A completed workflow never carries a live mode: the engine expired it at round end and heals any pre-AM-10 stale `Yes` at re-entry (AM-10); treat a completed workflow that still reads `Enabled: Yes` as expired and flip it per AM-08 before continuing.

After loading, follow the rules in `autonomous-mode.md` (AM-01 ~ AM-10). Until then, take NO autonomous-mode action — pause/exit phrases are meaningless while the mode was never activated in this session.
