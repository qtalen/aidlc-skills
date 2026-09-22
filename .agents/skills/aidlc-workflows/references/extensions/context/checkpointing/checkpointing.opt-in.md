# Context Checkpointing — Opt-In

**Extension**: Context Checkpointing

## Opt-In Prompt

The following question is automatically included in the Requirements Analysis clarifying questions when this extension is loaded:

```markdown
## Question: Context Checkpointing Extension
This extension controls how much the AI reloads into its context when a session is resumed. If enabled, the workflow writes a short checkpoint file (key decisions, core constraints, artifact inventory, open items) at the end of each phase/unit. New sessions then reload only these checkpoints plus the current stage's documents, instead of re-reading all previously generated documents and the full audit log — keeping the AI fast and focused as the project grows.

Note: park markers and artifact probing are already default engine capabilities; this extension only governs checkpoint distillation and lightweight loading on top of them.

Should context checkpointing rules (CTX) be enforced for this project?

A) Yes — write checkpoints at each phase/unit boundary and reload only them on session resumption (recommended for long-running, multi-session, or multi-unit projects)

B) No — no checkpoints; each new session reloads all previous stage documents as needed (suitable for small projects completable within a single session)

X) Other (please describe after [Answer]: tag below)

[Answer]: 
```

## Session Resumption Trigger

**Checkpoint-first loading must be in context before any checkpointed stage is resumed. Therefore, when a new session first enters a stage that has an active checkpoint (any CTX-01 checkpoint covering the current phase/unit), check `aidlc-docs/aidlc-state.md` BEFORE applying the tiered reading in `references/common/session-continuity.md`:**

- **If** `## Extension Configuration` shows this extension **Enabled** (opted in during a prior session): load the full rules file `checkpointing.md` (same directory) IMMEDIATELY and apply CTX-02 — restore from the checkpoint first, and let tier-2 required-consumes reads go checkpoint-first within the tiered reading. Enabled extension rules are hard constraints (see SKILL.md Extensions Loading); in case of conflict between an enabled extension rule and a common rule, the enabled extension rule wins for its stated scope.
- **If** the extension is disabled, not configured, or no aidlc-state.md exists: take NO checkpointing action — proceed with the standard tiered reading, and the opt-in prompt above is presented during Requirements Analysis as usual.
