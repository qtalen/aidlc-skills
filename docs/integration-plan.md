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
| D13 | 动词三层纪律 + 注记转移不变律（2026-09-21 定，2026-09-22 实施）：引擎动词分三层——读（status/next，无副作用）；**转移（report/jump，封闭集合 = 唯二改变 marks/current 的动词，Phase 4/5 永不新增）**；生命周期（init/park/rebase；park 为注记子类）。注记动词必须保持 marks 与 current 不变（digest 重算不算转移）。Phase 4 的 claim/release 照此办理——实现为 report 的 additive guard，不新增转移动词。新动词入场券 = 与全部既有 mutating 动词的两两交互测试（交互矩阵自此为 CI 法定成本） |
| D14 | 传感器 fire 点与 finding 接口（2026-09-21 定，2026-09-22 实施）：分叉侧传感器的 fire 点 = 引擎动词（status=恢复时 / report=收单时），永久不变（harness 无关性使然，区别于 v2.0 的 write hook）。finding 对象五字段 `{type, severity, subject, message, action_discipline}` 即 Phase 5 传感器接口；Phase 3.1 交付的 artifact_alerts 为第一代实现（硬编码 manifest）。`type` 集合可增不可删；同一 state_version 内对象 shape 永不破坏性变更；Phase 5 manifest 化须过输出等价测试 |

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

### Phase 3.1：会话连续性增强（park + 恢复简报 + 传感器第一代）【✅ 已实施 2026-09-22】

**背景与根因**（真实用户反馈）：AIDLC 流程中途新建会话要求"从上次结束的地方继续"，发生**文件状态漂移**——旧制品加载不完整导致工作流偏移。路由未漂（引擎是路由 SSOT），漂的是执行层，三个断点（均已代码考证）：

1. **状态机粒度是阶段，中断发生在阶段内部**——`current_stage` 无法区分"未开始"与"中断"（`cmd_status` 无子阶段信息，engine.py:730-742；Unit Progress 预留未用，engine.py:407-408）；无收尾动词，中断不留痕（动词集仅 status/init/next/report/jump/rebase）。
2. **恢复协议是全量散文指令**——session-continuity.md:38-57 "MANDATORY Load Previous Stage Artifacts" 平铺无优先级无验证，"Load ALL" 物理不可执行 → 模型抽样 → 偏移；恢复协议不读审计尾部（audit.md 这个恢复数据源未被使用）。
3. **半成品无探测**——`report` 收单不验 produces；pending 阶段 workspace 产物已存在时引擎沉默。

**定位**：park 与证据链均为 Phase 3 砍单在案项（§9 2026-09-14 其二，砍单见本文件 :269/:358/:445——"服务的能力不在分叉范围内，可随时按 §6.5 加回"），本次凭真实用户反馈**有据加回最小子集**：park（v2.0 orchestrate 五子命令之一）+ 证据链子集（missing-produces 探测），以传感器形态实现。Trellis 对照调研（2026-09-21，见 §9 当日记录）验证了同款问题形态与解法方向。

**新决策（实施时录入 §1 决策表）**：

- **D13（动词三层纪律 + 注记转移不变律）**：引擎动词分三层——读（status/next，无副作用）；**转移（report/jump，封闭集合 = 唯二改变 marks/current 的动词，Phase 4/5 永不新增）**；生命周期（init/park/rebase；park 为注记子类）。"转移不变律"：注记动词必须保持 marks 与 current 不变（digest 重算不算转移）。Phase 4 的 claim/release 照此办理——实现为 report 的 additive guard（如 `report --unit` 校验 claim 归属），不新增转移动词。新动词入场券 = 与全部既有 mutating 动词的两两交互测试（交互矩阵自此为 CI 法定成本）。
- **D14（传感器 fire 点与 finding 接口）**：分叉侧传感器的 fire 点 = 引擎动词（status=恢复时 / report=收单时），永久不变（harness 无关性使然，区别于 v2.0 的 write hook）。finding 对象五字段 `{type, severity, subject, message, action_discipline}` 即 Phase 5 传感器接口；Phase 3.1 交付的 artifact_alerts 为第一代实现（硬编码 manifest），Phase 5 manifest 化时**须过输出等价测试**（固定夹具工作区，前后输出逐字节一致）。`type` 集合可增不可删；同一 state_version 内对象 shape 永不破坏性变更。

**实施规格**：

1. **`park` 动词**：`engine.py park --note "<断点描述>"`。门槛 `_load_active` + `_require_intact`；新增拒绝分支：工作流完成（current=None）→ 错误码 `workflow-complete`（文案对齐 jump 既有拒绝，engine.py:930-936 风格）。效果一：Current Status 区写 `- **Last Parked**: <slug> — <note>`（入 digest；marks/current 不动）。效果二：追加 `aidlc-docs/handoff.md`（懒创建、引擎独写、append-only、integrity 永不解析）——**审计分家**：park 不写 audit.md（转移账本天然有界，审计膨胀与 integrity 解析成本问题就此消解）。写序固定**先 region 后 handoff**（region 是权威源；崩溃窗口=handoff 缺一条历史，resume_note 不受影响）。去重：同 stage+同 note 与 handoff 尾条相同则跳过。note 卫生：必填、换行折叠 `; `、截断 300 字符。清除：`report`/`jump --stage`/`jump --fresh` 前置 `state.parked=None`（fresh 走初始模板天然无行）；`rebase` 保留可解析行。并发：last-writer-wins + handoff 双存，可接受；降级：旧引擎重渲静默丢弃该行、digest 自洽；`--fresh` 归档随 aidlc-docs 整目录——三者均记入契约 §5.5。
2. **region 与解析**：`_render_region_lines(..., parked)` 加参；`load_state` 解析 Last Parked 行 → `state.parked`；无该行 → parked=None → 重渲逐字节同旧格式；**STATE_VERSION 保持 1**。`_initial_state_text` 标记区外加两行读者须知（新会话先跑 status / 勿改标记区；仅覆盖新项目，入负债）。
3. **`status` 升级**（active 分支追加；none/legacy/corrupt 早退分支不携带新键，§10+golden 钉死；integrity=violated 时 alerts 照常计算输出）：
   - **audit 单次读**：`check_integrity` 增缺省参数 `audit_text=None`（缺省自读=现状；`_require_intact` 及 next/report/jump/park 零改动——改返回值方案已否决：`_require_intact` 对非 None 恒 raise，返回 tuple 会致全部 mutating 命令 TypeError）。cmd_status 单次读入，供 integrity / recent_events / 计数三方复用。
   - `resume_note`：`{stage, note}` 或 null（region 行权威）。
   - `recent_events`：最近 5 条转移事件（不含 park），元素 `{event, stage, reason, timestamp}`。**新增独立解析函数**：逻辑限定在 `## Engine Transition` 节内（防用户原始输入伪造 Event 行——SKILL.md:571 允许原文入账），与既有 `_audit_events` **共享模块级正则常量**（消双解析器漂移面），后者三元组签名不动（integrity 路径零改动，engine.py:507/511 两处解包不受波及）；时间戳归属"节内最后见到的 Timestamp 归该 Event"，模型条目夹心场景测试锁定。
   - `audit_entries` / `audit_bytes` 计数（单次读顺带，零成本；为审计分段 contingency 提供 512KB/50ms 触发器度量）。
   - **artifact_alerts（不对称语义——缺失断言零误报，存在信号低成本）**：
     - 通用排除：引擎自有文件 `aidlc-state.md` / `audit.md` 不参与任何检查（init 保证存在、零信号价值；WD 阶段因此自然豁免）。
     - **missing-produces**（completed `[x]` 阶段）：N = 非通配具体产物数（`{unit-name}`/`*` 跳过）；**N≥2 且全部缺失/为空才告警**（列出全部路径）；N=0/1 豁免。依据（一轮审查 🔴-1 + 二轮 🟡-A 考证）：RA questions 条件创建（requirements-analysis.md:174）、B&T 4/8 产物 As-Needed（build-and-test.md:192/252/256）、infra-design 唯一具体产物 shared-infrastructure.md 亦条件产物（infrastructure-design.md:89）、operations produces 为空、WD produces 恰为引擎文件——N=1 时"条件缺席"与"真没写"不可区分，语义鸿沟留待 gen-2 per-produce required。action_discipline: "Report to the user; do not regenerate or fabricate artifacts."（防 Goodhart：模型自作主张补制品）。
     - **resumed-artifacts**（current 阶段）：覆盖全部 produces 条目（引擎文件除外）；具体路径=退化 glob 精确存在；`{unit-name}` → `*` 翻译后 glob 展开；**任一匹配存在即告警**（封顶 5，message 注明可能是半成品）。存在信号=中断残留，误报代价低（"先读后写"恰为正确指引），且恰好覆盖 per-unit 阶段中断半成品（用户真实场景近邻）。action_discipline: "Read existing files before writing; append rather than regenerate (unless in a rejected/revised redo — see session-continuity)."
     - 整体 fail-open：探测异常 → `alerts_unavailable: true` + 空数组（不响亮但可见）；写动词照旧 fail-loud。
4. **`report` 软警告**：completed/approved 时对当前阶段按 N≥2 全缺规则检查 → 输出 `produces_missing: [...]`，**转移照常成功**；检查本身 try/except fail-open（异常省略字段——绝不阻断唯一写入口，否则重试撞 invalid-transition）；rejected/revised/skipped 不查。软警告跑一个 dogfood 周期再议升级硬错误。
5. **测试**（102 → 约 134）：ParkTests(~9：handoff 写入且 audit 零新增/digest 自洽/marks 不变/note 卫生/no-state 与 workflow-complete 拒绝/去重两分支/report 清除/**写序用 mock.patch 断言 `_write_text_atomic` 先于 `_append_text`**)；StatusRecoveryTests(~10：resume_note 有无/recent_events 5 条/时间戳夹心/**反误报六连**（RA-minimal 无 questions、B&T 缺 e2e、infra N=1 豁免、operations N=0 豁免、WD fresh-init 无 resumed、RA 单缺不告警）/**正例**（RA completed 双缺失告警、resumed glob 含磁盘 `auth[1]` 目录命中、current RA 半成品 requirements.md）/alerts_unavailable)；ReportWarningTests(2：字段出现且转移成功/fail-open 字段省略)；BackwardCompatTests(2：旧格式载入 parked=None、report 重渲逐字节回归)；InteractionMatrixTests(4：park×report、park×jump --stage、park×jump --fresh、park×rebase)；GoldenOutputTests(~4：形状对齐契约 §10，掩码=timestamp 键+ISO 值+workspace 路径占位)；CliTests(~2：park 缺 --note、usage 串与 docstring 动词列表含 park)。
6. **文档同步**（10 处）：engine-contract.md（§1 动词分类列全 8 个——**2026-09-22 审核更正：实际 7 个子命令，"8"系本规格笔误**、转移定义+不变律；:158 枚举补 park；新 §5.5 Park Semantics 含写序/并发/降级/--fresh 归档/引擎文件排除；§6 措辞"**引擎对** audit.md 的写入收窄为转移条目，模型侧用户输入记录与 CTX phase summary 不变"+Last Parked 行与 handoff.md 引擎独占；§9 表加 park；§10 样例含 status 新键形状/early-exit 无新键/violated 时 alerts 照常/park ack/workflow-complete 错误/produces_missing/finding 形状/alerts_unavailable）；session-continuity.md（恢复协议 v2：status→integrity→resume_note+recent_events→响应 alerts→分级阅读①引擎输出②required consumes③按需→增量续作含 rejected/revised 整体重写例外；Park Ritual 含 CTX-01 边界双写；反劝退条；Welcome Back 模板加 "Last parked: [stage] — [note]" 行；生成标记区保留为查阅地图）；checkpointing.md（CTX-02 改"分级阅读第 2 层插入 checkpoint 优先"+always-load 集加 resume_note/artifact_alerts；CTX-03 归属 phase summary 留 audit/park 记 handoff+补"模型侧读纪律不约束引擎全量读"；opt-in 文案补"断点与探测已默认，本扩展只管蒸馏与轻量加载"）；checkpointing.opt-in.md（Session Resumption Trigger 段改写，删 "full-artifact loading" 过期锚点）；error-handling.md（"Missing Artifacts During Resumption" **节头**定序交叉引用覆盖全节：传感器发现→报告用户→用户决定后才进入本节 jump→regenerate 路径）；SKILL.md（bootstrap active 行补 resume_note；Park 触发规则；:534/:554 枚举补 park；Directory 树加 handoff.md；**运行时缺失指引**：engine 调用报 Python 缺失特征（`'python' is not recognized` / `command not found` / `No module named`）时停止重试，向用户转达需 Python 3.8+（纯标准库、免 pip/venv）并给出平台安装命令——Windows `winget install Python.Python.3.12` 或 python.org 安装器、macOS `brew install python3` 或 `xcode-select --install`、Debian/Ubuntu `sudo apt install python3`——装好后重试；零代码，AI 即错误翻译层）；terminology.md（Park/Parked 词条）；AGENTS.md（§3.1 动词列表+park+handoff.md；实施后测试数 102→实际数）；README.md + README_cn.md（运行要求显式化：Python 3.8+ 纯标准库，缺失时附上述平台安装命令一行）；本文件（§1 决策表录 D13/D14；§9 记录实施结果）。
7. **顺序与验证**：engine.py（region→park/handoff→status→report→头部→CLI/docstring）→ 全部测试全绿 → `generate.py --check` 零漂移（本相位不触 frontmatter/生成物）→ 文档按第 6 条清单 → 终验（二次全绿幂等 + git diff 生成标记区零改动 + AGENTS.md 测试数更新 + CI 绿）。
8. **不做（八项）**：per-unit missing 精确覆盖（Phase 4 Unit Progress）｜report 硬阻断｜审计分段实现（contingency）｜CTX 转正（维持两层：默认层确定薄/增强层智能厚）｜missing-produces 自动补写｜handoff 模型直读 API（resume_note 是唯一通道）｜per-produce required 标记（gen-2）｜存量项目头部须知迁移。
9. **负债清单（七条，backlog）**：①N=1 具体产物阶段豁免 missing-produces（gen-2 per-produce required 可解）②per-unit missing 精确覆盖依赖 Phase 4 Unit Progress（`{unit-name}` 逐单元展开）③report 软警告待 dogfood 后议升级④状态文件头部读者须知仅覆盖新项目⑤审计分段 contingency（触发器 512KB 或解析 50ms，度量=新计数字段）⑥未 park 且当前阶段零制品的中断不可探测（park 是自律层非传感器）⑦handoff.md 无模型直读 API。

### Phase 3.2：Trellis 借鉴立即批（机制移植，零代码复制）【✅ 已完成 2026-09-22】

**来源**：Phase 3.1 立项同日的 Trellis 调研（§9 2026-09-21）产出四档借鉴清单（本体见本节第 9 条，随本节落盘）。Phase 3.2 承载①档全部 5 项 + ②档 2 项 + 落档编辑；经三轮独立 reviewer 审核（R1/R2 完成、R3 因服务中断放弃、R4 为新 reviewer 定义首跑），全部发现逐条考证属实后消解，本节为终版。审查过程与裁决见 §9 2026-09-22。

**实施状态（2026-09-22 开工，同日全部完成）**：

| 工作包 | 状态 |
|---|---|
| P0 四档清单落盘 | ✅ 已自解 |
| WP-7 落档（①登记表 ②5A/5B 拆写 ③本状态段） | ✅ 完成（②为 2026-09-22 立项时前移完成，开工核验无漂移） |
| WP-6 契约硬规则单测清零 | ✅ 完成（+25 测试：规则 1-8/10/12-15 全覆盖，含保留键 reviewer/sensors 夹具与规则 12 的 SKILL_ROOT patch 法；零契约-实现出入） |
| WP-1 Evidence-First 提问纪律 | ✅ 完成（指南顶部 Policy+豁免表、Recommendation+trade-off 两要素、排序纪律并入 Best Practices #3、6 处示例标注、9 文件 sweep 指针） |
| WP-3 DOC-06 导航索引 | ✅ 完成（advisory 定性、:21 例外条款、Overview 01~06、Enforcement 表补行） |
| WP-5 RE 可选产物 | ✅ 完成（无编号小节、source-backed、5A 种子定位、Step 10/12 同步） |
| WP-4 B&T 提交协议 | ✅ 完成（时序定死、六条内容、AUD-02 先例、AM-03 不自动 commit） |
| WP-2 dogfood 协议 | ✅ 完成（docs/dogfood-protocol.md 100 行，六度量+消融+模板，3.1 术语逐字对齐） |
| 收尾（登记表回填/测试数刷新/全量验证/一致性 sweep） | ✅ 完成（169 全绿 + --check 零漂移 + 全树无相抵指令） |

**0. 批次与前置**：Phase 3.1 → **Phase 3.2** → Phase 4 → 5A → 5B。串行理由（R2/R4 修正）：**仅 integration-plan.md 与 AGENTS.md 共享**（3.2 各内容 WP 不触 SKILL.md）。**前置 P0（半小时）**：四档清单本体已随本节落盘（P0 自解，R4-R1 阻塞项消解）。原则：frontmatter 零改动；generate.py --check 例行验证。

**1. WP-7 integration-plan 落档**（1h）——三件套：① §9 登记 Trellis 借鉴登记表（从本节第 9 条迁移，加"状态"列，先记"计划中"，收尾回填；④档 evidence-first 注明与 WP-1 非同一物：前者=扩展结构范式，后者=提问纪律）；② §7 Phase 5+ 拆写 5A/5B 并给完整映射表——**已前移至 2026-09-22 落档时完成**（5A/5B 两节 + 映射注 + Phase 4 Trellis 设计输入清单 6 项挂 Phase 4 节末 + ④档三项入不排期，执行期仅核对无漂移）；③ 新增 §7 Phase 3.2 实施状态段。

**2. WP-1 Evidence-First 提问纪律**（~120 行，1.5-2h）：
- a. question-format-guide.md 顶部新增 **Evidence-First Policy**，含优先级条款（探索优先覆盖各阶段 "when in doubt, ask" 类指令——overconfidence=不查就假设）与豁免表：可由代码库/制品探索回答的问题必须由探索解决（引用来源），不进问题文件。**豁免**：RA Step 2.5 scope 聊天问题（既有唯一聊天豁免）；**扩展 opt-in 问题**（RA Step 5.1 MANDATORY 项，天然非探索可解，R4 新增豁免）
- b. Multiple Choice Guidelines 补两要素：**when a recommendation exists** 时必含 Recommendation（含一句话理由）+ "If you choose otherwise" trade-off 行（对齐 QT-01 条件口径，同步 QT-01 映射说明）
- c. 排序纪律与既有 Best Practices #3（one topic）合并表述
- d. **系统性收口 sweep（D23 先例通用化）**：8 个产问题的阶段文件（RA/user-stories/application-design/units-generation/functional-design/nfr-requirements/nfr-design/infrastructure-design）各加 1 行指针；overconfidence-prevention.md 的 "Default to Asking" 处加同款指针
- e. 自洽修复：指南示例（:78/:133/:151/:308/:322 等非三类问题——数据库选型/部署目标/架构模式）改写或标注；Question Structure 模板与 Summary 清单同步两要素
- 验收：**全树 grep 无相抵指令**

**3. WP-3 DOC-06 导航索引（advisory）**（~30 行，0.5h）：workflow-conventions.md Group 1 新增 DOC-06——≥300 整行的 aidlc-docs **内容制品**（创建或实质更新）须顶部维护"任务→章节"导航表，覆盖全部 H2（可机械核对）。**排除**：audit.md（append-only 互斥）、aidlc-state.md/handoff.md（引擎独占）、checkpoints（≤200 行上限）、问题文件（QT/DOC-04 辖区）。声明为该文件**首条 advisory 规则**（:21 措辞修正 + Blocking 行为节注明 advisory=列出不阻断；理由：缺失无危害，blocking 训练用户无视 findings）。同步：Overview 行 DOC-01~05→01~06；Enforcement Integration 表补收窄语境行。

**4. WP-5 RE 可选产物**（~30 行，0.5h）：reverse-engineering.md Step 9 与 Step 10 之间新增**无编号小节** "Optional Artifact: Working Conventions"（禁重编号，:302 有步号自引用）。落点 `aidlc-docs/inception/reverse-engineering/working-conventions.md`——**位于既有通配 produce `inception/reverse-engineering/*` 内，自动进入会话加载清单与 3.1 resumed-artifacts 探测，无需 frontmatter 改动**（删 promote 说法；是否单列留 gen-2 per-produce 决策，入负债）。内容纪律：source-backed（每条约定带来源路径引用，拒绝空话）；**定位为 Phase 5A 知识树的种子/导入源**（防两套约定存储分叉，R4-B3 新增）。同步：Step 10 时间戳/产物清单提及；Step 12 完成消息列出。

**5. WP-4 B&T 提交协议**（~50 行，1h）：build-and-test.md **Step 9 内**新增 "### Commit Protocol"，**时序定死**：门批准 → `report approved` → 完成消息正文呈现 commit 计划（APG-05 允许）→ Approve & Continue 语义含"执行 commit 计划"（**2026-09-22 审核更正**：原文顺序可歧读为"批准后才呈现计划"；实施定序为"完成消息含计划先呈现 → Approve & Continue 即阶段批准+执行授权 → `report approved` → 执行"，见 build-and-test.md Commit Protocol 与 §9 实施后审核段）；拒绝 → Request Changes / 手动路径。内容：①脏文件二分，判定依据=**本会话工具调用实际写过的路径**，其余一律二类列出、绝不静默暂存；②一次性展示 commit 计划（含阶段与单元）；③禁 amend、禁 push（用户显式要求除外）；④**非 git 工作区**：对齐 AUD-02 先例（no git → 标注 unknown，不阻塞，跳过协议，R4 新增）；⑤commit 计划与确认结果入 audit，hash 记入 build-and-test-summary.md；⑥顺序：工作成果 → **若存在**归档/handoff 待提交项则其后（条件式，B&T 时点二者常不存在）。**AM-03 自主模式**：不自动 commit，完成消息列出待提交清单。前置核查存档：全库 grep 结论（仅 AUD-02 git config 与 security-baseline lock-file 提法，无冲突）。

**6. WP-2 dogfood 协议**（新文件 docs/dogfood-protocol.md，中文，~120 行，1.5h）：六条度量——①重复解释次数→audit 条目趋势 ②PRD 范围清晰度→**定性项**（观测边界/非目标声明表述，不新增 RA 模板节）③重复评审→rejected/revised 趋势 ④换工具稳定→引擎 JSON 一致性 ⑤新人首任务独立完成→定性 ⑥RCA bug 沉淀率→5A 后生效。消融对照=**历史对照**（Phase 3 前后 dogfood 记录）+ **引擎内开关对照**（park/软警告 on-off）；显式注明"无引擎臂在当前契约下不可构造"（D6 HARD STOP + Only-next-routes）。数据源=audit trail + 3.1 的 audit_entries/audit_bytes；一次一表记录模板。定位：**服务 3.1 落地后的首个 dogfood 周期**（含 3.1 遗留的"软警告待 dogfood 后议升级"决策回填）。

**7. WP-6 契约硬规则单测清零**（~300-400 行，4-6h）：映射表**以模块 docstring 固化**在 test_generate.py；表首行注明规则 9/11/16 已覆盖（test_generate.py:251/:264/:278）。实施时核对规则 1 与 12 是否真无夹具（12 需临时技能树或 SKILL_ROOT override，方法记入映射表）；补 **reserved 键（reviewer）夹具**锁定契约 §5 预留命名空间。收尾：AGENTS.md 测试数 102→实际数刷新。

**8. Phase 5A 骨架（WP-7 落档，不实施）**：位置 `aidlc-docs/knowledge/<domain>/index.md`（index 只路由）；条目 frontmatter 预留 `governs:`（条目级无碍；未来用于阶段 frontmatter 须走契约 §5 保留命名空间）。机制定性：**按需加载的复盘约定条款**，复用两态扩展体系（opt-in 存根 + 常载规则），非新加载机制。写入仪式双触发：B&T 收尾自问 + 复盘触发器——判定者=**模型**、计数窗口=**同单元连续失败**、跨会话以 handoff/audit note **best-effort** 续（引擎计数属引擎改动，须付 D13 交互矩阵成本）。内容纪律：可执行契约模板（签名/边界行为/错误矩阵/来源引用）；"分析留在聊天里=零"；超阈值拆分。学习双出口：约定→知识树条目 or→传感器提案（D14 finding 形态）。知识源关系：**RE working-conventions.md = 知识树初始种子/导入源**（唯一"约定"存储为知识树）；空树期 knowledge_refs 回退引用它与既有规则文件。悬空依赖显式化：knowledge_refs 完整设计见 docs/result-oriented-delegation-design.md（待 WP-7 第 6 项处理）。排期：Phase 4 后、5B 前。

**9. 四档清单本体**（已迁入 §9 登记表并加状态列；本表为规格存档，以 §9 为准）：

| 档 | 项 | 去向 |
|---|---|---|
| ①立即（5） | brainstorm 三纪律 / 成功度量清单 / 消融对照 / 长制品导航索引 / 批量提交协议 | WP-1 / WP-2 / WP-2 / WP-3 / WP-4 |
| ②排期（3） | 单层活知识树闭环 / spec 冷启动 / 契约硬规则单测清零 | 5A 立项（WP-7 落档骨架）/ WP-5（RE 可选产物为先行）/ WP-6 |
| ③相位触发（8） | 策展清单 / 派遣三件套 / channel 对照 / 单元依赖显式化 / spec 移植 / knowledge_refs 字段 / 学习双出口 / 任务信封设计稿处理 | Phase 4 设计输入（WP-7 清单 6 项）/ Phase 5 |
| ④仅记录（3） | 技能版本戳 / 模板升级保护 / evidence-first 扩展范式（≠WP-1 提问纪律） | 技能分发/升级阶段再议 |

**10. 顺序与验收**：**前置 P0（已自解）→ WP-7 → WP-6 → WP-1 → WP-3 → WP-5 → WP-4 → WP-2 → 收尾**（登记表状态回填 + AGENTS.md 测试数 + 全量 unittest + generate.py --check + 散文一致性 sweep）。总验收：测试全绿（102 + 3.1 新增 + WP-6 新增）、--check 零漂移、全树无相抵指令、dogfood-protocol 与 3.1 数据源对齐且服务其首个 dogfood 周期。总工时 **~10-12h**（WP-7 因②前移缩至 1h；WP-7 前置锁定全部裁决与清单；WP-6 前置去风险——最大最易超时项压尾会拖垮总验收；WP-4 交叉契约面最大放后吸收结论；WP-2 纯文档殿后备用）。

**11. 不做（十项）**：per-unit missing 精确覆盖（Phase 4）｜report 硬阻断｜审计分段实现｜CTX 转正｜missing-produces 自动补写｜handoff 模型直读｜per-produce required 标记（gen-2）｜存量项目头部须知迁移｜**SKILL.md 问答概述指针（可选镀金）**｜**RA 模板加 out-of-scope 节（度量 2 已降定性）**。

**12. 负债清单（并入本节 backlog，WP-7 执行时挂 §9）**：WP-5 通配单列 per-produce 决策（gen-2）/ 5A 触发器跨会话计数 best-effort / WP-4 二分语义随 Phase 4 claim/merge 重审 / 登记表漂移风险（收尾回填对冲）/ 消融无引擎臂违宪（永久，除非契约变更）/ 四档清单状态列初始为"计划中"待收尾刷新。

### Phase 4：Team Construction

**硬依赖链（顺序不可乱）**：单元清单结构化（Phase 3 ✓ 已排）→ unit-major → claim → merge。Team Construction 的每一步都以 unit-major 为前提：没有引擎感知单元就没有可认领的对象，没有 claim 锁多会话就是状态文件互踩。

1. **unit-major 波次编排**（地基，本身即可交付价值）：`report --unit`、Unit Progress 区启用、单元级审批门节奏（per-stage / unit-end 两种，借鉴 v2.0 `unit_gate_rhythm`）、单元级恢复。stage-major 保留为默认节奏（单单元/小项目无感）。**随此项一起做**（2026-09-15 dogfood 排期）：指令中的 `consumes` 条目增加计划感知标注（如 `producer_skipped: true`），把 stage-contract §2 "生产者被跳过则 moot" 的语义在指令层面显性化——引擎有了单元/计划感知后才有能力做这个标注，提前做只会返工
2. **claim/release + git worktree**（形态 A：多会话团队，harness 无关）：N 个 AI 会话（或人机混合）各自打开同一仓库，claim 粒度 = unit；所有协调逻辑在引擎，harness 只需能跑 shell。状态文件多会话并发写锁是实现期重点（参考 v2.0 mkdir 锁，Python stdlib 有对应做法）。**Trellis 前车之鉴（2026-09-21 调研）**：其曾实现后又删除 worktree 管理（复杂度收益比不佳）——引入 worktree 前先评估，能靠 claim 锁 + 目录约定解决就不上
3. **single 单阶段重跑**（~50–100 行）：`next/report --single`，独立审计对、绝不动主指针、stage_validity 警告不阻塞。用户场景：team 并行试验多个算法变体 → 选定其一单独重跑（试验-收敛闭环）
4. **swarm 进程内并行**（形态 B：harness 相关，依赖 subagent 能力，工作量最大，可再拆为独立子相位）

**Trellis 设计输入（2026-09-22，源自 §7 Phase 3.2 四档清单③档，进入本相位设计时逐项核对）**：① 上下文策展清单——派遣给 worker 的文件清单须 `{file, reason}` 二元组 + 字节预算 + 禁预注册代码文件（worker 应自己改动代码，派遣方只给规格）；② 派遣三件套——Active task 首行约束 + 递归守卫（子会话禁再派遣）+ 任务注入标记-or-回拉双通道；③ channel 事件日志 vs claim 注册表对照——协调状态放文件而非聊天流（channel 可丢、注册表可审计），与上面 claim/release 设计合并评估；④ 单元依赖显式写在工件（units.md 依赖列），而非图暗示；⑤ spec 移植模式——上游规格可整体移植进单元工件。

### Phase 5A：单层活知识树与学习闭环（Trellis ②档"单层活树闭环"立项；Phase 4 后、5B 前；完整骨架见 §7 Phase 3.2 第 8 条）

- 知识树：`aidlc-docs/knowledge/<domain>/index.md`（index 只路由不存内容）；条目 frontmatter 预留 `governs:`（条目级无碍；未来用于阶段 frontmatter 须走契约 §5 保留命名空间流程）
- 写入仪式双触发（B&T 收尾自问 + 复盘触发器——模型判定、同单元连续失败计数窗口、跨会话以 handoff/audit note best-effort 续）+ 学习双出口（约定→知识树条目 or→传感器提案[D14 finding 形态]）
- knowledge_refs（③档）：按 `task`/阶段声明需要加载的知识引用；完整设计见 `docs/result-oriented-delegation-design.md`（现为"讨论记录待并入"状态，Phase 4 设计输入第 6 项处理并入/延后）；空树期回退引用 RE working-conventions（WP-5 交付）与既有规则文件
- 种子关系：RE working-conventions.md = 知识树初始种子/导入源，唯一"约定"存储为知识树（防两套分叉，R4 裁决）

### Phase 5B：reviewer 及其他（逐项独立可交付，纯增量无返工，路径见 §6.5）

- reviewer 状态机（启用契约 §5 预留字段 reviewer/review_artifact/reviewer_max_iterations；READY/NOT-READY 回路由 report 分支承接）
- 传感器自检清单 → report 时阻塞校验（required-sections / upstream-coverage / traceability / claim-sources）。**注（2026-09-21）**：fire 点与 finding 接口已由 Phase 3.1 的 D14 预定——fire 点 = 引擎动词（status/report，harness 无关性决定，区别于 v2.0 的 write hook），finding 五字段形状见 §7 Phase 3.1；Phase 3.1 交付的 artifact_alerts 即传感器第一代，manifest 化时须过输出等价测试
- persona 体系（轻量版 inline 扮演先行；完整版 14 agent + 知识库另议）
- 五层记忆（org→team→project→phase→stage）+ §13 学习仪式（引擎承担确定性去重写入）；与 5A 关系——5A 先交付项目级单层闭环，五层记忆届时复用其条目模板与写入仪式做跨层扩展
- 门仪式精细化（HARD STOP、revision 逃生舱、non-matching reply 处理）
- 完成消息 5 段契约、声音/沉默规则、PRE-GENERATION SUMMARY STOP 强化
- **report+next 合并评估**（2026-09-15 dogfood 结论：不合并）：合并可省每次转移一次调用，但会破坏被两次守住的 CQS 边界（next 纯只读、report 单一写入口），引入"写成功但路由失败"混合错误域、rejected/revised 时返回冗余指令、对 APG-02 门挂起纪律形成"呈现即诱惑"。**仅当** Phase 4 多单元循环使转移次数成倍增长、编排开销成为真实痛点时再议，届时形态为 `report --and-next` opt-in 标志，默认行为保持纯粹

**Trellis 借鉴映射注（2026-09-22）**：③档 8 项——5 项入 Phase 4 设计输入（见 Phase 4 节末），knowledge_refs 字段与学习双出口入 5A，任务信封设计稿处理挂 Phase 4 输入第 6 项；②档"活树闭环"即 5A 立项本体（spec 冷启动先行已由 Phase 3.2 WP-5 承载）；5B 各项无 Trellis 来源，为原有 backlog 原位保留。④档 3 项见"不排期（仅记录）"。

### 不排期（仅记录）

- **多 intent / compose**（D11）：一个版本就是一个产品意图；当前版本做到一半去做不相干的另一件事，应该是两个 git 版本的事。**重启前提**：与 Team Construction 协同设计——claim 注册表天然按 intent 隔离（v2.0 为 `claim/<intent-id8>/<unit>`）；`aidlc-docs/` 路径假设需加 intent 维度，属目录结构级重构，是所有后置项中侵入最深的
- **Trellis ④档三项**（2026-09-22 记录，触发条件出现再议）：**技能版本戳**（技能分发/多版本共存场景——SKILL.md 元数据声明版本，消费方可探测兼容性）；**模板升级保护**（用户本地定制模板与上游技能升级冲突场景——生成物标记区机制推广到用户模板）；**evidence-first 扩展范式**（将 WP-1 的 evidence-first 纪律推广为扩展作者的结构性模板：最小证据→定位瓶颈→分支→再测量；≠WP-1 提问纪律，二者同名不同物）

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

### 2026-09-21：跨会话文件状态漂移——诊断、Trellis 对照、两轮审查与 Phase 3.1 立项

**触发**：真实用户反馈两条——①长会话中开头读过的规则/spec 遗忘导致执行偏移；②流程中途新建会话要求"从上次结束的地方继续"后仍发生文件状态漂移（旧制品加载不完整、工作流偏移）。

**根因诊断**（全部代码考证）：路由层未漂（引擎是路由 SSOT），漂在执行层——①状态机粒度是阶段而中断发生在阶段内部，引擎对阶段内进度失明且中断不留痕；②恢复协议是"MANDATORY Load ALL"全量散文指令，无优先级无验证，且不读审计尾部；③report 收单不验 produces、半成品无探测。详见 §7 Phase 3.1 背景节。

**Trellis 对照调研**（外部工作流框架，docs.trytrellis.app + 本地仓库全量考察）：同一哲学（"判断归 LLM、精确归工具、决定归人类"）的正交投影——我们把确定性押在阶段路由（契约+引擎），它押在状态保活与知识复利（per-turn breadcrumb 注入 + 活 spec 回写闭环）。对本次立项的直接馈赠：①park 是其 task.py 生命周期事件的成熟先例（"生命周期事件 ≠ 状态转移"）；②"必需步骤必须出现在模型必经通道"不变量；③"分析留在聊天里=零"的落盘纪律；④其自身删掉 worktree 管理的历史警示已并入 Phase 4 前置检查意识。其他可借鉴项（knowledge_refs 三代演进、反劝退表、成功度量清单等）记录于当日会话，供后续相位取用。

**方案演进与两轮审查**（全部发现均经逐条考证属实后消解）：

- 一轮（reviewer）：1🔴（传感器 produces 检查语义与 frontmatter 数据现实冲突——RA/B&T 条件产物、`{unit-name}` 占位）+ 6🟡（尾部读冗余、`_audit_events` 改元组砸 integrity、audit 收窄措辞冲突、D13 分类漏 init/rebase、三规格空洞、文档漏三处）+ 8🔵。裁决核心：缺失检查与存在检查采用**不对称语义**。
- 二轮（reviewer）：3🟡（①infra-design 唯一具体产物亦为条件产物+operations 空产物 → 定 **N≥2 且全缺才告警**通用规则，弃硬编码豁免表；②resumed 检查条目参与范围 → 定**全产物参与唯排除引擎自有文件**；③单次读实现二选一 → 写死**可选参数方案**，改返回值会致 `_require_intact` 对非 None 恒 raise、全部 mutating 命令 TypeError）+ 8🔵 + 4 建议（共享正则常量、新解析器限定 Engine Transition 节、violated 时 alerts 照常、terminology 词条），全部采纳。
- 副作用治理（讨论定案）：审计膨胀→**账本分家**（park 记 handoff.md，audit.md 只收转移，天然有界；审计分段降级为 contingency，触发器 512KB/50ms）；Goodhart（告警变任务）→action_discipline 字段禁自行补写；fail-open 不可见→alerts_unavailable 标记；引擎角色扩张→D13/D14 把 ad-hoc 实现定性为"传感器第一代"而非透支（换心脏不换接口）。
- **既有 CTX checkpointing 扩展（opt-in）与新方案互补而非重复**：边界重压缩归 CTX-01 检查点、任意断点轻记号归 park、确定性探测与路由归引擎；CTX 三处修订并入实施清单（CTX-02 措辞对齐分级阅读、CTX-01×park 边界双写、CTX-03 归属澄清）。

**产出**：Phase 3.1 完整实施计划（§7，已裁决待实施）；D13/D14 待实施时录入 §1 决策表。park/证据链属"有据加回"（砍单见 :269/:358/:445）。测试 102 → 约 134。

### 2026-09-22：Trellis 借鉴综合、Phase 3.2 三轮独立审核与终版立项

**过程**：①对 Trellis 文档库与技能市场做补充调研（spec 冷启动/活树模板/真实案例/evidence-first 领域技能范式），与既有调研合并产出**四档借鉴清单**（①立即 5 项/②排期 3 项/③相位触发 8 项/④仅记录 3 项）——清单本体已随 §7 Phase 3.2 第 9 条落盘，取代 2026-09-21 条目中"记录于当日会话"的临时状态。②据清单起草 Phase 3.2 实施计划（7 个工作包 + Phase 5A 骨架），经三轮独立 reviewer 审核。

**三轮审核（模型各异，全部发现经主智能体逐条考证属实后消解）**：
- **R1**（引导性提示词）：1🔴（WP-1 三类白名单与阶段文件 MUST 指令冲突）+ 6🟡 + 8🔵。微观精确度高（指南自带示例自相矛盾、QT-01 条件口径、步号自引用、规则 9/11/16 已覆盖的测试名证据）。
- **R2**（中性提示词，换模型）：1🔴 + 7🟡 + 4🔵 + 6 建议。系统思维最强——独有发现：四档清单无源、**消融臂违宪**（D6 + Only-next-routes 使无引擎对照契约性不可行）、AM-03 阻塞、扩展"第三态"无先例、串行理由失实（3.2 实不触 SKILL.md）。
- **R3**：因 opencode 服务中断两次未完成，放弃。
- **R4**（新 reviewer 定义首跑）：1🔴 + 7🟡 + 6🔵。首次出现"核对通过项"正向确认节与显式不可核验范围声明；独有发现：knowledge_refs 依赖悬空（指向"讨论记录待并入"的 result-oriented-delegation-design.md）、扩展 opt-in 豁免缺失、知识树×working-conventions 两套存储风险；但未达 R2 的消融违宪深度。**方法学副产物**：比较两轮完成的审核确认中性提示词优于引导性提示词（R2 在无预埋条件下覆盖 R1 全部发现且增量更重），据此修订了 reviewer/architect/executor 三个子代理定义与全局 AGENTS.md 委派纪律（反锚定协议+待验证主张+路径委派；属 opencode 全局配置，非本仓库变更，特此记录以解释后续审核行为的变化）。

**合并裁决要点**：Evidence-First Policy 含优先级条款与扩展豁免 + 8 文件 sweep（D23 通用化）；DOC-06 首条 advisory + 排除表；WP-5 通 produces 自动覆盖（删 promote）；WP-4 时序定死（门批准→report→commit 计划入完成消息）+ AM-03 不自动 commit + 非 git 回退；WP-2 度量 2 降定性 + 消融改历史/开关对照；5A 定性为按需加载约定条款（复用两态）；WP-7 扩三件套 + Phase 4 设计输入 6 项（新增任务信封设计稿处理）。

**产出**：§7 Phase 3.2 终版（已裁决待实施，前置 P0 已自解）；同日完成 WP-7-② 前移——Phase 5+ 拆写为 5A（知识树与学习闭环）/5B（reviewer 及其他）+ 映射注、Phase 4 节末挂 Trellis 设计输入 6 项、④档三项入不排期（回应"去向列悬空"缺口：四档清单的路由在 §7 各节全部落地）。工时 ~10-12h（WP-7 因前移缩至 1h），顺序 P0→WP-7→6→1→3→5→4→2→收尾。

**追加（同日晚，运行时可移植性讨论）**：担心部分用户环境无 Python，评估"脚本全量改写 Node"方案后**搁置**——macOS/Linux 默认自带 python3 不带 node（缺口互换不缩小）、Node LTS 版本窗远窄于 Python 3.8+、102 测试资产与 Phase 3 验收清零、且"真实用户被阻断"触发器未响。裁决：**D6 不变**，仅向 Phase 3.1 文档同步追加零代码兜底（第 6 条 9→10 处：SKILL.md 错误翻译规则 + README 双语运行要求一行，~半小时）。若未来触发条件出现，正确路径是"先导出语言无关一致性测试向量，再单语言整体替换"，不做双实现并存。

### 2026-09-22（晚）：Phase 3.1 实施完成

**过程**：主智能体实施引擎核心（engine.py 11 处耦合编辑：常量/正则 → State.parked 与 region 渲染/解析 → 审计双解析器 → check_integrity audit_text 复用 → 传感器三函数 → cmd_status 六新键 → cmd_report 软警告+清除 → cmd_park 全套 → CLI/docstring），冒烟验证后按"可分离工作分发 executor"原则四批并行：①测试套件（39 个新测试七类）②engine-contract.md（§1 动词三层/§5.5 Park Semantics/§6 收窄措辞/§9 表/§10 样例）③session-continuity.md v2（分级阅读取代 Load ALL/Park Ritual/反劝退条）+ checkpointing×2 ④SKILL.md/terminology/error-handling/AGENTS.md/README×2（含运行时缺失指引）。全部经主智能体复核（141 测试全绿 + --check 零漂移 + 载荷文档抽读）。

**结果对照计划**：测试 102 → **141**（计划"约 134"，超额因反误报正例细化）；文档同步 10 处全落（含当日新增的第 10 处 README×2）；D13/D14 已录入 §1 决策表；软警告/传感器 fail-open/审计分家（park 不入 audit）/写序 region→handoff/去重/清除矩阵全部按规格实现。executor 上报一处自主判断：engine-contract 中 audit 分段触发度量只写 512KB 未写"50ms"（本地无可考证实现，50ms 属计划负债⑤的解析耗时阈值构想，留待 contingency 实施时定）。

**验证**：`python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests` → Ran 141 tests OK；`python .agents\skills\aidlc-workflows\scripts\generate.py --check` → 零漂移；既有 102 测试零回归。

**负债确认（七条不变）+ 新增一条**：⑧测试套件新增 `_run_main`/`make_doc`/`route_to` 等辅助（后续阶段测试可复用，但 route_to 依赖 plan-skip 语义，Phase 4 unit-major 时需复查）。

### 2026-09-22（续）：Phase 3.1 实施后全量审核与修复

**审核**（reviewer 子代理，静态全量对照 §7 规格 1-9 条）：🔴 阻断 0；🟡 应修 3（①session-continuity 分级阅读第 2 层"required consumes"与生成地图同位语语义冲突——地图列的是各阶段自身 produces 而非 consumes；②workflow-changes.md §6 On Resume 残留"Read all artifacts from completed stages"全量加载旧指令（规格 10 处同步清单的漏网文件，本相位引入分级阅读后成为相抵指令）；③"WD fresh-init 无 resumed"反误报场景无测试承载、且 test_no_alert_for_zero_produce_stage 的 engine-files 断言为空覆盖）；🔵 建议 4（动词计数 8→7、早退分支 hint 措辞、AGENTS.md "D1-D12" 过期、none/legacy 键集未钉死+截断仅断言 ack）。三个待验证主张裁决：A 部分证实（反误报覆盖确有空档，但写序 mock/金样两类强度充分）；B 证伪（当前 produces 无 `[`/`?` 条目，无现行缺陷；未来 frontmatter 引入时需 glob.escape——记入负债⑨）；C 证实且合理（50ms 属计划构想、仓库无实现可考，不写入契约正确）。

**修复**（全部落）：①tier 2 措辞改为"consumes 取自 next 指令；地图是上游产物的查阅地图，非加载清单"；②workflow-changes §6 Handling 补 Park 步骤、On Resume 改指分级阅读；③新增 test_fresh_init_has_no_resumed_alerts_for_engine_files（载荷测试：排除逻辑若被移除即红）+ none/legacy 键集钉死 + note 截断落盘断言；④动词计数改 7（规格原文"列全 8 个"系计划笔误——7 个子命令，非实施缺陷）；⑤早退分支措辞补 hint 说明；⑥AGENTS.md 决策区间改 D1-D14。测试 141 → **144** 全绿，--check 零漂移。审核者环境无 shell，命令级验证（测试/--check/CI）由主智能体代跑并确认。

**负债清单追加**：⑨produces 若引入字面 `[`/`?` 字符，missing-produces（字面量判断）与 resumed-artifacts（glob 判断）将不一致——届时需 glob.escape 或显式字面量声明（来源：审核主张 B 裁决的残余风险）。

**第二轮审核（同日，reviewer 复审）**：裁决"修复轮通过，可作为提交依据"。修复逐条验收通过（tier-2 新措辞与 CTX-02 一致、workflow-changes §6 自洽、fresh-init 测试载荷成立[排除逻辑移除即红]、计数/键集/落盘断言全部到位）；三主张裁决：A 证伪（编辑事故无残留，逐行核查 GoldenOutputTests 区域）、B 部分证实（Phase 3 历史条目挂当前计数属时间线混淆，无功能后果）、C 证实（"8 个"确系规格笔误，jump --fresh 是 jump 的旗标非独立动词）。新发现 1🟡+6🔵，全部当场修复：🟡AM-05 断点通道改指 park（原指 audit.md，与 CTX-03 相抵且恢复通道不覆盖）；🔵 workflow-conventions 时间戳枚举补 park、AGENTS.md Phase 3 条目改"当时 77 例，现累计 144"、本文件 §7 规格就地注记 8→7 笔误、金样测试补 audit_bytes==文件字节数断言（格式微调不敏感）、session-continuity 早退指引改指 status hint+契约 §10（error-handling.md 不覆盖 legacy）、CliTests._run 委托 _run_main 消双实现。终态：144 全绿 + --check 零漂移。

### 2026-09-22（续三）：Phase 3.2 开工——Trellis 借鉴登记表（WP-7-①）

四档清单自 §7 Phase 3.2 第 9 条迁入，加"状态"列。WP-7-②（5A/5B 拆写 + Phase 4 设计输入挂档 + ④档三项入不排期）为立项时前移完成，开工核验无漂移。

| 档 | 项 | 去向 | 状态 |
|---|---|---|---|
| ①立即 | brainstorm 三纪律 | WP-1（Evidence-First 提问纪律） | 已完成（2026-09-22） |
| ①立即 | 成功度量清单 | WP-2（dogfood 协议） | 已完成（2026-09-22） |
| ①立即 | 消融对照 | WP-2（dogfood 协议） | 已完成（2026-09-22） |
| ①立即 | 长制品导航索引 | WP-3（DOC-06） | 已完成（2026-09-22） |
| ①立即 | 批量提交协议 | WP-4（B&T Commit Protocol） | 已完成（2026-09-22） |
| ②排期 | 单层活知识树闭环 | Phase 5A 立项（骨架已落 §7） | 已落档（实施在 Phase 5A） |
| ②排期 | spec 冷启动 | WP-5（RE 可选产物为先行） | 已完成（2026-09-22） |
| ②排期 | 契约硬规则单测清零 | WP-6 | 已完成（2026-09-22） |
| ③相位触发 | 上下文策展清单 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | 派遣三件套 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | channel 事件日志 vs claim 注册表对照 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | 单元依赖显式化 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | spec 移植模式 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | knowledge_refs 字段 | Phase 5A | 已落档（设计稿 docs/result-oriented-delegation-design.md，处理挂 Phase 4 输入第 6 项） |
| ③相位触发 | 学习双出口 | Phase 5A | 已落档（实施在 Phase 5A） |
| ③相位触发 | 任务信封设计稿处理 | Phase 4 输入第 6 项 | 已落档（实施在 Phase 4） |
| ④仅记录 | 技能版本戳 | 技能分发/升级阶段再议 | 已落档（不排期，带触发条件） |
| ④仅记录 | 模板升级保护 | 技能分发/升级阶段再议 | 已落档（不排期，带触发条件） |
| ④仅记录 | evidence-first 扩展范式 | 技能分发/升级阶段再议 | 已落档（不排期；**与 WP-1 非同一物**：此项=扩展结构范式，WP-1=提问纪律） |

执行顺序：WP-7 → WP-6 → WP-1 → WP-3 → WP-5 → WP-4 → WP-2 → 收尾（登记表状态回填 + AGENTS.md 测试数 + 全量 unittest + --check + 散文一致性 sweep）。

### 2026-09-22（续四）：Phase 3.2 实施完成

开工即收尾，同日完成全部 7 个工作包（并行分发 3 个 executor：WP-6 测试 / WP-3+5+4 文档 / WP-2 新文档；WP-1 强耦合由主智能体直做）。要点：

- **WP-6**：test_generate.py +367 行/25 测试（Rule1~15 各类，规则 9/11/16 既有覆盖在 docstring 映射表注明）；映射表以模块 docstring 固化（含规则 12 的 SKILL_ROOT 调用期 patch 方法说明）；保留键 reviewer/sensors 夹具锁定契约 §5；实施中发现规则 7 实际校验点在 `_validate_references` 而非 build_stage——按实际实现测试，行为与契约一致，零出入。
- **WP-1**：question-format-guide.md 顶部 Evidence-First Policy（优先级条款覆盖各阶段 "when in doubt, ask" 类指令 + 豁免表：RA Step 2.5 scope 聊天问题、RA Step 5.1 扩展 opt-in 问题）；Multiple Choice Guidelines 新增 Recommendation and Trade-off 小节（与 QT-01 流程无涉、AM-04 auto-recommended 恰选 "(Recommended)" 项）；排序纪律并入 Best Practices #3；Question Structure 模板与 Summary 清单同步两要素；6 处探索可解示例全部标注（新/旧项目由 WD/RE 定、数据库/部署/架构 brownfield 先探索）；sweep 落地 9 文件（8 个产问题阶段文件各 1 行 Evidence-First gate 指针 + overconfidence-prevention.md "Default to Asking" 补门控）。验收达成：全树 grep 各 ask-aggressively 指令均有相邻门控从属化，无孤立相抵指令。
- **WP-3**：DOC-06 导航索引（advisory）：≥300 整行内容制品顶部"任务→章节"表覆盖全部 H2；排除 audit/state/handoff/checkpoints/问题文件；:21 补 Advisory 例外条款（列出不阻断）；Overview 与 Enforcement 表同步。
- **WP-5**：RE Step 9/10 之间无编号小节 "Optional Artifact: Working Conventions"（步号零重排）；source-backed 纪律（每条约定带来源引用）；定位 Phase 5A 知识树种子/导入源（防两套存储分叉）；免 frontmatter 改动（produces 通配已覆盖）；Step 10 产物清单与 Step 12 完成消息同步。
- **WP-4**：B&T Step 9 内 "Commit Protocol" 子节，时序定死（门批准 → report approved → 完成消息正文呈现 commit 计划 → Approve & Continue 即批准执行；**时序表述已于实施后审核更正，以 build-and-test.md Commit Protocol 新序为准**）；六条内容（脏文件二分/一次性计划/禁 amend-push/非 git 对齐 AUD-02 跳过/审计+hash 入 summary/条件式归档顺序）；AM-03 不自动 commit。
- **WP-2**：docs/dogfood-protocol.md（100 行中文）：六条度量（2/5 定性、6 待 5A）、消融对照（历史+引擎内开关，显式声明无引擎臂不可构造 D6/HARD STOP/Only-next-routes）、数据源对齐 3.1（audit_entries/audit_bytes/分级阅读）、一次一表模板含软警告升级决策回填行。

**终态**：测试 144 → **169** 全绿；--check 零漂移；登记表 7 行回填"已完成"；AGENTS.md 测试数与路线图同步。规格两处既知小漂移（WP-5 ":302 步号自引用"锚点过期、测试基线数 102→144）均在就绪核查中预判并按语义稳健指令处置，无实施影响。

**负债挂档（第 12 条六项，随本轮 §9 落档）**：①WP-5 通配单列 per-produce 决策→gen-2（未决）；②5A 触发器跨会话计数 best-effort→Phase 5A 设计输入（未决）；③WP-4 二分语义随 Phase 4 claim/merge 重审→Phase 4 设计输入（未决）；④登记表漂移风险→已由收尾回填对冲，长期靠"以 §9 为准"标记（§7 第 9 条已加注）；⑤消融无引擎臂违宪→永久（除非契约变更）；⑥四档清单状态列"计划中"待收尾刷新→已消解（本轮收尾回填完毕）。

**实施后审核（同日，reviewer 全量静态审查）**：裁决"通过，可作为提交依据"，0🔴/1🟡/4🔵；五主张裁决：A 证实（Neo4l 虚惊无残留）、B 部分证实（overconfidence :60/:74/:100 三行无相邻门控，验收条款实质达成/字面未全达）、C 证实（映射表 16 规则无遗漏，30+25=55 与 114 合计 169 精确吻合）、D 实质满足（行内门控约束力强于指针行，意图达成）、E 证实（步号顺移无交叉引用破坏）。审核发现全部当场修复：🟡六条负债挂 §9（本段即修复）；🔵overconfidence 三行补门控半句（B 项字面口径随之达成）、AGENTS.md Phase 3.1 行改"当时 144 例"范式、B&T Commit Protocol 时序句重排（完成消息含计划先呈现→Approve & Continue 即阶段批准+执行授权→report approved→执行，消除"批准后才见计划"的歧读）、§7 第 9 条加"已迁入 §9，以 §9 为准"标记。

**第二轮审核（同日，reviewer 复审修复轮）**：裁决"修复轮通过（0🔴/0🟡/2🔵），可作为提交依据"；五项修复逐条验收属实，新鲜眼光复查未发现第一轮误判（169 计数静态精确复核、门控 sweep 抽查、新术语交叉引用、WP-3/5 本体抽样均过）。四主张裁决：A 部分证实（B&T/§7 时序张力属实且发现 §9 记录内亦有旧序残留——新发现第二处）、B 部分证实（:61 属覆盖度轴无需门控、:62 属边界字面未闭合）、C 证实（§9 记录无美化失真）、D 证实（括注二次修正后干净）。两条 🔵 当场修复：§7 :448 与 §9 旧序两处加"审核更正，以 build-and-test.md 新序为准"指针（对照 :409 行内更正先例）、overconfidence :62 补门控半句（"every included question must still pass the Evidence-First gate"）。命令级验证由主智能体代跑闭合：169 全绿 + --check 零漂移。
