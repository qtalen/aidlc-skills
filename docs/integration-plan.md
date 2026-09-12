# AI-DLC v1.0 分叉整合计划（integration-plan）

> 本文档是 v1.0 分叉（原地进化于 `.agents/skills/aidlc-workflows/`）整合 v2.0 先进理念的**持久参考**。
> 目的：后续阶段的整合工作（以及新的会话）以此为准，不必重复讨论和重新摸底两个版本。
> 创建于 2026-09-11，基于对两个版本的完整源码探查。

---

## 1. 背景与目标

- **v1.0**（`.agents/skills/aidlc-workflows/`）：纯 Markdown 技能形态（SKILL.md + references/ 规则文件），已停止维护。用户使用习惯好，但存在结构性扩展痛点。
- **v2.0**（`opencode/`）：opencode 插件形态（`.aidlc/` 核心 + `.opencode/` 原生层 + `aidlc/` 数据树），版本 2.7.1，含 50+ 个 bun/TS 工具、17 个钩子、33 阶段、11 scope、14 agent。
- **任务**：在 v1.0 上发展独立分叉（**不与原版 v1.0 整合**），吸收 v2.0 的先进理念。
- **硬性约束**：保持 aidlc-workflows 作为技能形态的 **harness 无关性和可移植性**——运行期不引入任何引擎/运行时依赖，纯 Markdown 技能在任何 AI 编码工具中可用。
- **演进方式**：原地进化（`.agents/skills/aidlc-workflows/` 直接修改，git 分支保留历史），分阶段整合，每阶段可独立测试。

### 已确认的决策记录

| # | 决策 | 结论 |
|---|------|------|
| D1 | 阶段体系 | **保持 v1.0 阶段集**（3 相位 14 阶段），不引入 v2.0 的 Ideation 相位和完整 Operation 相位 |
| D2 | 唯一事实源方案 | **方案 A：阶段文件 frontmatter + 作者期生成脚本**（否决方案 B 纯注册表——见 §4.3） |
| D3 | persona/评审者体系 | 暂不引入，后置到 Phase 3+ |
| D4 | 五层记忆/学习仪式 | 暂不引入，后置到 Phase 3+ |
| D5 | 分叉落点 | 原地进化 `.agents/skills/aidlc-workflows/` |
| D6 | 编排引擎定位 | 后置到 Phase 2，契约先行；引擎与技能的关系（可选增强层 vs 必选依赖）Phase 2 再定 |
| D7 | 引擎技术栈 | 暂不决定（候选：Python / bun+TS）；契约设计与引擎语言无关 |
| D8 | 脚本目录约定 | **所有脚本（含作者期工具）放技能目录下的 `scripts/`**，遵循 Agent Skills 规范 |

---

## 2. v2.0 相对 v1.0 的对比分析

### 2.1 v2.0 核心架构哲学

v2.0 的根本理念（其文档原话）：**"判断归 LLM，精确归工具，决定归人类"**（determinism belongs in tools and hooks, knowledge in agents, judgement with humans）。

- **LLM（conductor）负责判断**：扮演领域专家、提问、设计权衡、在审批门向人类呈现决策。
- **TypeScript 工具负责精确**：状态机（走到哪一步）、编排（下一步做什么）、审计日志、传感器校验、并行收敛——绝不由模型在散文中即兴推导。
- **人类负责决定**：每个阶段有强制审批门，不可推断、不可自动批准；自治权永不推断。

用户最想引入的正是这个理念中"**AI 负责生成文案制品和代码，编排引擎负责状态**"的部分。

### 2.2 v2.0 先进理念清单与可移植性分类

图例：**[MD]** 纯 Markdown 可移植 · **[ENGINE]** 需 TS 引擎/钩子才能成立 · **[CONVENTION]** 可降级为约定（写 MUST/NEVER + 自检清单，靠模型自律，无强制力）

#### A. 纯 Markdown 可移植（可搬进 SKILL.md + references/）

| 理念 | v2.0 出处 | 说明 |
|---|---|---|
| **Scope 裁剪矩阵**：同一套阶段 DAG 按任务类型（bugfix/feature/mvp/express/refactor/infra/poc/security-patch/workshop/classic/enterprise 共 11 种）裁剪 EXECUTE/SKIP 与深度 | `.aidlc/scopes/*.md`；矩阵数据在 `tools/data/scope-grid.json` | v1.0 只有逐阶段临时判断，无任务类型预设 |
| **阶段 frontmatter 契约**：`slug/phase/execution/condition/lead_agent/mode/produces/consumes/requires_stage/sensors/scopes/reviewer` 等机器可读字段 | `.aidlc/aidlc-common/protocols/stage-definition.md:44-68` | 阶段文件 = 接口声明 + 规则正文；v2.0 全部派生物（graph/grid）都从这里编译 |
| **审批门仪式精细化**：HARD STOP（呈现门问题后立即结束回合）、NO EMERGENT BEHAVIOR（严格 2 选项）、revision 逃生舱（3 次 Request Changes 后追加 Accept as-is）、non-matching reply 处理 | `protocols/stage-protocol.md:139-236` | v1.0 已有双选项门，v2.0 的仪式更完备 |
| **完成消息 5 段契约**：Announcement → Summary（产物摘要表）→ Review+Approval → Progress 进度行 | `stage-protocol.md:239-310` | |
| **声音/沉默规则**：保留内部词汇表（engine/directive/conductor 等绝不出现在用户面前）、工具调用之间零散文、只复述引擎 narration | `stage-protocol.md:5-86`；`.aidlc/skills/aidlc/SKILL.md:63-77` | 最重要的可移植行为约束之一 |
| **三模式问答**（guided/self-guided/chat）+ 合并总结确认（PRE-GENERATION SUMMARY STOP） | `stage-protocol.md:313-485` | v1.0 已有问题文件 + [Answer]: 机制 |
| **五层规则记忆**：org → team → project → phase → stage，严格可加（strict-additive），窄层不得推翻宽层 | `aidlc/spaces/default/memory/{org,team,project}.md` + `phases/*.md` | v2.0 "越用越好用"的关键；D4 决定后置 |
| **§13 学习仪式**：每阶段末从人类纠正中沉淀实践到记忆层 | `stage-protocol.md:1053-1144` | 后置 |
| **Persona 人格结构**：frontmatter + 知识预载顺序 + Core Responsibilities + Collaboration + Key Principles | `.aidlc/agents/*.md`（14 个） | 后置；纯技能形态可降级为"进入阶段时 inline 扮演" |
| **Reviewer 输出契约**：首行身份标记 + READY/NOT-READY verdict + Finding 表 + 迭代上限 | `.aidlc/agents/aidlc-product-lead-agent.md:129-186` | 后置 |
| **按 agent 分类的知识库** + 加载优先级 | `.aidlc/knowledge/`（14 目录 + aidlc-shared） | 后置 |
| **传感器即自检清单**：required-sections/upstream-coverage/traceability/claim-sources 本质是结构化自检规则 | `.aidlc/sensors/*.md` | linter/type-check 可写为"运行项目 linter 并 halt on failure"约定 |
| **Stage DAG / scope grid 的 Markdown 镜像表** | `.aidlc/skills/aidlc/SKILL.md:189-251` | 数据用表格承载 + "如何按 scope 推导执行阶段"的判断规则 |

#### B. 需要引擎/钩子才能成立（纯 Markdown 无法强制）

| 能力 | v2.0 依赖 |
|---|---|
| 阶段间路由与状态机（next/report；scope 解析、jump、resume、完成判定） | `tools/aidlc-orchestrate.ts`、`aidlc-state.ts` |
| 审批门硬停/收据（HUMAN_TURN、GATE_APPROVED、计划指纹、摘要 digest） | `hooks/aidlc-record-human-turn.ts`、`aidlc-state-transition-guard.ts`、`aidlc-plan-approval-guard.ts` |
| 计划批准门禁（未批准不得生成代码） | `hooks/aidlc-plan-approval-guard.ts` |
| 状态转换守卫（禁止绕过引擎直接改状态） | `hooks/aidlc-state-transition-guard.ts` |
| review-freeze（评审 READY 后写产物即失效） | `hooks/aidlc-review-freeze.ts` |
| reviewer 读范围限制 | `hooks/aidlc-reviewer-scope.ts` |
| 传感器自动触发（写入时匹配、门处 blocking 校验） | `hooks/aidlc-run-sensors.ts` |
| 审计日志自动写入（mkdir 锁、91 事件类型冻结词表） | `hooks/aidlc-write-audit-log.ts` |
| forwarding loop 续跑（session.idle nudge） | `hooks/aidlc-continue-workflow.ts` + 适配器 |
| stage-graph 编译与漂移守卫 | `tools/aidlc-graph.ts compile --check` |
| swarm 并行构建 / worktree | `tools/aidlc-swarm.ts`、`aidlc-bolt.ts`、`aidlc-worktree.ts` |
| 学习的确定性检测/去重/原子写 | `tools/aidlc-learnings.ts` |
| DocumentKB 文档知识目录（事务/索引重建） | `tools/aidlc-knowledge.ts` |

#### C. 可降级为约定（无强制力，诚实标注）

以下在 v2.0 靠钩子硬保证；纯 Markdown 技能中写成 MUST/NEVER + 自检清单，**靠模型自律**：

1. 审批门 HARD STOP、"门未批准不得继续"
2. 生成前先出计划、先获批准
3. READY 评审后不得再改产物
4. 生命周期状态只能经约定流程更新、不得手改 state
5. 阶段仪式原子完成（questions→artifact→review→gate 不可跳步）
6. autonomy 不跨阶段推断
7. 传感器作为提交前自检清单
8. 审计记录（失去防篡改与可重放）

### 2.3 v1.0 现状评估

#### 优势（保留）

- 单编排器 + `references/` 懒加载，上下文友好
- **Extensions opt-in 机制**（扫描 `*.opt-in.md` 轻量存根，opt-in 后才加载完整规则）——非常优雅，v2.0 没有对应物
- 审批门双选项 + NO EMERGENT BEHAVIOR 已具雏形
- aidlc-state.md + audit.md 状态/审计纪律
- 深度自适应（minimal/standard/comprehensive）

#### 结构性痛点（本整合要解决的核心问题）

**阶段清单在 8+ 个文件中重复硬编码**。新增一个阶段至少要改：

| 文件 | 重复内容 |
|---|---|
| `SKILL.md` | 阶段列表（94-101 行）+ 阶段执行块 + 目录结构 |
| `references/common/process-overview.md` | 阶段分类 + Mermaid 流程图 + 阶段描述表 |
| `references/common/welcome-message.md` | ASCII 图阶段行 |
| `references/common/terminology.md` | 各相位阶段清单 |
| `references/common/session-continuity.md` | 恢复时产物加载清单（28-40 行） |
| `references/inception/workflow-planning.md` | 执行计划模板 + 状态文件模板（345-385 行） |
| `references/extensions/workflow/autonomous-mode/autonomous-mode.md` | 硬编码阶段名列表（107 行，最易漏） |

其他已知问题：
- 无 scope 预设（Workflow Planning 靠逐阶段临时判断）
- `workflow-changes.md:114` 与 `workflow-planning.md:224` 的计划产物名不一致（`workflow-planning.md` vs `execution-plan.md`）
- `security-baseline.md:295` 有未解决的 OWASP "2025" 版本存疑 TODO
- Operations 相位是占位符（D1 决定保持现状）

---

## 3. 总体路线：分层架构

```
Phase 0/1（本次执行）  阶段契约化：frontmatter 唯一事实源（借用 v2.0 字段子集）
                       + 作者期生成脚本（scripts/，消除 8 处重复清单）
                       → 运行时仍是纯 Markdown 技能，零依赖

Phase 2                scope 裁剪矩阵（frontmatter 加 scopes: 字段，
                       转置生成矩阵表；强化 Workflow Planning：
                       从"逐阶段临时判断"升级为"先选 scope 再微调"）

Phase 3                轻量编排引擎：消费 Phase 0 的契约（契约文件零改动），
                       接管状态机/路由（next/report 理念）
                       → 引擎定位与技术栈届时再定（D6/D7）
                       → 立场：引擎是增强层；无引擎环境技能照常可用

Phase 4+（backlog）    persona 体系、reviewer 契约、五层记忆、§13 学习仪式、
                       声音/沉默规则强化、门仪式精细化、传感器自检清单
```

**关键架构原则：地基按"未来要盖两栋楼"设计。**

```
阶段文件 frontmatter（唯一事实源，engine-ready）
   ├─ Phase 0/1：scripts/generate.py 读它 → 生成 8 处人类可读清单
   ├─ Phase 2：scope 矩阵从 scopes: 字段转置生成
   └─ Phase 3：引擎直接读它 → 运行时路由/状态
```

三个阶段的后续工作都是**消费方的新增**，事实源本身永不动工——这就是"方案 A 不会返工"的原因。
（方案 B 纯注册表被否决的原因：引擎需要每阶段自声明的契约，注册表路线在 Phase 3 仍需回头补 frontmatter，属重复改造。）

### 为什么不是"引擎先行"

- 引擎的前提是机器可读的阶段契约——没有数据模型，引擎无米下锅。两条路线的第一块砖是同一个。
- 引擎解决的是"谁来路由"（模型→工具），**不能**自动解决文档清单重复（欢迎图、术语表、恢复清单仍是手抄副本，仍需生成脚本）。
- 契约先行让两个阶段独立可交付、可测试。

---

## 4. Phase 0/1 详细计划：阶段契约化 + 作者期生成脚本

> **状态：✅ 已完成（2026-09-11）**。交付物：`references/common/stage-contract.md`（契约规范）、14 个阶段文件的 frontmatter、`scripts/generate.py`（stdlib-only 生成器，含校验与 `--check` 漂移检测）、7 个消费方文件的 13 个 GENERATED 标记区。冒烟测试通过：新增一个阶段文件 + 跑一次脚本即可同步全部 12 个清单元件。SKILL.md 已加契约的按需引用指针（非常驻加载）。
>
> 遗留说明（有意为之的规范化，非 bug）：生成清单中的措辞做了归一（如 `CONDITIONAL - Brownfield only` → `CONDITIONAL`，完整条件在阶段文件 `condition` 字段）；workflow-planning 模板不再预置 `(COMPLETED)` 勾选状态；process-overview 流程图因 requires_stage DAG 补全而边更密。executor 实现时对规格做的三个裁决（记录在案）：inline 标记用原位替换；`depth` 缺失视为未声明（不默认 adaptive 标注）；相位副标题按各渲染场景分别取词。

> 本阶段完成后：扩展痛点解决；运行时仍是纯 Markdown 技能；AI 行为应与改造前一致。

### 4.1 步骤

**Step 1：设计阶段契约规范**
- 新增 `references/common/stage-contract.md`：字段定义、取值约束、校验规则
- 字段（借用 v2.0 子集，见 `opencode/.aidlc/aidlc-common/protocols/stage-definition.md:44-68`）：

| 字段 | 说明 |
|---|---|
| `slug` | 阶段标识，必须 = 文件名 stem |
| `phase` | inception / construction / operations |
| `execution` | ALWAYS / CONDITIONAL |
| `condition` | 执行/跳过条件（把 SKILL.md 里的 Execute IF/Skip IF 散文收编进阶段文件） |
| `produces` | 产物清单（供 session-continuity 加载列表生成） |
| `consumes` | 上游产物依赖 |
| `requires_stage` | DAG 边（软依赖，用于排序与流程图） |
| `gate` | 审批门类型（如 inception 的 approve-continue / construction 的 2-option） |
| `depth` | 深度策略（adaptive 等） |
| `scopes` | **本阶段预留空字段**，Phase 2 填充 |

**Step 2：给 14 个阶段文件加 frontmatter**（机械性；规则正文一字不动）
- inception 7：workspace-detection、reverse-engineering、requirements-analysis、user-stories、workflow-planning、application-design、units-generation
- construction 6：functional-design、nfr-requirements、nfr-design、infrastructure-design、code-generation、build-and-test
- operations 1：operations（占位）

**Step 3：在 8 个消费方文件中圈定生成区**
- 插入 `<!-- BEGIN GENERATED: <key> -->` / `<!-- END GENERATED -->` 标记
- 只生成"清单类"内容；SKILL.md 中各阶段的详细执行块（手写判断指引）**本阶段不生成、不搬动**，SKILL.md 瘦身留给引擎落地时

**Step 4：编写作者期脚本 `scripts/generate.py`**（纯 Python 标准库，仅维护技能时运行）
- 扫描 frontmatter → 校验（slug=文件名、必填字段、consumes 引用存在、DAG 无环）→ 重新生成所有标记区
- `--check` 模式检测漂移（生成物与磁盘不一致时非零退出）

**Step 5：验证**
- 跑脚本逐一审查 diff
- 在真实测试项目 dogfood 一遍技能，确认 AI 行为与改造前一致

### 4.2 范围护栏（本阶段不做）

- 不引入 persona/reviewer、五层记忆、学习仪式
- 不动阶段集、不改审批门仪式、不改 extensions 机制
- 不引入任何运行时依赖；`scripts/` 只是仓库内的维护工具，不是技能运行时的组成部分

### 4.3 补充说明

- 生成脚本虽在技能目录内（`scripts/`），但属作者期工具；技能分发时它是惰性文件，不影响 harness 无关性。
- 顺手修复已知文档不一致（§2.3 的 execution-plan 命名问题），OWASP TODO 单独处理。

---

## 5. Phase 2 预告：scope 裁剪矩阵

- 给阶段 frontmatter 填充 `scopes:` 字段；定义分叉自己的 scope 集（参考 v2.0 的 11 个：`opencode/.aidlc/scopes/*.md`，按 v1.0 的 14 阶段集裁剪）
- 生成脚本转置出 scope 矩阵表（EXECUTE/SKIP），注入 Workflow Planning 规则
- Workflow Planning 升级：先按任务特征选 scope（关键词/显式指定），再做单阶段微调（沿用 v1.0 workflow-changes.md 的增删机制）
- 参考：v2.0 scope frontmatter 字段 `depth/keywords/skeleton/review_cap/testStrategy`（见 `stage-protocol.md:842-875`）

## 6. Phase 3 预告：轻量编排引擎

- 消费 Phase 0 契约，实现 `next/report` 式状态接管（参考 `opencode/.aidlc/tools/aidlc-orchestrate.ts`，仅 5 个子命令：next/continue/report/park/team-board——分叉可更简）
- 届时决策：引擎与技能的关系（可选增强层 vs 必选依赖，D6）、技术栈（Python vs bun+TS，D7）
- 设计立场（已确立）：无引擎环境下技能按约定自路由，照常可用；有引擎环境获得状态硬保证
- 状态文件/审计从"模型维护"平滑过渡到"工具写入"，格式尽量延续
- 注意 v2.0 的现实：硬强制来自钩子（hooks），无钩子的 harness 上引擎同样是"约定 + 工具辅助"——分叉不追求跨 harness 的强制力一致性

## 7. Phase 4+ backlog（优先级待排）

- persona 人格体系（轻量版：进入阶段时 inline 扮演；完整版：14 agent + 知识库）
- reviewer 契约（输出格式、READY/NOT-READY、迭代上限）
- 五层记忆（org→team→project→phase→stage）+ §13 学习仪式
- 门仪式精细化（HARD STOP、revision 逃生舱、non-matching reply 处理）
- 完成消息 5 段契约、声音/沉默规则
- 传感器自检清单化（required-sections / upstream-coverage / traceability / claim-sources）
- PRE-GENERATION SUMMARY STOP 强化

---

## 8. 关键参考文件索引

### v1.0 分叉（工作对象）
- `.agents/skills/aidlc-workflows/SKILL.md` — 主入口（546 行）
- `.agents/skills/aidlc-workflows/references/common/` — 12 个通用规则
- `.agents/skills/aidlc-workflows/references/{inception,construction,operations}/` — 14 个阶段规则
- `.agents/skills/aidlc-workflows/references/extensions/` — 6 个扩展（opt-in 机制）

### v2.0（理念来源，只读参考）
- `opencode/AIDLC-PLUGIN.md` — v2.0 全量技术文档（最权威的导览）
- `opencode/.aidlc/aidlc-common/protocols/stage-definition.md` — 阶段契约字段权威定义
- `opencode/.aidlc/aidlc-common/protocols/stage-protocol.md` — 门仪式/问答/学习/传感器协议
- `opencode/.aidlc/aidlc-common/conductor.md` — conductor 人格手册
- `opencode/.aidlc/scopes/*.md` — 11 个 scope 定义
- `opencode/.aidlc/tools/data/stage-graph.json`、`scope-grid.json` — 编译产物（结构真理）
- `opencode/.aidlc/skills/aidlc/SKILL.md` — v2.0 编排器提示词（268 行）
- `opencode/.aidlc/agents/*.md` — 14 个 persona
- `opencode/aidlc/spaces/default/memory/` — 五层规则种子

### 相关目录说明
- `aidlc-workflows-cn/`、`opencode-cn/` — 两版本的中文对应物（本计划暂不涉及）
