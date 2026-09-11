# AIDLC v2.0 相比 v1.0 新增特性总结

**日期**：2026-09-10
**状态**：讨论记录（供后续新会话继续讨论）
**范围**：仅记录 v2.0 相对 v1.0 的**特性差异**及其文件/目录对应；不含整合路线与实施决策。
**对照对象**：
- v1.0 = `.agents/skills/aidlc-workflows/`（纯 Markdown 提示词技能）
- v2.0 = `opencode/`（带确定性 TypeScript 引擎的完整脚手架，`AIDLC_VERSION = 2.7.1`）

---

## 0. 本质差异

| | v1.0 (`.agents/skills/aidlc-workflows/`) | v2.0 (`opencode/`) |
|---|---|---|
| 形态 | 一个 SKILL.md + `references/*.md` 提示词 | 三层：opencode 原生层 + 框架引擎 + 数据树 |
| 流程控制 | 模型自行判断 | `aidlc-orchestrate.ts` 确定性引擎 |
| 阶段 | 3 phase / 14 stage，Operation 是占位符 | 5 phase / 33 stage，全生命周期 |
| 输出 | `aidlc-docs/` | `aidlc/spaces/.../intents/<record>/`（多空间多意图） |
| 治理 | 散文规则（`workflow-conventions.md` 的 DOC/APG/AUD/QT 组） | 确定性工具 + 钩子 + 传感器 |

---

## 1. 确定性编排引擎（v1.0 完全没有）

- `opencode/.aidlc/tools/aidlc-orchestrate.ts` — 引擎本体，恰好 5 子命令 `next/continue/report/park/team-board`；`next` 只读且只输出一个 directive。
- `opencode/.aidlc/tools/aidlc-directive.ts` — 冻结的 directive 契约（11 种 kind + `validateDirective`）。
- `opencode/.aidlc/skills/aidlc/SKILL.md` — conductor 转发循环（v1.0 的 SKILL.md 是人工流程，这里是确定性循环）。
- `opencode/.aidlc/aidlc-common/protocols/stage-protocol.md` — 主协议（审批门、语音契约、问题格式）。

## 2. 生命周期扩展：5 phase / 33 stage

- **新增 Initialization**（v1.0 无）：`aidlc-common/stages/initialization/`（workspace-scaffold / workspace-detection / state-init），`skills/aidlc-init/`。
- **新增 Ideation 整相**：`aidlc-common/stages/ideation/`（intent-capture / market-research / feasibility / scope-definition / team-formation / rough-mockups / approval-handoff）。
- **Inception 扩充**：新增 `practices-discovery`、`refined-mockups`、`domain-design`、`contract-design`、`delivery-planning`（v1.0 的 Workflow Planning / Application Design 被拆成这些）。
- **Operation 从占位符变为 7 个真实阶段**：`aidlc-common/stages/operation/`（deployment-pipeline / environment-provisioning / deployment-execution / observability-setup / incident-response / performance-validation / feedback-optimization）。
- 另有新增 `construction/ci-pipeline.md`。

## 3. Scope 系统（自适应流程，v1.0 无）

- `opencode/.aidlc/scopes/` — 11 个 scope（enterprise/feature/classic/mvp/poc/express/bugfix/refactor/security-patch/infra/workshop），决定 33 阶段中哪些 EXECUTE/SKIP。
- `opencode/.aidlc/tools/data/scope-grid.json` — 编译后的 EXECUTE/SKIP 网格。
- `opencode/.aidlc/tools/data/stage-graph.json` — 编译后的阶段 DAG（结构真理）。

## 4. 自适应 Composer + ARS 评分（v1.0 无）

- `opencode/.aidlc/agents/aidlc-composer-agent.md` — 按任务熵值定制流程网格。
- `opencode/.aidlc/tools/aidlc-graph.ts`（`ars`/`validate-grid`）、`opencode/.aidlc/tools/data/ars-priors.json` — Autonomy Risk Score 确定性算术。
- `opencode/.aidlc/skills/aidlc-compose/` — `/aidlc compose` 入口。

## 5. 多智能体系统（v1.0 无独立 agent 概念）

- `opencode/.aidlc/agents/` — 14 个权威 persona（11 领域专家 + 2 只读评审 + composer）。
- `opencode/.opencode/agents/` — opencode 原生 subagent 投影（逐字节复制）。
- `aidlc-common/protocols/stage-protocol-ensemble.md` — 4 种拓扑 inline/subagent/pipeline/mob、contribution file、委派纪律。
- `aidlc-common/protocols/stage-protocol-swarm.md` + `tools/aidlc-swarm.ts` — 自治蜂群。

## 6. 治理机制（v1.0 只有散文审批门）

- **传感器**：`opencode/.aidlc/sensors/`（claim-sources / required-sections / upstream-coverage / traceability / linter / type-check）+ `tools/aidlc-sensor*.ts` — 自动质量检查，gate 可 blocking。
- **评审者协议 §12a**：`aidlc-common/protocols/stage-protocol-reviewer.md` + `tools/aidlc-review-brief.ts` + 冻结钩子。
- **学习仪式 §13（自学习护栏）**：`tools/aidlc-learnings.ts` — 人类纠正沉淀进 `team.md/project.md`；写 `aidlc/spaces/<space>/memory/`。
- **Construction 机制**：Unit/Bolt/Worktree/失败回跳 — `tools/aidlc-unit.ts`、`aidlc-bolt.ts`、`aidlc-worktree.ts`、`aidlc-jump.ts`、`aidlc-testing-posture.ts` + `stage-protocol-construction.md`。

## 7. 持久化、状态与恢复（v1.0 只有 audit.md + aidlc-state.md）

- `tools/aidlc-state.ts`（State Version 8，唯一权威写入者 + 生命周期所有权守卫）
- `tools/aidlc-audit.ts`（91 事件 / 22 类的冻结词表，见 `knowledge/aidlc-shared/audit-format.md`；按 clone 分片）
- `tools/aidlc-runtime.ts` + `runtime-graph.json`（per-workflow 派生图）
- `aidlc-common/protocols/stage-protocol-recovery.md` — 五数据源重建（产物树→memory.md→审计→状态→runtime-graph）
- `tools/data/state-template.md`、`memory-template.md`

## 8. 五层规则系统（v1.0 用 references/*.md 静态加载）

- `aidlc/spaces/<space>/memory/` + `tools/data/memory-seed/` — `org.md → team.md → project.md → phases/<phase>.md → stage` 严格叠加，`load-steering` 以内容送达。
- 对应 `tools/aidlc-steering.ts`、`knowledge/aidlc-shared/rules-reading.md`、`tools/aidlc-rule-schema.ts`。

## 9. 知识资产（v1.0 无）

- **CodeKB**：`aidlc/spaces/<space>/codekb/<repo>/`（棕地反向工程共享存储）
- **Team Knowledge**：`aidlc/spaces/<space>/knowledge/`
- **DocumentKB**：`tools/aidlc-knowledge.ts` + `skills/aidlc-knowledge/`（onboard/sync/show/associate…，文档抽取、不可信数据契约）

## 10. opencode 原生集成层（v1.0 无）

- `opencode/opencode.json`、`opencode/.opencode/command/aidlc.md`、`opencode/.opencode/plugin/aidlc-opencode-adapter.ts`。
- `opencode/.aidlc/hooks/` — 17 个核心钩子（状态转移守卫、计划审批守卫、评审冻结、评审读范围、规则注入等）。
- 四层防御权限模型（见 `AIDLC-PLUGIN.md` §38）。

## 11. 会话/工具技能（v1.0 无）

- 30 个单阶段隔离运行器 `opencode/.aidlc/skills/aidlc-<stage>/` + `tools/aidlc-runner-gen.ts`
- `skills/aidlc-session-cost|aidlc-replay|aidlc-outcomes-pack/` — 成本/回放/成果交接
- `opencode/AIDLC-PLUGIN.md` 是 v2.0 的完整技术文档（权威索引，约 1200 行）。

---

## 12. v1.0 已有概念 → v2.0 对应升级（便于平滑整合）

| v1.0（`.agents/.../references/`） | v2.0 对应 |
|---|---|
| `extensions/security/baseline`、`resiliency/baseline` | **sensors** + `phases/*.md` 护栏 |
| `extensions/context/checkpointing` | `stage-protocol-recovery.md` + `runtime-graph` + 压缩前钩子 |
| `extensions/workflow/autonomous-mode` | Construction 自治模式（Bolt/Swarm + `AUTONOMY_MODE_SET`） |
| `extensions/testing/property-based` | `aidlc-testing-posture.ts` + Testing Contract |
| `common/depth-levels.md` | Scope `depth` + `--depth` 覆盖 |
| `common/content-validation.md` | **sensors**（required-sections/traceability/linter/type-check） |
| `common/overconfidence-prevention.md` | 追问机制 + 学习仪式 |
| `common/session-continuity.md` | intent 游标 + 五数据源恢复 + Resume 菜单 |
| `common/workflow-changes.md` | `recompose`/`jump`/`stage-protocol-recovery` 变更分级 |
| `common/question-format-guide.md` | `question-rendering.md` + `aidlc-log.ts` decision/answer |
