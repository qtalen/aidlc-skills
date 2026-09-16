# AI-DLC v1.0 分叉整合计划（integration-plan）

> 本文档是 v1.0 分叉（原地进化于 `.agents/skills/aidlc-workflows/`）整合 v2.0 先进理念的**持久参考**。
> 目的：后续阶段的整合工作（以及新的会话）以此为准，不必重复讨论和重新摸底两个版本。
> 创建于 2026-09-11，基于对两个版本的完整源码探查。

---

## 1. 背景与目标

- **v1.0**（`.agents/skills/aidlc-workflows/`）：纯 Markdown 技能形态（SKILL.md + references/ 规则文件），已停止维护。用户使用习惯好，但存在结构性扩展痛点。
- **v2.0**（`opencode/`）：opencode 插件形态（`.aidlc/` 核心 + `.opencode/` 原生层 + `aidlc/` 数据树），版本 2.7.1，含 50+ 个 bun/TS 工具、17 个钩子、33 阶段、11 scope、14 agent。
- **任务**：在 v1.0 上发展独立分叉（**不与原版 v1.0 整合**），吸收 v2.0 的先进理念。
- **硬性约束**：保持 aidlc-workflows 的 **harness 无关性**——任何能加载技能且能执行 shell 的 AI 编码工具可用，不绑定特定 harness 的钩子/插件机制。（**2026-09-14 修订**：Phase 3 起引入**单一运行时依赖 Python 3.8+**（编排引擎必选，D6 修订）；原"零运行时依赖、纯 Markdown"措辞废止，修订理由见 §9。）
- **演进方式**：原地进化（`.agents/skills/aidlc-workflows/` 直接修改，git 分支保留历史），分阶段整合，每阶段可独立测试。

### 已确认的决策记录

| # | 决策 | 结论 |
|---|------|------|
| D1 | 阶段体系 | **保持 v1.0 阶段集**（3 相位 14 阶段），不引入 v2.0 的 Ideation 相位和完整 Operation 相位 |
| D2 | 唯一事实源方案 | **方案 A：阶段文件 frontmatter + 作者期生成脚本**（否决方案 B 纯注册表——见 §4.3） |
| D3 | persona/评审者体系 | 暂不引入，后置到 Phase 3+ |
| D4 | 五层记忆/学习仪式 | 暂不引入，后置到 Phase 3+ |
| D5 | 分叉落点 | 原地进化 `.agents/skills/aidlc-workflows/` |
| D6 | 编排引擎定位 | **必选运行时依赖**（2026-09-14 修订，取代原"可选增强层"立场）：单一依赖 Python 3.8+，无引擎 = HARD STOP 提示安装。修订理由见 §9 |
| D7 | 引擎技术栈 | **Python 标准库**（2026-09-14 定）：与 generate.py 同栈，零第三方依赖；"契约设计与引擎语言无关"仍成立 |
| D8 | 脚本目录约定 | **所有脚本（含作者期工具）放技能目录下的 `scripts/`**，遵循 Agent Skills 规范 |
| D9 | 契约消费方式 | **compile-to-JSON**（2026-09-14）：作者期 generate.py 编译 `scripts/data/stage-graph.json`，引擎运行时只读 JSON，解析器风险关在作者期 |
| D10 | 状态/审计归属 | **引擎原子写**（2026-09-14）：Markdown 状态 + 审计转移条目 + State Digest 完整性校验（检测非阻止，详见 §6.3-B8） |
| D11 | 多 intent / compose | **不排期，仅记录**（2026-09-14）：一版本一产品意图，两件事 = 两个 git 版本；若重启须与 Team Construction 协同设计（§7） |
| D12 | 引擎分发形态 | **随技能分发**（2026-09-14）：engine.py + stage-graph.json 在 `scripts/` 下随技能目录一起复制；用户侧前提仅"harness 能加载技能 + 能执行 python"，不依赖 AGENTS.md 等任何额外文件；裸项目 dogfood 为验收硬标准 |

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
Phase 0/1（✅ 已完成） 阶段契约化：frontmatter 唯一事实源（借用 v2.0 字段子集）
                       + 作者期生成脚本（scripts/，消除 8 处重复清单）
                       → 运行时仍是纯 Markdown 技能，零依赖
                       （Phase 0/1 时点表述；Phase 3 起废止，见 §1 修订）

Phase 2（✅ 已完成）   scope 裁剪矩阵（frontmatter 加 scopes: 字段，
                       转置生成矩阵表；强化 Workflow Planning：
                       从"逐阶段临时判断"升级为"先选 scope 再微调"）

Phase 3（✅ 已完成）     轻量编排引擎："判断归 LLM，精确归工具，决定归人类"落地
                       Python stdlib 必选引擎 + compile-to-JSON + next/report/
                       status/jump + 状态完整性校验 + 单元清单结构化
                       （交付物与实施期裁决见 §6 状态段）

Phase 4                Team Construction：unit-major 波次编排（硬地基）→
                       claim/release + worktree 多会话团队（形态 A，harness 无关）→
                       single 单阶段重跑（试验-收敛闭环）→
                       swarm 进程内并行（形态 B，harness 相关，可再拆）

Phase 5+（backlog）    reviewer 状态机、传感器阻塞校验、persona 体系、
                       五层记忆 + §13 学习仪式、门仪式精细化、
                       完成消息 5 段契约、声音/沉默规则
```

**关键架构原则：地基按"未来要盖两栋楼"设计。**

```
阶段文件 frontmatter（唯一事实源，engine-ready）
   ├─ Phase 0/1：scripts/generate.py 读它 → 生成 8 处人类可读清单
   ├─ Phase 2：scope 矩阵从 scopes: 字段转置生成
   └─ Phase 3：编译为 scripts/data/stage-graph.json → 引擎只读 JSON 做运行时路由/状态
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
>
> 审查修复（Phase 0/1 审查，与 Phase 2 审查同修）：🟡 修 execution-plan 命名（workflow-changes.md Type 5，此前声称已修实际未落地，见上方更正）；新增 `.github/workflows/contract-check.yml` CI 兜底（--check 漂移检测）；契约 `depth` 字段语义对齐实现（缺失=未声明，仅显式 adaptive 渲染标注）；depth-levels.md 的 Application Design 产物示例对齐 SSOT（component-diagram.md 系历史残留，已更正为真实产物清单）；解析器 `_strip_inline_comment` 静默截断 bug 修复（引号内 " #" 不再被截）+ 新增 `scripts/tests/` 20 个 unittest（解析边界/校验/幂等/漂移检测）；B5 数据精度三处（WP 补 consumes questions 文件、B&T 的 code 产物 required→true、契约 §4 补 audit.md 归因说明）。遗留 backlog：`--check` 重复 key 僵尸区与 key 前缀误配两个逃逸场景、保留键报错信息优化、中缀 glob 约定、Operations 的 CONDITIONAL 语义（Phase 4+ 评估 NEVER 值）、welcome ASCII 截断保护；Phase 3 设计提示：execution-plan.md 无消费者、condition 为散文、第三选项在正文（引擎落地时收口）；D7 决策参考：v2.0 compile-to-JSON 模式（运行时只读编译产物，把解析器风险关在作者期）。

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
- ~~顺手修复已知文档不一致（§2.3 的 execution-plan 命名问题）~~——**更正（Phase 0/1 审查发现）**：该修复当时未实际落地，`workflow-changes.md` Type 5 仍指向 `workflow-planning.md`；已在审查修复批次中真正修复（改为 `execution-plan.md` + `aidlc-state.md` 的 Depth 行）。OWASP TODO 单独处理。

---

## 5. Phase 2：scope 裁剪矩阵

> **状态：✅ 已完成（2026-09-12）**。交付物：`references/common/scopes/` 6 个 scope 定义（classic[默认]/bugfix/refactor/security-patch/infra/express，v2.0 对齐命名）；14 个阶段 frontmatter 填充 `scopes:` 映射；stage-contract.md §6（scope registry 规范、成员语义、选择与 depth 绑定）+ §7 校验规则 9-12；generate.py 新增 scope registry 解析、完整性校验与两个渲染器（`scope-catalog` 注入 Requirements Analysis、`scope-matrix` 注入 Workflow Planning）；RA 新增 Step 2.5（关键词启发式推荐 + 用户确认，显式指定优先）；WP 新增 Step 3.0（scope 基线 + 单阶段微调），计划/状态模板记录 Scope/Depth。
>
> 关键决策（本轮确认）：精简 6 个 scope——`poc`/`mvp`/`workshop` 依赖 Operations 补齐后才有区分度，届时再引入；`enterprise` 用 depth 表达；命名对齐 v2.0 以便 Operations 补齐后各 scope 只需"扩行"（如 bugfix 追加 deployment 阶段），定义本身不改。运行时上下文纪律：AI 只看生成的矩阵/目录表（~35 行），scope 文件本体按需加载（仅被选中的那个）。
>
> 有意分歧（记录在案）：`infra` scope 保留 code-generation EXECUTE（v2.0 跳过它用独立 ci-pipeline 阶段，我们的 CG 负责写 IaC）；矩阵列序 = default 优先 + 字母序（classic, bugfix, express, infra, refactor, security-patch）。
>
> 审查修复（reviewer 全面审查后）：🔴 隐式单单元约定——scope 跳过 units-generation 时 per-unit 阶段对全任务执行一次（WP Step 3.0 约定 + CG/FD/NFR-req/infra-design 前提条件化 + 生成器 advisory 规则 16 防回归）；🟡 SKILL.md 加 scope 总则（scope SKIP 的阶段不得重新评估）、RA Step 2.5 明确确认为门式聊天选择（豁免问题文件规则）+ 新功能请求优先 classic 的关键词优先级规则 + audit 显式记录、depth-levels.md 更新两层选择描述（"Scope"因子改名 "Change footprint" 消歧）、契约 default 字段语义对齐生成器（恰好一个）；🔵 workflow-changes.md 新增 Type 9（re-scope）、terminology.md 加 scope 消歧词条、session-continuity 恢复时读取活跃 Scope（无记录按 classic）。遗留 backlog：infra 在 brownfield 下 RE=SKIP 的代价提示、解析器 `_strip_inline_comment` 对含 " # " 引号字符串的边界 bug、scope depth enum 是否加 `adaptive`（Phase 3 再评估）。

- ~~给阶段 frontmatter 填充 `scopes:` 字段~~ ✅
- ~~生成脚本转置出 scope 矩阵表（EXECUTE/SKIP），注入 Workflow Planning 规则~~ ✅
- ~~Workflow Planning 升级：先按任务特征选 scope（关键词/显式指定），再做单阶段微调~~ ✅

## 6. Phase 3 实施方案：轻量编排引擎（✅ 已完成 2026-09-14）

> **状态：✅ 已完成（2026-09-14）**。交付物：`scripts/engine.py`（Python stdlib 必选运行时引擎，子命令 status/init/next/report/jump/jump --fresh/rebase，~1000 行）+ generate.py 编译渲染器（`scripts/data/stage-graph.json`，--check 覆盖漂移）+ `references/common/engine-contract.md`（B11 分区所有权矩阵 + directive 消费契约 + 转移语义矩阵 + 完整性/rebase 流程）+ SKILL.md 引擎化改写（Engine Bootstrap 启动探测 HARD STOP + Orchestration Loop 主循环 + 阶段块撤路由散文 + per-unit report 总注）+ 全部 references/ 手改 state 指令收口（D23，含清单外捕获的 reverse-engineering.md）+ error-handling.md 恢复协议重定向（halt→人工确认→rebase）+ WP Step 8 重写（Execution Plan Summary 结构化行，state-template-stages 生成区删除）+ 单元清单结构化（units-generation Step 19 写 `## Units` 模型辖区，state 引擎辖区预留 `## Unit Progress`）。测试：`scripts/tests/` 共 77 例（生成器 30 + 引擎 47）全绿、generate 二次运行幂等、--check 零漂移；裸项目 dogfood 通过（greenfield 全流程走通至 done、brownfield bugfix scope 裁剪、篡改触发 integrity-violated halt→rebase、中断恢复、backward jump、jump --fresh 归档）。
>
> 实施期裁决（记录在案）：①per-unit（for_each）阶段引擎单次发射、单元内循环归模型，`report` 在最后一个单元门批准后调用一次（5 个 construction 阶段文件均补 per-unit note）；②审计交叉核验在存在 STATE_REBASELINED 事件后豁免（否则 rebase 无法真正"重定基线"）；③`jump` 到计划外阶段返回 `note` 提示需补 Stages to Execute 行（路由纯化，jump 不绕过 scope/计划过滤）；④`--workspace` 参数位子命令之后（调用约定 `engine.py <subcommand> [--workspace <path>]`）；⑤CLI 错误一律 error JSON + 退出码 1（usage 错误同形）；⑥engine-contract.md 将 init/report/jump/rebase 的成功输出记为"通用 JSON 确认对象"（消费方忽略未知字段兜底）。
>
> **二次 dogfood 与增量修复（2026-09-15，course-schedule 真实项目 dogfood）**：结论——引擎下限收益已兑现（长离题后状态零歧义恢复、契约缺陷 fail-fast 暴露逗号解析 bug、审计双轨），上限收益（多单元循环、多会话、完整性防漂移）待 Phase 4 场景验证；单单元线性小项目中 stage-major 够用，佐证 Phase 3 排序正确。落地三项增量修复：⑦`_slug_list` 注册表感知容错重组（理由含英文逗号不再误报 unknown slug）；⑧所有 JSON 输出（含 error 与 usage 错误）统一注入 `timestamp` 字段（ISO 8601 UTC 秒级），AUD 时间戳获取规则改为优先读引擎输出；⑨节标题静默回退让位于 fail-fast——`_parse_plan` 检测"计划形态行存在但精确 `## Execution Plan Summary` 标题缺失"并报 plan-invalid（信息性副本与占位符模板豁免，不违背 §6 informational-copies 条款）。配套：workflow-conventions QT-02 补"唯一上下文 Edit 回写、勿用临时脚本"实现提示；AGENTS.md §4 新增"先考证，后修复"编辑纪律（考证 integration-plan 决策/契约字段语义后再动手）；测试 77 → 96 全绿，--check 零漂移。考证修正两条初判：consumes 的 `required` 语义本就写明"生产者被计划跳过则 moot"（stage-contract §2），非缺陷；节标题回退是记录在案的已知弱点，修复方案因此收窄检测条件。
>
> **技能加载 token 测量与 engine-contract 加载策略调整（2026-09-15，同日讨论后落地）**：course-schedule dogfood 全程实测——共加载 18 个技能文件约 171 KB（≈4.3 万 tokens，字节数÷4 粗估），另加引擎 JSON 输出约 1.5k tokens；相对无引擎版本净增约 +15%，其中最大单项是 engine-contract.md（18.7 KB，被 SKILL.md Common Rules 块强制每次加载）。考证结论：integration-plan 无任何决策要求强制加载，属 Phase 3 SKILL.md 改写时的分组惯性；stage-contract.md 已有"维护文档按需加载"先例；SKILL.md 自身在 5 处（legacy/integrity/完整契约/directive/所有权矩阵）已按指针使用。决策（用户批准方案 A）：engine-contract.md 移出 Common Rules ALWAYS 清单，改为按需加载——触发条件集中在 SKILL.md bootstrap 表后的指引句（legacy/integrity 行指向、jump/rebase 前、引擎错误或状态格式争议时）；engine-contract §1 Load 口径同步改写。安全性依据：happy path 实证不依赖契约内容（指令 JSON 自描述 + 错误消息自解释），误用由引擎 fail-fast 校验兜底。瘦身方案（§10 Mermaid 样例下沉）经评估暂缓——按需加载后频率低，性价比不足。预期效果：引擎 token 增量从 +15% 压至 ~+3-4%（余量为 SKILL.md 引擎化改写净增与 JSON 输出）。注：本次真正省 token 的是 Phase 2 扩展延迟加载（4 个扩展全 opt-out，只读 opt-in 文件），非引擎。同日评估 SKILL.md 本体瘦身（Phase 3 使其 27.4→35.4 KB，+29%：Bootstrap ~2KB + Orchestration Loop ~1.8KB + 12 行 per-stage report 样板 ~2.6KB + 所有权改写 ~1KB + 两处注记 ~0.9KB）：per-stage 样板与 Orchestration Loop 第 3 步纯冗余（可省 ~1.5-2KB）、Bootstrap 安装指引可压缩（~0.3-0.5KB）、阶段块步骤摘要（~22KB，pre-engine 存量，涉 v1.0 设计性格）可单独立项——**全部暂缓**（2026-09-15 决定），因 engine-contract 按需化节省的 18.7KB 已超 SKILL.md 引擎化净增，引擎版每会话加载量已低于无引擎版。reviewer 复审（2026-09-15）有条件通过并落地两处修复：①契约 §4 三条 MUST（禁止伪造 report——non-gated 阶段引擎无法甄别、放弃 directive 由 next 重发、忽略未知字段）压缩进 SKILL.md Orchestration Loop 纪律行，原 L135 指针降格为出处注记，contract §1 触发枚举删去 "or orchestration loop"；②session-continuity.md 恢复菜单 B（jump）补预警——后跳会把目标及其后所有阶段重置为 `[ ]`，执行前须告知用户（该菜单是唯一由必载文档直接驱动 jump 的路径）。遗留：legacy handling 仅为契约 §10 样例旁注（存量问题），留待下次契约维护。
>
> **reviewer 全面复审与修复批次（2026-09-16，Phase 0-3 复审）**：reviewer 只读复审 + 主智能体逐条实码验证（文档步骤、引擎代码路径、测试反证三层证据链），确认三项实质缺陷并当日修复：⑩workflow-changes.md Type 1/2 执行协议与引擎路由语义冲突（引擎每次调用按计划行即时重算 current，且 Skip > Execute 恒胜）——Type 1"加 Execute 行后 jump"会被 invalid-jump 拒绝（目标通常已成 current，hint 不对症）或 forward jump 误标中间未执行阶段 `[S]`，且未指示先删 Skip 行时加回静默失效；Type 2"先写 Skip 行再 report"必报 invalid-transition（current 已被重算移走）。修正为与引擎语义对齐：Type 1 = 删 Skip 行（如在）→ 加 Execute 行 → 直接 `next`；Type 2 = current CONDITIONAL 阶段先 `report skipped` 后写 Skip 行，其余阶段先写 Skip 行再 `next`；jump 保留给重做/回退（Type 3/4）；error-handling.md 同族步骤与决策树同步修正。⑪截断状态（BEGIN 在 END 缺）原被误判 legacy（绕过完整性流程且 status 报 integrity: ok 掩盖损坏）——`load_state` 细分为 legacy（完全无标记，维持原语义）与 corrupt（标记残缺/乱序）：status 报 `state: corrupt, integrity: violated`，变更类命令报新错误码 `state-corrupt`（hint 给出精确 END 行内容与恢复路径），`jump --fresh` 仍可恢复；engine-contract §10 状态枚举与 SKILL.md bootstrap 表补 corrupt 行。⑫CI contract-check.yml 只跑 --check 不跑测试套件（engine.py 回归对 CI 完全不可见）——补 unittest discover 步骤（纯 stdlib 零依赖）。新增 6 例测试锁定语义：skip 行恒胜 execute 行、正确顺序（先 report 后写行）、错误顺序必拒（invalid-transition）、截断与孤 END 标记判 corrupt、fresh 恢复 corrupt；测试 96 → 102 全绿，--check 零漂移。P3 观察项（planned_skip report 分支不可达、jumped 豁免未入契约、END 标记文档语法不符、CRLF 混行尾、terminology 陈旧计数等）记录在案暂不动；其中"Skip > Execute 优先级"与"jump 不绕过计划过滤"经考证系故意设计（实施期裁决③、契约 §5/§6），非缺陷不改。
>
> **主题："判断归 LLM，精确归工具，决定归人类"落地。** 本节是 Phase 3 的权威清单（已全部实施，见上方状态段）。
>
> 技术摸底依据（2026-09-14 完成）：v2.0 侧 `aidlc-orchestrate.ts`（8.6k 行，next/continue/report/park/team-board 五子命令）+ `aidlc-state.ts`（6.8k 行）；选阶段算法 = 全图线性扫描 + scope 网格过滤 + state 覆盖 + checkbox 跳过（`aidlc-lib.ts:21852`）；v2.0 状态文件也是 Markdown。分叉侧现状：契约除 `condition` 外全机器可读；`execution-plan.md` 无程序化消费者（路由靠模型记忆）；状态/审计由模型在 20+ 处散文约定中手维护；`gate` 的下一阶段名散落在阶段正文。
>
> v2.0 体量中确认不引入的子系统（砍的都是"服务能力不在分叉范围内"，非"移植不了"，可随时按 §6.5 的扩展路径加回）：steering token 续传、team/swarm、per-unit 波次、single、Kiro 遗留、compose 多意图、ownership env 门、传感器/证据链、park。

### 6.1 决策汇总

| # | 决策 | 结论 |
|---|---|---|
| D6（修订） | 引擎定位 | **必选运行时依赖**。启动探测失败（无 Python 3.8+）→ HARD STOP 提示安装，工作流不启动。原"可选增强层 + 双模镜像"立场废止（镜像成本会掐死演进：每个引擎功能要写两份文档） |
| D7 | 技术栈 | **Python 标准库**（与 generate.py 同栈，3.8+，零第三方依赖） |
| D9 | 契约消费 | **compile-to-JSON**：generate.py 编译 `scripts/data/stage-graph.json`；引擎只读 JSON，**永不解析 frontmatter，也永不解析 condition 散文** |
| D10 | 状态/审计归属 | **引擎原子写** Markdown 状态 + 审计转移条目；State Digest（sha256）+ 审计交叉核验，漂移即 halt + 人类确认重定基线 |
| D12 | 分发形态 | 引擎随技能分发（`scripts/` 下）；验收硬标准 = **裸项目**（只复制技能目录、无任何其他文件）dogfood 通过 |

### 6.2 三归理念 ↔ 机制映射（实施自查表）

| 理念 | 机制 | 诚实边界 |
|---|---|---|
| 精确归工具 | 引擎独占跨阶段路由、状态机、审计转移；compile-to-JSON 防漂移；完整性校验防手改 | — |
| 判断归 LLM | condition 散文不进引擎：CONDITIONAL 阶段照常发射并标 `conditional: true`，模型判断不适用则 `report --result skipped --reason`；scope 推荐、深度自适应、需求澄清全留模型 | — |
| 决定归人类 | 门内容/双选项/NO EMERGENT BEHAVIOR 不变；jump 是"改主意"的正规执行通道 | 无钩子环境下"模型伪造批准"工具层防不住（v2.0 在无钩子 harness 同局限）；靠提示词纪律 + 审计留痕 |

### 6.3 实施清单

**A. 契约编译层（generate.py 扩展）**

1. 新增编译渲染器，产出 `scripts/data/stage-graph.json`：有序阶段数组（slug/name/phase/execution/gate/for_each/workspace_writes/produces/consumes/requires_stage/scopes）+ scope registry（name/default/depth/keywords）+ `state_version`
2. `--check` 覆盖 JSON 漂移（frontmatter 改了未重编译 → 非零退出；现有 CI contract-check.yml 自动兜底，无需改）
3. 修正 stage-contract.md 两处散文：worked example 的 condition 折行写法（与解析器单行能力对齐）；文首 Runtime neutrality 段（"pure Markdown" 表述在 Phase 3 后失效，改为"单一运行时依赖 Python 3.8+"口径，与 §1 修订一致）
4. 契约 **frontmatter 字段集与取值约束**零改动（兑现 stage-contract §8 对 Phase 3 的承诺；A3 仅为散文修订，不触字段）

**B. 引擎本体（`scripts/engine.py`，单文件纯 stdlib，预估 1000–1500 行）**

5. 调用约定：`python <skill>/scripts/engine.py <subcommand> [--workspace <path>]`（workspace 默认取 CWD）；启动探测兼容 Windows `python` 与 Linux/macOS `python3`（探测序列两者都试）
6. `status`（只读）：双重职责——启动探测（python 可用 + 引擎完好）+ 会话恢复数据源；输出 `{engine, state: none|active|completed, current_stage, scope, depth, last_completed, ...}` JSON
7. `next`（纯只读路由）：线性扫描 + scope 过滤 + state 覆盖 + 勾选跳过；输出**单个** directive JSON（`run-stage` / `done` / `error`）；run-stage 含 stage/phase/gate/stage_file/produces/consumes/conditional/next_stage（**next_stage 是"假设本阶段 completed"的预测值，仅供呈现，不作为路由依据**）；error 字段契约 `{kind, code, message, hint}`（code 机器可读类别 / message 人类可读 / hint 补救提示）
8. `report`（唯一转移写入口）：`--stage <slug> --result <r> [--reason]`；原子写状态 + 追加审计转移条目。**转移语义矩阵**（E26 的测试基准）：

   | result | 勾选 | 指针 | 适用 |
   |---|---|---|---|
   | `completed` | `[x]` | 推进 | 非门阶段完成 |
   | `approved` | `[x]` | 推进 | 门阶段用户批准后 |
   | `rejected` | `[R]` | 停本阶段 | 门拒绝 |
   | `revised` | `[?]` | 停本阶段 | 修订后再提交 |
   | `skipped` | `[S]` | 推进 | 仅 CONDITIONAL 或计划 SKIP，须 `--reason` |

9. `jump --stage <slug>`（**独立子命令、写操作**；`next` 保持纯只读）：方向解析 + 指针移动 + 中间阶段重标 + `STAGE_JUMPED` 审计。**与完整性校验是阴阳配套**：校验堵死歪路，jump 敞开正门；缺它则每次正常改主意都会以"完整性告警"呈现。附带 Start Fresh（归档 aidlc-docs + 状态重置，resume 菜单执行层闭环；可独立为 `jump --fresh`，实现时定）
10. 状态完整性校验：写引擎辖区附 `State Digest`（sha256）；每次读先校验 + 审计交叉核验（勾选 vs 转移事件一致性）；漂移 → error directive + halt + 人类确认后重定基线。检测非阻止（无钩子收不走模型的 Write/Edit），威胁模型是"模型疏忽/偷懒"而非对抗。**digest 只覆盖引擎辖区**（见 B11），模型辖区不入摘要——其改动的合法来源是用户指令，由审计中的用户输入记录兜底
11. **状态文件分区所有权矩阵（设计项，实施的首件产出）**：

    | 状态文件的区 | 写入方 | digest 覆盖 |
    |---|---|---|
    | Stage Progress 勾选区、Current Status、State Digest、Unit Progress（预留） | **引擎独占** | ✅ |
    | Project Information、Workspace State、Code Location Rules、Extension Configuration、Autonomous Mode、Execution Plan Summary（含 Scope/Depth 与计划覆盖行） | 模型按模板写 | ❌ |

    WP 计划覆盖（Stages to Execute/Skip）由模型按结构化行格式写入 Execution Plan Summary，引擎读取消费（**收口"execution-plan.md 无消费者"**）；Scope/Depth 同理（模型写、引擎读，`next` 的 scope 过滤依赖它，为 load-bearing 通道）
12. 状态文件确定性创建（取代 workspace-detection Step 4 内联模板）：含 `State Version: 1`、`Engine` 字段
13. **单元清单结构化**：units-generation 把单元表（slug/名称/**依赖字段预留**/规模估计）以结构化形式落 state（模型辖区）；state schema 预留 `## Unit Progress` 区（引擎辖区，本阶段不启用，为 Phase 4 unit-major 留位）

**C. SKILL.md 引擎化改写**

14. 启动序列：跑 `engine.py status` 探测（`python`/`python3` 双命令名，见 B5）；失败 → HARD STOP + Python 3.8+ 安装提示
15. forwarding loop 入主循环：`next → 按 directive.kind 行动 → report → 重复`；directive 消费契约（error 原样呈现即停；不伪造 report；放弃 directive 直接丢弃不 report；**消费方忽略未知字段**——向后兼容条款，写进契约）
16. 阶段执行块瘦身：撤路由散文（"自动继续下一阶段"清单归引擎）；**保留** CONDITIONAL 的 Execute-IF/Skip-IF 判断散文与阶段内执行指引（判断归 LLM）
17. 所有权纪律：MUST NOT 手改引擎辖区（B11 矩阵左列）；模型辖区各区按模板正常维护；用户原始输入记录仍归模型（模型是唯一可见源）

**D. 关联规则文件同步**

18. workspace-detection：状态创建步骤改为引擎执行
19. workflow-planning：计划批准后由模型把覆盖决策按结构化行格式写入 state（引擎读取消费）
20. session-continuity：恢复菜单数据源改为 `status` 输出（呈现层保留 Markdown）
21. workflow-changes：收敛为"**判断在约定、执行在引擎**"——redo/跳步的执行一律走 jump，不再手工移指针
22. autonomous-mode 扩展：Review Stages 按显示名匹配 → 补 slug 对齐说明（消命名耦合风险；生成器 `_derive_name` 会剥离括号，显示名可能随 H1 变化）
23. **系统性收口**：grep 全 references/ 树中所有 `aidlc-state.md` 手写指令（12+ 处：全部 construction 阶段文件、application-design、user-stories、units-generation、requirements-analysis、workflow-conventions 扩展等），逐一改写为 report 调用或删除——否则模型同时收到"引擎独占写状态"与"Mark stage complete"两组矛盾指令，dogfood 必撞
24. **error-handling.md 恢复协议整体重定向**（独立工作量）：备份重建/reset/标 SKIPPED/标 incomplete/修正 current stage 等手改 state 路径，统一改为"完整性 halt → 人工确认 → 引擎重定基线"新流程
25. workflow-planning.md 的 `state-template-stages` GENERATED 生成区归宿：**删除**（含 generate.py MARKERS 注册清理）——引擎确定性创建 state 后，该"教模型手写 Stage Progress"的模板成为矛盾指令/死代码

**E. 测试与验证**

26. `scripts/tests/test_engine.py`（stdlib unittest）：路由（scope 过滤/覆盖/跳过/完成判定）、状态原子写、report 转移语义矩阵全分支（B8 表）、status 探测、摘要漂移 halt（含**模型辖区改动不触发 halt**的反例）、stage-graph.json 与 frontmatter 一致性
27. 既有 20 个 generate.py 测试零回归 + 二次运行幂等
28. **裸项目 dogfood（验收硬标准）**：只复制技能目录的新项目全工作流跑通；另测 brownfield、手改 state 触发 halt、中断恢复

**F. 文档回填**

29. integration-plan.md（本节定稿 + §7 排期 + §9 讨论记录）
30. AGENTS.md §3 护栏修订 + 路线图速览
31. README / README_cn：使用前提（Python 3.8+）与分发形态（自包含技能目录）

### 6.4 范围护栏（本阶段明确不做）

- steering token 续传、team/swarm、per-unit 引擎路由（per-unit 阶段 = 单次 run-stage 发射，单元内循环模型负责）、single、park、ownership env 门、多 intent
- condition 结构化、gate 第三选项契约化（留正文）
- 传感器、reviewer/persona/五层记忆（Phase 5+）

### 6.5 防返工设计备忘（扩展性五支点）

1. **compile-to-JSON 单数据源**：所有消费方从同一编译产物取数，新数据只编译一次
2. **dispatch 子命令结构**：新动词 = 新 handler + 一个 case，无侵入
3. **directive JSON 可扩展**：消费方忽略未知字段（向后兼容条款）
4. **State Version 迁移机制**：状态格式演进不伤旧档案
5. **契约 §5 预留命名空间**：reviewer/sensors/lead_agent 等字段语义已定义，启用 = 白名单放行

**三档重跑语义边界（勿混淆）**：redo（workflow-changes 决策协议 → jump 执行，回拨主指针）/ jump（移动指针的路由行为）/ single（脱钩主线、绝不动主指针、独立审计对，Phase 4）。

**error directive 是统一逃生舱**：任何新失败模式走"呈现并停止"，不发明新协议。

## 7. 后续 Phase 排期（2026-09-14 重排）

### Phase 4：Team Construction

**硬依赖链（顺序不可乱）**：单元清单结构化（Phase 3 ✓ 已排）→ unit-major → claim → merge。Team Construction 的每一步都以 unit-major 为前提：没有引擎感知单元就没有可认领的对象，没有 claim 锁多会话就是状态文件互踩。

1. **unit-major 波次编排**（地基，本身即可交付价值）：`report --unit`、Unit Progress 区启用、单元级审批门节奏（per-stage / unit-end 两种，借鉴 v2.0 `unit_gate_rhythm`）、单元级恢复。stage-major 保留为默认节奏（单单元/小项目无感）。**随此项一起做**（2026-09-15 dogfood 排期）：指令中的 `consumes` 条目增加计划感知标注（如 `producer_skipped: true`），把 stage-contract §2 "生产者被跳过则 moot" 的语义在指令层面显性化——引擎有了单元/计划感知后才有能力做这个标注，提前做只会返工
2. **claim/release + git worktree**（形态 A：多会话团队，harness 无关）：N 个 AI 会话（或人机混合）各自打开同一仓库，claim 粒度 = unit；所有协调逻辑在引擎，harness 只需能跑 shell。状态文件多会话并发写锁是实现期重点（参考 v2.0 mkdir 锁，Python stdlib 有对应做法）
3. **single 单阶段重跑**（~50–100 行）：`next/report --single`，独立审计对、绝不动主指针、stage_validity 警告不阻塞。用户场景：team 并行试验多个算法变体 → 选定其一单独重跑（试验-收敛闭环）
4. **swarm 进程内并行**（形态 B：harness 相关，依赖 subagent 能力，工作量最大，可再拆为独立子相位）

### Phase 5+：reviewer 及其他（逐项独立可交付，纯增量无返工，路径见 §6.5）

- reviewer 状态机（启用契约 §5 预留字段 reviewer/review_artifact/reviewer_max_iterations；READY/NOT-READY 回路由 report 分支承接）
- 传感器自检清单 → report 时阻塞校验（required-sections / upstream-coverage / traceability / claim-sources）
- persona 体系（轻量版 inline 扮演先行；完整版 14 agent + 知识库另议）
- 五层记忆（org→team→project→phase→stage）+ §13 学习仪式（引擎承担确定性去重写入）
- 门仪式精细化（HARD STOP、revision 逃生舱、non-matching reply 处理）
- 完成消息 5 段契约、声音/沉默规则、PRE-GENERATION SUMMARY STOP 强化
- **report+next 合并评估**（2026-09-15 dogfood 结论：不合并）：合并可省每次转移一次调用，但会破坏被两次守住的 CQS 边界（next 纯只读、report 单一写入口），引入"写成功但路由失败"混合错误域、rejected/revised 时返回冗余指令、对 APG-02 门挂起纪律形成"呈现即诱惑"。**仅当** Phase 4 多单元循环使转移次数成倍增长、编排开销成为真实痛点时再议，届时形态为 `report --and-next` opt-in 标志，默认行为保持纯粹

### 不排期（仅记录）

- **多 intent / compose**（D11）：一个版本就是一个产品意图；当前版本做到一半去做不相干的另一件事，应该是两个 git 版本的事。**重启前提**：与 Team Construction 协同设计——claim 注册表天然按 intent 隔离（v2.0 为 `claim/<intent-id8>/<unit>`）；`aidlc-docs/` 路径假设需加 intent 维度，属目录结构级重构，是所有后置项中侵入最深的

---

## 8. 关键参考文件索引

### v1.0 分叉（工作对象）
- `.agents/skills/aidlc-workflows/SKILL.md` — 主入口（620 行）
- `.agents/skills/aidlc-workflows/references/common/` — 12 个通用规则
- `.agents/skills/aidlc-workflows/references/{inception,construction,operations}/` — 14 个阶段规则
- `.agents/skills/aidlc-workflows/references/extensions/` — 6 个扩展（opt-in 机制）
- `.agents/skills/aidlc-workflows/scripts/` — generate.py（作者期生成器）；engine.py + data/stage-graph.json（Phase 3 交付的运行时引擎与编译产物）

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

---

## 9. 讨论与变更记录

### 2026-09-14：scope 淡化（已落地）+ 扩展配置成熟度重估（搁置）

**已落地 — scope 选择淡化（修改 Phase 2 交付的 RA Step 2.5 行为）**：
- 动机：对最终用户淡化 scope 概念，减少明显场景下的审批门（用户原话："明显是一个 bug，直接给 bugfix 就好；classic 既然知道太重，就不需要让用户选"）。
- 改动：`requirements-analysis.md` Step 2.5 第 4 条重写——无歧义（用户显式指定，或关键词唯一命中且无优先级冲突）→ **自动选定、不设门**，事后一句话告知并记录 state/audit；有歧义 → **最小候选**（1-2 个最可能的，永不展示完整目录，不列已知不合适的 scope）；Workflow Planning 门作为选错的安全网。`SKILL.md` scope 段落同步（"selected with the user" → 自动选定优先）。纯正文改动，`generate.py --check` 通过。
- 注意：本节修改了 §5 中"用户确认"的原始描述——Step 2.5 现行为以本节为准。

**搁置 — 扩展配置成熟度重估（待 Operations 阶段补全后再处理）**：
- 背景讨论：淡化 scope 后用户不会主动选 scope；scope 机制靠"默认 classic + 轻量信号触发"自动按请求分类（功能请求自动回落 classic，机制已保证）。但"产品从 MVP 转向企业级"的真正载体不是 scope，而是**项目级的扩展插件配置**（Security Baseline / Resiliency / PBT 强度）——它持久生效，却缺少重估触发时机（opt-in 问题挂在 RA 澄清问题文件里，需求太清晰时不生成文件就不会重问，存在盲区）。
- 已细化的方案要点（未实施）：
  1. **位置**：RA 新增 Step 5.2（扩展重估），Step 5.1 加交叉引用（已配置不重问，除非信号触发）。
  2. **触发信号**：M1 用户措辞含"上线/正式/生产/企业级/合规/付费/用户数据"（强）；M2 需求涉及敏感面（认证/支付/个人数据/外部集成）而 Security Baseline=No（强）；M3 迭代 ≥3 轮且从未重估（弱，仅提示）；M4 棕地代码规模增长（弱，仅提示）。强信号→必须重估；弱信号→完成消息里一句话提示。
  3. **关键不对称**：scope 可自动选定（选错可零成本纠正、不引入约束）；扩展**绝不自动开启**（开启即引入阻塞性约束，静默开启会让用户莫名被门拦）——重估只能"问"，且只问信号指向的 1-2 个扩展，一句话说清后果。
- **搁置原因（用户决定）**：Operations 阶段尚未补全，扩展配置的处理与 Operations 内容（部署/监控/生产就绪）强相关，待 Operations 补全后一并设计。届时回填本节为正式方案。

### 2026-09-14（其二）：Phase 3 方案定稿（D6 重大修订）

**过程**：先完成双侧技术摸底（v2.0 编排工具 8.6k 行 orchestrate + 6.8k 行 state 的机制拆解；分叉侧状态/路由/契约/解析器现状盘点），随后逐条审议了"相对 v2.0 砍掉清单"（steering 续传、team/swarm、per-unit 波次、single、Kiro 遗留、compose 多意图、ownership env 门、传感器/证据链、jump/resume 机器、park）——确认砍的都是"**它服务的能力不在分叉范围内**"，没有一项是"移植不了"，全部可按 §6.5 的扩展路径加回。**注**：其中 jump/resume 机器经裁剪后保留子集入 Phase 3（jump 独立子命令 + status 恢复探针），被砍的是 v2.0 的完整机制（aidlc-jump.ts 的 resolve/execute 分层、resume 菜单引擎内路由等）。

**关键决策与理由**：

- **D6 修订（引擎必选）**：用户定调——引入引擎的动机就是践行"判断归 LLM，精确归工具，决定归人类"；原"可选增强层"立场隐含的双模镜像成本（每个引擎功能都要写一份 Markdown 约定镜像）会掐死后续演进。分叉对 v2.0 的差异化定位随之明确为"**同等理念、更轻的可移植性**"（Python 3.8+ vs bun + opencode 钩子体系），而非"零依赖"。§1 硬约束同步修订。
- **三归理念可行性结论**：精确归工具 ✅（引擎接管路由/状态/审计）；判断归 LLM ✅（condition 散文永不进引擎，v2.0 同此分工）；决定归人类 ⚠️ 诚实边界——无钩子环境防不住模型伪造批准（v2.0 同局限），靠提示词纪律 + 审计留痕。
- **状态完整性校验入 Phase 3**：引擎必选使"只有引擎能写状态"从空强制变为可检测（State Digest + 审计交叉核验 + halt + 人工重定基线）。检测非阻止，威胁模型是模型疏忽而非对抗。
- **jump 入 Phase 3**：完整性校验堵死歪路后，jump 是"改主意"的正规执行通道，二者阴阳配套；拆开交付会让每次正常需求变更都以"完整性告警"形态呈现（体验裂缝）。
- **Team Construction 死结消解**：引擎必选使 claim 锁可行（原死结：引擎可选则锁不可靠）；拆为形态 A（多会话团队，harness 无关，优先）与形态 B（swarm 进程内并行，harness 相关，殿后）；unit-major 是其硬地基（claim 粒度 = unit）。
- **single 入 Phase 4**：用户场景——team 并行试验多算法变体后选定其一单独重跑（试验-收敛闭环）。
- **多 intent / compose 不排期**（D11）：用户原话"一个版本就应该是一个产品意图……那应该是两个 git 版本的事"。
- **分发自包含确认**：技能目录内对 AGENTS.md 零引用（已查证）；用户侧前提仅两条——harness 能加载技能 + 能执行 python。裸项目 dogfood 列为验收硬标准。

**审查修订（2026-09-14 其三，reviewer 审查后落地）**：🔴 D 组补系统性收口项（12+ 处手改 state 指令逐一改写，原清单仅覆盖 5 个文件）+ error-handling.md 恢复协议整体重定向为独立项；🔴 补状态文件分区所有权矩阵（B11：引擎辖区 digest 覆盖 / 模型辖区不入摘要）与 scope/计划覆盖的模型写-引擎读通道（原 report 无 payload 通道的空白改为混合所有权解法，report 不引入结构化参数）。🟡 jump 改独立子命令（保持 next 纯只读）；next_stage 标注为预测值；补 `--workspace` 调用约定与 python/python3 双命令名探测；补 report 转移语义矩阵（B8 表，E26 测试基准）；§9 砍单注明 jump/resume 裁剪口径；§3 路线图 Phase 0/1 行加历史时点标注；"契约零改动"限定为字段集零改动（A3 散文修订含 Runtime neutrality 段）；WP 的 state-template-stages 生成区定为删除（D25）。🔵 SKILL.md 行数勘误（556）；AGENTS.md §1 字段清单补 scopes；引擎体量预估上调至 1000–1500 行；error directive 字段契约（code/message/hint）写入 B7。清单总数 26 → 31。

### 2026-09-14（其四）：Phase 3 实施完成

按 §6 清单全部 31 项落地。分工：4 个 executor 并行（generate.py 编译层 + WP Step 8 重写 / 四规则文件引擎化 / state 指令收口 + error-handling 重定向 / SKILL.md + engine-contract.md），引擎本体（engine.py + test_engine.py）由主智能体亲自实现。实施期裁决记入 §6 状态段（①per-unit report 粒度、②rebase 后交叉核验豁免、③jump 不绕过路由过滤、④--workspace 位置、⑤错误 JSON 形态、⑥确认对象契约）。验收：77 个 unittest 全绿（生成器 30 + 引擎 47）、generate 幂等且 --check 零漂移、裸项目 dogfood 通过（greenfield 全流程 + brownfield scope 裁剪 + 篡改 halt/rebase + 中断恢复 + jump + --fresh）。Ex2b 发现并收口的清单外文件：reverse-engineering.md。遗留 backlog（Phase 4+ 评估）：scope depth enum 是否加 `adaptive`；welcome ASCII 截断保护；--check 重复 key 僵尸区逃逸场景；Operations 的 CONDITIONAL 语义。

**审查修复（2026-09-14 其五，reviewer 全面审查后落地）**：🔴 workflow-changes.md Type 5/9 把引擎消费的 Scope/Depth 通道错指到 `## Project Information`（引擎只读 `## Execution Plan Summary`）——改为指向正确位置并明示"engine consumes ONLY the Execution Plan Summary copies"；RA Step 2.5 同步改为直接填 Execution Plan Summary 的 Scope/Depth 占位行。🟡 argparse 用法错误与未捕获异常绕过"一律 error JSON"契约——新增 `_JsonArgumentParser`（error → JSON + exit 1）与 main() Exception 兜底（code: internal）；SKILL.md per-unit 阶段块缺"report 恰好一次"护栏——Per-Unit Loop 节加总注；workspace-detection Step 3/6 残留路由散文——Step 3 重构为纯 brownfield/RE 适用性判断、Step 6 改为 report completed + 引擎路由。🔵 B&T 完成消息的 Operations 预测改中性措辞；engine-contract §6 补 Skip>Execute 优先级与节标题严格性说明；死代码清理（EV_FRESH 投入 --fresh 归档审计使用、generate.py `regenerate(check)` 死参删除）；补 4 个测试（CRLF 摘要稳定性、argparse JSON、jump→已完成阶段、未知 scope 名），引擎测试 43→47。

**复审修复（2026-09-14 其六，二轮 reviewer 复审后落地）**：🔴-1 同源残留两处清除——SKILL.md State Ownership 条与 §6.3 B11 矩阵行的"Scope/Depth 属 Project Information"旧口径（改指 Execution Plan Summary）。卫生项：删除仓库根 dogfood 遗留垃圾目录（cmd 变量未展开产物）；AGENTS.md 测试数 73→77、§8 SKILL.md 行数 556→620 勘误。改进项落地：RA Step 2.5 代码块归属消歧（state 填写格式与 audit 记录分开表述）；5 个 construction per-unit note 的 "approval" 统一为 "gate outcome"（覆盖 skipped 收尾）；engine-contract 规则 4 措辞精确化（仅该行回落，Skip 行仍生效）；workspace-detection Step 5 完成消息的下一阶段预测改"Decided by the engine"；engine-contract §10 error 样例补尾注对齐实际输出；test_jump_fresh_archives 补 WORKFLOW_FRESH 断言。

### 2026-09-15：Phase 0/1/2 复审与修复

对 Phase 0/1（契约+生成器）与 Phase 2（scope 矩阵）做了一轮双路全面复审。总体结论：机制层零缺陷（契约 16 条校验规则全有实现、84 格 scope 矩阵逐格核对零误差、--check 零漂移、77 测试全绿），无 🔴 发现。落地的 5 项 🟡 修复：

1. **SKILL.md B&T 手写产物清单陈旧（5/8）**：改为指向阶段文件的指针，不再枚举文件名。
2. **依赖建模数据修正**：code-generation 的 `requires_stage` 补 `functional-design`、`nfr-design` 边；infrastructure-design 补 `functional-design` 边；5 处同类 consume（nfr-requirements/CG/infra-design 的 FD/*、CG 的 nfr-design/* 与 infra-design/*）`required: false → true`（对齐契约 §2 语义与 nfr-design 既有写法）。流程图/计划图新增 3 条边，经生成器落地。
3. **FD 前提条件随 scope 条件化**：nfr-requirements / infrastructure-design 的 "Functional Design must be complete" 前提与 Step 1 读取行补"计划无 FD 阶段时改从 requirements.md + RE 产物取数"的条件分支（security-patch/infra scope 下 FD 恒为 SKIP，原措辞每次运行必触发矛盾指令）。
4. **stage-contract §6.1/§6.3 同步 scope 淡化口径**：keywords 字段描述与选择流程改为"无歧义自动选定、不设门；真歧义才走最小候选聊天问题"，消除与 RA Step 2.5 现行行为的冲突。
5. **聊天豁免传播**：question-format-guide 总则/清单与 session-continuity 的"NEVER ask in chat"均补 RA Step 2.5 scope 选择问题的唯一豁免。

验证：generate.py 幂等且 --check 零漂移、无 advisory 告警，77 个 unittest 全绿。

复审遗留 backlog（未修，并入既有清单）：契约硬规则 1-8/10/12 与 advisory 13-15 缺单测；解析器未闭合引号静默通过；未注册文件中的 GENERATED 标记区逃逸 --check；workflow-changes Type 9 混淆 scope-SKIP 与 [S] 标记且决策树缺 Type 9 分支；隐式单单元前提注记遗漏 nfr-design/build-and-test；规则 16 的 for_each 豁免宽于约定覆盖面（Phase 4 扩 scope 前处理）；terminology Operations "Outputs" 与 process-overview "No fixed sequences" 陈旧散文；§4 状态段"13 个 GENERATED 标记区"计数口径与现树（17 个）不符，待下次修订校正。
