## aidlc-workflows skill

---

A Skill-form adaptation of Amazon's aidlc-workflows v1.0, making it more general-purpose.

Simply copy the `.agents` directory to your project root to use it.

If you want the skill to take effect globally, you can copy the `.agents` directory to your user directory, just like other skills.

**Requirements**: the skill directory is fully self-contained — the only prerequisite is that your AI coding tool can load the skill and run **Python 3.8+** (`python` or `python3` on the PATH). The skill ships a built-in orchestration engine (`scripts/engine.py`, standard library only) that handles workflow routing, the stage state machine, and audit transitions; nothing else needs to be installed.

**Runtime requirements**: Python 3.8+ — standard library only, no third-party dependencies, no pip/venv needed. If Python is missing, install it with one of: Windows `winget install Python.Python.3.12` or the python.org installer · macOS `brew install python3` or `xcode-select --install` · Debian/Ubuntu `sudo apt install python3`.

Before your next coding session, simply load this skill — no additional learning cost is required.

For an introduction to the aidlc skill, read my article [**From OpenSpec to AIDLC: How I Improved My Team's AI Code Quality**](https://www.dataleadsfuture.com/from-openspec-to-aidlc-how-i-improved-my-teams-ai-code-quality/)

Does your AIDLC workflow always drift off track in long sessions? In v0.3.5, I added a script engine based on state machines and graphs that provides deterministic navigation for the workflow, ensuring it no longer drifts. For details, read my article [**Your AI Coding Workflow Keeps Drifting? I Gave It a Navigator**](https://www.dataleadsfuture.com/your-ai-coding-workflow-keeps-drifting-i-gave-it-a-navigator/)