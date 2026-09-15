## aidlc-workflows skill

---

将亚马逊的aidlc-workflows v1.0转化为Skill形式，以使其更加通用。

你只需要将`.agents`目录复制到你的项目根目录即可使用。

如果你希望该技能全局生效，可以将`.agents`目录复制到你的用户目录，就像其他技能一样。

**使用前提**：技能目录完全自包含——唯一前提是你的 AI 编码工具能加载该技能并能执行 **Python 3.8+**（PATH 中的 `python` 或 `python3`）。技能内置编排引擎（`scripts/engine.py`，仅用标准库），负责工作流路由、阶段状态机与审计转移，无需安装任何其他组件。

下次编码前，只需要加载此技能即可，不需要任何额外的学习成本。

有关aidlc技能的介绍，可以阅读我的文章[**From OpenSpec to AIDLC: How I Improved My Team's AI Code Quality**](https://www.dataleadsfuture.com/from-openspec-to-aidlc-how-i-improved-my-teams-ai-code-quality/)