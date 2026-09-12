# AGENTS.md — aidlc-skills 仓库指南

本仓库是 **AI-DLC（AI-Driven Development Life Cycle）技能的分叉与整合工作区**：以 v1.0 纯 Markdown 技能为基座进行分叉演进，分阶段吸收 v2.0 的先进理念。

**开始任何工作前，先读 `docs/integration-plan.md`**——它记录了全部已确认的决策（D1-D8）、v2.0/v1.0 对比分析、分阶段路线图（Phase 0-4+）和各阶段完成状态，是本仓库的单一权威上下文。

## 目录结构与职责

| 路径 | 性质 | 说明 |
|---|---|---|
| `.agents/skills/aidlc-workflows/` | **工作对象（可写）** | v1.0 分叉，原地进化中。纯 Markdown 技能（SKILL.md + references/），任何 harness 可加载 |
| `opencode/` | **只读参考** | v2.0（opencode 插件形态，v2.7.1）。整合的理念来源，**不要修改**。权威导览见其 `AIDLC-PLUGIN.md` |
| `opencode-cn/` | 只读参考 | v2.0 中文版对应物 |
| `aidlc-workflows-cn/` | 只读参考 | v1.0 中文版对应物（暂不纳入整合范围） |
| `docs/` | 可写 | 项目文档。`integration-plan.md` 是整合路线图 |
| `README.md` / `README_cn.md` | — | 仓库自述 |

## 核心架构约定（v1.0 分叉）

### 1. 阶段契约是唯一事实源（SSOT）

- 每个阶段规则文件（`references/<phase>/*.md`）顶部的 **YAML frontmatter 是阶段清单的唯一事实源**（slug/phase/execution/condition/gate/produces/consumes/requires_stage/for_each/workspace_writes/depth）。
- 字段定义与校验规则见 `references/common/stage-contract.md`。
- SKILL.md、process-overview、welcome-message、terminology、session-continuity、workflow-planning、autonomous-mode 中的阶段清单全部是 **`<!-- BEGIN/END GENERATED: <key> -->` 标记区内的生成物——严禁手改**。

### 2. 作者期生成器

- 脚本：`.agents/skills/aidlc-workflows/scripts/generate.py`（纯 Python 标准库，无第三方依赖）。
- **改动任何阶段 frontmatter 后必须运行**：
  ```cmd
  python .agents\skills\aidlc-workflows\scripts\generate.py
  ```
- 提交前用 `--check` 验证无漂移（非零退出 = 有未同步的生成物）。
- 验收标准：二次运行幂等；标记外内容零改动。
- 所有脚本（含作者期工具）一律放技能目录的 `scripts/` 下（Agent Skills 规范）。

### 3. Harness 无关性护栏（硬约束）

- 技能运行时必须保持**纯 Markdown、零运行时依赖**——不引入引擎、不要求 bun/python/钩子。任何 AI 编码工具加载即用。
- 作者期工具（如 generate.py）只服务技能维护者，不作为运行时的一部分。
- 未来引入编排引擎（Phase 3）时，引擎是**可选增强层**：无引擎环境下技能按约定自路由，照常可用。

### 4. 编辑纪律

- 修改阶段规则：正文可直接改；frontmatter 改动后必须跑生成器。
- 新增阶段 = 新建一个带 frontmatter 的阶段文件 + 跑生成器（无需改其他文件）。
- `opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读。
- 技能文件（SKILL.md、references/）用**英文**撰写；`docs/` 下的工作文档用**中文**。

## 路线图速览（详见 docs/integration-plan.md）

- **Phase 0/1 ✅ 已完成**：阶段契约化 + 生成器（本文件 §核心架构约定即其成果）
- **Phase 2（下一阶段）**：scope 裁剪矩阵（frontmatter 填 `scopes:`，转置生成 EXECUTE/SKIP 矩阵，强化 Workflow Planning）
- **Phase 3**：轻量编排引擎（消费同一契约；定位与技术栈届时再定，决策 D6/D7）
- **Phase 4+ backlog**：persona 体系、reviewer 契约、五层记忆、学习仪式、门仪式精细化、传感器自检清单

## 环境

- Windows 11 + cmd.exe（不要用 PowerShell 语法或 Unix 命令）。
- 生成器只需系统 Python（3.8+），无虚拟环境要求。
