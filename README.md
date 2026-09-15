## aidlc-workflows skill

---

A Skill-form adaptation of Amazon's aidlc-workflows v1.0, making it more general-purpose.

Simply copy the `.agents` directory to your project root to use it.

If you want the skill to take effect globally, you can copy the `.agents` directory to your user directory, just like other skills.

**Requirements**: the skill directory is self-contained — the only prerequisite is that your AI coding tool can load the skill and run **Python 3.8+** (`python` or `python3` on the PATH). The skill ships a built-in orchestration engine (`scripts/engine.py`, standard library only) that owns workflow routing, stage state, and audit transitions; no interpreter beyond stock Python is needed and nothing else is installed.

Before your next coding session, simply load this skill — no additional learning cost is required.

For an introduction to the aidlc skill, read my article [**From OpenSpec to AIDLC: How I Improved My Team's AI Code Quality**](https://www.dataleadsfuture.com/from-openspec-to-aidlc-how-i-improved-my-teams-ai-code-quality/)