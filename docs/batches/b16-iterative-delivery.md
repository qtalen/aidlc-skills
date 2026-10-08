# B16 · 迭代交付批（Iterative Delivery）· 2026-10-07 立项

| 项 | 值 |
|---|---|
| 状态 | ♻️ 已并入 B15（段一已实施·段二待实施）（2026-10-08 全量合并——D20.1~19 逐条处置与 12 文件归属见 [B15 档案其六处置表](b15-interaction-modes.md)；D20 编号保留、实施归属改挂 B15；本档案作为 D20 语义之家[子裁决全文/roadmap 模板/Trellis 考证]与被吸收方案的历史记录存续，正文不动） |
| 触发 | 用户即期需求——非技术用户一句话需求场景下，harness 按 PRD 一次性长程实施，最终产出 demo 而非可持续演进的真产品（执行秩序断裂 + 质量门向末端压缩） |
| 关联决策 | D20（本批产出，19 项子裁决随立项确认，见规格节）；D11/D15/D16 被引用不变 |
| 测试基线 | 立项时 237；实施时按 B13/B15 落地顺延对齐（预计 239→241±1） |
| 材料来源 | 2026-10-07 会话讨论链（五轮设计共识 + reviewer 计划审核 v1→v2，含 9 条待验证主张独立裁决）；Trellis 本地考证（`D:\Documents\PythonProject\opencode-suit\trellis\.trellis\workflow.md` :166-172/:322/:557、`tasks/archive/2026-05/05-10-task-artifacts-and-tiers/`，引用经 reviewer 复核属实）；v2.0 考证（实施前置工序 WP-0，材料 `opencode/` 只读）；主文档 §5 Phase 4 设计输入⑥（parent/child，见立项与裁决） |

## 立项与裁决

**背景**：用户终极目标是"一句话需求 → 自主完成软件开发与部署维护"。失败链四断点——① 意图断裂（需求未澄清，B15 已立项解决）；② 秩序断裂（一次性长程实施，本批解决）；③ 质量门空心（本批以每迭代 DoD 结构性收口）；④ 运行面缺位（Operations placeholder，显式登记开放项单独立项）。本批打击断点②③，"不再只是一个 demo"大概率成立；"线上持续运行"依赖断点④的后续批次。

**用户裁决（2026-10-07 讨论链确认）**：
1. **B16 批 + 新相位，排在 Phase 4 之前**——与 B15 构成非技术用户场景闭环（需求端澄清 + 执行端分片），且先行缩小 Phase 4 多会话协调的爆炸半径；与 Phase 4 正交（迭代 = 垂直时间切片，unit-major 波次 = 单轮构造内水平并行）。
2. **迭代边界人工门绝对**——v1 不做 AM 自动续迭代（D16 零改动，完成转移必停；自动链式迭代留作 AM 未来扩展，须显式立项修订 D16）。

**多批次战略论证（§7 四问之③，Phase 3.4 立相位依据）**：Phase 3.4 = "端到端产品交付"方向，批次构成——B16 迭代交付机制（本批）→ B17+ Operations 实义化（部署/监控/告警/回滚，"线上持续运行"唯一通路）→ 远期遥测回灌（运行反馈驱动 roadmap 修订，依赖前两者）。

**核心机制复用**：D15 再入通道就是"同产品新迭代的正规通道"（B07 修复 + fx991 三迭代 dogfood 实证——隔会话仅凭 status 探针正确路由、FR/US 编号续编、RE 产物复用）。本批不做新通道，做的是把"人事后驱动"的隐式迭代显式化为"roadmap 事前拆分 + 完成后引导"。

**与 Phase 4 设计输入⑥的关系**：⑥（parent/child 任务树——"树不是依赖系统"）的核心原则已由本批在**迭代维度**先行操作化（D20.5 依赖写在制品）；其注明的"与 D11 一版本一意图的张力"在迭代维度由 D15 语义消解（同产品多迭代 = 同一意图多个版本，版本边界由 git 承载）。Phase 4 若引入跨意图任务树，张力仍需届时裁决，⑥ 原文不动。

## 规格

### 决策清单 D20.1~19

**核心语义**

- **D20.1 迭代定义**：一个迭代 = 一轮工作流轮次（再入转移→完成转移）；下一迭代 = 新会话 + `jump --stage` 再入，同产品永不 `--fresh`；版本边界由 git 提交承载（D11/D15 原文不动）。
- **D20.2 roadmap 为模型侧活文档**：`aidlc-docs/inception/plans/roadmap.md`，WP 产出、随 WP 门批准；**引擎零改动**——迭代计数由 roadmap + git + audit（re-entry 条目）推导，状态文件不加 Iteration 行（Phase 4 与 claim 协同设计时再议）。
- **D20.3 人工门绝对**：完成消息呈现下一迭代预览 + 用户确认后才可再入；v1 不做 AM 自动续迭代（非目标显式登记）。
- **D20.4 两道门不互替**：roadmap 批准（WP 门）≠ 迭代开工确认（再入前人工门）。
- **D20.5 依赖写在制品**：迭代顺序/依赖只存在于 roadmap 文本与单元工件，任何结构（引擎状态）不隐含顺序；UG 按单元 DAG 复核下行闭包（Trellis "parent/child is not a dependency system" 同构）。

**拆分判据**

- **D20.6 粒度本质**：一个迭代 = 一轮工作流内能以全质量门收尾的最小可演示增量（判据对象是"能否全质量收尾"，不是尺寸直觉）。
- **D20.7 硬判据**：H1 下行闭包（迭代 K 不依赖 >K 才交付的能力；WP 按 FR 依赖查、UG 按单元 DAG 复查）；H2 可观测结局（每迭代结束存在外部可检验物，禁止黑暗迭代）；H3（缩减）= 全量回归绿 + 本迭代可演示验收。原拟 H3 中的"staging 部署演练 + 薄运维交接物"**降为 DoD 占位字段**（Operations 实义化后升格硬判据；开放项挂账）——避免硬判据在 Operations 占位阶段悬空不可执行。违例须门批准前修复或显式豁免留痕。
- **D20.8 软判据**：S1 骨架先行（迭代 1 = 最薄端到端纵切，非"先做完某层"）；S2 一句话叙事（讲不出 = 太薄合并，要列清单 = 太厚再拆）；S3 风险前置；S4 硬化迭代预留（连续功能迭代后或 Deferred 溢出时插入）。
- **D20.9 覆盖规则**：用户显式拆分永远赢（scope 先例）；模型呈报 H1/H2 违例代价；用户坚持 → audit 留痕 + roadmap 风险注记。
- **D20.10 单迭代合法退化**：N=1 roadmap 合法；非 classic scope 默认不拆（scope 体系已回答一轮尺度问题）；express 豁免。
- **D20.11 用户自带拆分**：审计不重拆（判据 checklist 对照），呈报违例，微调须经用户确认——典型呈报案例：横切分层拆分（迭代 1 全部前端 / 迭代 2 全部后端）违反 H2/S1，建议改纵切。

**流程落点**

- **D20.12 再入增量纪律**：迭代 N+1 的 RA 范围 = roadmap 子集 + 对已交付功能的组合边界影响分析（B09 规则同构生效）+ RE/设计工件与代码一致性检查（承接质量软肋，规格写进检查项）。
- **D20.13 完成仪式三分支**（closing summary 内容扩展，**不构成 engine-contract 变更**——done 指令语义不变，`engine-contract.md` :90/:116 原文"present the closing summary and stop"未脚本化 summary 内容）：① 还有下一迭代 → 读 roadmap 呈现预览 + 人工门；② 最后一迭代 → 产品级收尾审查（对照 PRD 全量验收 + roadmap 关闭登记 + Deferred 去向处置）——**最后迭代标 shipped ≠ roadmap 完成**（Trellis parent 终集成审查同构）；③ 无 roadmap（旧项目/未拆分）→ 现行为不变。同一交互内顺序：closing summary（含预览/收尾）→ AM 轮次结束宣告（AM-10 既有条款）。**三层落笔**：详规住 workflow-changes 新增 Iteration Completion Ritual 节（tier-3 按需加载）；SKILL.md:126 压缩指针；build-and-test.md Commit Protocol 一句（改动面 #10）。
- **D20.14 roadmap 修订三时点**：迭代边界（最自然）/ 迭代中（小想法→Deferred 编号不回收；方向性→workflow-changes 既有流程，补 roadmap 同步条款）/ RA-WP 期（**WP 门 = roadmap-执行计划一致性检查点**）。shipped 条目不可改写（回滚 = git revert 或新迭代）；修订记录 append-only（DOC-04）。
- **D20.15 "建议更小拆分"是被批准的拒绝动作**：用户坚持一次性且模型判断跑偏风险高 → 给拆分建议 + 呈报代价，不沉默照做也不拒绝服务（Trellis consent gate 同构：拒绝时不做大范围 inline，只做解释/澄清/拆分建议）。
- **D20.16 rollup 模板内建**：shipped 迭代压一行 + git 指针，**压行发生在 ship 转换当刻**（迭代边界提交批内完成），此后该行不可再改写（与 D20.14 自洽）；5A 观察项纪律前置进模板（Trellis journal 2000 行硬上限先例）。
- **D20.17 轻量反馈回灌**：迭代边界仪式收集用户口述生产观察 → roadmap 修订时点；遥测级回灌依赖 Operations 实义化，不在本批。
- **D20.18 roadmap 产线条件**：**不进 frontmatter produces**。理由：(a) produces 语义为"阶段执行即无条件产出"，roadmap 是"scope × 拆分判据"双条件产物，语义对不上；(b) frontmatter 变更会破坏本批"引擎零改动 + `--check` 零漂移"目标。守护改由规则文本 + 完成仪式存在性检查承担；取舍（放弃 produces_missing 机械守护）记录在案。*v1 计划曾以"非 classic scope 每轮触发 produces_missing 噪声"为由，reviewer 实测证伪（`engine.py:873-894`：N≥2 且全部缺失才报，WP 的 execution-plan.md 恒产，永不触发）——理由已改写，决策不变。*
- **D20.19 非目标**：AM 自动续迭代；引擎迭代感知；Operations 实义化（单独立项，本批只放 DoD 占位字段）；多 intent/compose（D11 不变）。

### 改动面（12 文件，含 2 项立项落盘物）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `references/inception/workflow-planning.md` | 新增 Step：Iteration Planning（判据决策树：scope 分流→价值测试+视野测试→N=1 退化；用户自带拆分审计模式；"建议更小拆分"出口动作）；roadmap.md 模板与产出规则；Step 7 execution-plan 模板加 Iteration Scope 节（本轮=迭代 K，FR 子集）；Step 9 呈现加 roadmap 摘要。**frontmatter 不动**（D20.18） |
| 2 | `references/inception/units-generation.md` | 单元生成作用域 = 当前迭代 FR/US 子集；新增下行闭包校验步骤（依赖 >K 迭代能力 → 报 roadmap 缺陷回 WP）；既有单元增量更新不重生成 |
| 3 | `references/inception/requirements-analysis.md` | 再入分支补两条：迭代子集范围 + 组合边界影响分析；RE/设计工件一致性检查项 |
| 4 | `references/common/workflow-changes.md` | Re-Entering 节加 roadmap 流程（完成态先读 roadmap→预览→人工门→jump）；新增 **Roadmap Changes** 节（三时点协议 + shipped 不可改写 + 修订 append-only）；新增 **Splitting an Oversized Iteration** 节（视野破裂/H1 迟发违例 → 完成在飞单元→修订→重计划，禁单元中途拆）；新增 **Iteration Completion Ritual** 节（D20.13 三分支详规 + AM 宣告顺序 + roadmap shipped 标记时机） |
| 5 | `references/common/session-continuity.md` | 完成态呈现**路径核对**：`:88` Menu Execution 完成态分支 + `:23` Welcome Back 模板 "none — workflow complete" 行，两处按需同步 roadmap 下一迭代预览呈现 |
| 6 | `SKILL.md` | `:102` completed 行加 roadmap 路由前置；`:126` done 消费补三分支压缩指针（详规指 workflow-changes 新节）；行数断言同步 |
| 7 | 根 `AGENTS.md` | `:5` 决策区间 `D1-D19→D1-D20`、批次区间 `B01-B15→B01-B16`（**立项时已同步**，§7 指针同步纪律）；`:15` 目录表批次区间 `B01-B14→B01-B16`（立项时顺手修 B15 残留）；路线图速览 Phase 3.4 行 + 待实施行（立项时已加）；`:49`/`:62`/§3.1 测试计数**留实施时**按实际数更新 |
| 8 | `docs/batches/b16-iterative-delivery.md` | 本档案（立项落盘物） |
| 9 | `docs/integration-plan.md` | §2 D20 行、§3 B16 行、§5 Phase 3.4 节、§6 Operations 实义化开放项（立项时已加）；§7 `:205` "Phase 4 将来 = B16+"→"B17+"（立项时已改）；实施时无剩余 |
| 10 | `references/construction/build-and-test.md` | Commit Protocol 补一句：多迭代项目，迭代边界提交批包含 `roadmap.md`（迭代 K 标 shipped + rollup 压行，随 B&T 门提交计划入库——迭代版本边界本就锚在此门的提交计划）；完成消息模板本体不动（迭代预览属 done 阶段 closing summary，不属 B&T 门消息） |
| 11 | `references/inception/user-stories.md` | **WP-1 裁决项**：预期一句话——多迭代项目 US 按当前迭代范围增量撰写（经 RA 迭代子集继承，US 编号续编）；规格期判定是否需要并留痕 |
| 12 | `docs/batches/b15-interaction-modes.md` | `:190` "B16+ 候选"括注改 "B17+"（立项时已改，b15 状态待实施未冻结） |

**明确不动**：`engine.py`、`engine-contract.md`（done 指令语义不变）、`generate.py`（零 frontmatter 改动 → `stage-graph.json` 零变化，`--check` 零漂移）、`welcome-message.md`（迭代再入不触发 welcome）。

### roadmap.md 模板草案（改动面 #1 产出物规格）

```markdown
# Product Roadmap

## Product Intent
<一句话 + 指向 requirements.md / PRD>

## Iteration Status
| # | Status | Goal（一句话） | Scope（FR/US 子集） | DoD | Git |
|---|--------|----------------|---------------------|-----|-----|
| 1 | shipped | ... | FR-1~FR-5, US-1~US-4 | 回归绿+验收 | abc1234 |
| 2 | next | ... | FR-6~FR-11 | ... | — |
| 3 | planned | ... | ... | ... | — |

<!-- Status 值：planned / next / in-progress / shipped / dropped -->
<!-- DoD 字段构成：全量回归绿 + 本迭代可演示验收（硬，D20.7-H3）；
     staging 部署演练 + 薄运维交接物（占位，Operations 实义化后升格）；
     硬化项（若有，S4） -->

## Shipped Log
<!-- rollup：ship 当刻压一行 + git 提交指针（D20.16），此后不可改写 -->

## Deferred / Backlog
<!-- 编号不回收（Type 10 / D20.14 同款纪律），后续迭代候选池 -->

## Revision Record
<!-- append-only（DOC-04）：何时、为何改、改动映射 -->
```

### 工序与分工

| 工序 | 内容 | 承担 |
|---|---|---|
| WP-0 | **v2.0 考证**：Operation 相位阶段构成与产物形态、有无 milestone/epic 概念、版本演进语义；可吸收点并入规格 | 主智能体（研究性） |
| WP-1 | **规格收口**：裁决项定稿——user-stories 作用域（#11）、D20.18 终稿确认、session-continuity 两处呈现点实际改幅、B15 落地后交互面条款对齐（D19.1~34 最新态）；产出各文件逐字正文 | 主智能体 |
| WP-2 | **实施与登记**：#1-#6、#10-#11 按序落地（**主智能体直做**——新撰散文全文即简报本体，非机械性实施，不满足 executor 委派条件，B15 先例）；#7/#9 剩余项（测试计数）收尾 | 主智能体 |
| WP-3 | **验证与收口**：测试套件、`--check`、主文档行数红线、关键词 sweep、逐文件复核、AGENTS.md 活指针核对 | 主智能体 |

顺序：WP-0 → WP-1 → WP-2 → WP-3。**B15 未落地前不开工 WP-2**（改动面重叠：RA/SKILL.md/session-continuity，串行硬约束）。

## 实施与实施期裁决

（待实施）

## 验证（预定验收标准）

**机械验证**：
- `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests` 全绿，+1~3 规则文本断言（断言 WP/workflow-changes 含关键节与关键句，B15 模式；引擎/生成器零改动，既有用例预期零变化）
- `python .agents\skills\aidlc-workflows\scripts\generate.py --check` 退出码 0（零 frontmatter 改动，预期零漂移）
- 负向冒烟（回归锚）：临时目录 init + 构造 completed 态 + roadmap.md，`status`/`next` 输出与改动前一致（roadmap 不进引擎视野）
- 生成区标记内零改动；只读目录零触碰
- 指针核验：根 AGENTS.md `D1-D19`/`B01-B15`/`B01-B14` 零残留；integration-plan `:205` 无 "B16+" 残留

**dogfood 验收场景**（fx991 或新项目，度量沿用 dogfood-protocol 六度量）：
- **A 隔会话续做**：迭代 1 done → 新会话 status=completed → 读 roadmap 呈现迭代 2 预览 → 确认 → jump 再入 → RA 增量（FR 续编/RE 不重跑/组合边界）→ 迭代 2 交付
- **B 三时点变更**：迭代边界重排 + 迭代中 Deferred 落账 + WP 期 H1 违例修订
- **C 判据校准**：一句话需求（如"做个科学计算器"）→ 多迭代 roadmap；小需求（CSV 导出按钮）→ 单迭代退化；用户横切分层拆分 → 审计呈报改纵切建议；**express/bugfix 走查确认非 classic scope 零迭代开销**（D20.10 行为验证）
- **D 收尾**：最后迭代 done → 产品级收尾审查呈现（≠最后迭代交付消息）

## 附注

**Trellis 考证记录（2026-10-07，引用经 reviewer 复核属实）**——吸收五点 + 反面一点，不吸收三点：

1. **依赖写在制品，不藏在结构里**（workflow.md:170 "Parent/child structure is not a dependency system"）→ D20.5；与"引擎零改动"路线独立收敛，交叉验证。
2. **账本不干活**（:322 "Do not start the parent"；parent 持需求源/任务映射/跨子验收/终集成审查）→ roadmap 定位 + D20.13② 产品级收尾审查（v2 计划审核补入）。
3. **最后一次检查必须全范围**（:557）→ 每迭代 Build-and-Test 全量回归，独立收敛互证。
4. **"建议更小拆分"是被批准的拒绝动作**（05-10 design.md §3.1 consent gate）→ D20.15。
5. **journal 硬上限自动轮转**（workflow.md:82，2000 行）→ D20.16 rollup 前置进模板。
6. 反面：Trellis 明确否决 epic status（05-10 implement.md:96）→ 佐证不加引擎迭代概念。
7. 不吸收：被动拆分（Trellis 拆分是 brainstorm 反应式，非技术用户不会自己驱动）；per-task 归档模型（B07 已否决的 O(迭代数×全文件) 路径，D15 单树活文档的对立面）；无完成预览（Trellis 靠用户现场挑下一任务，本批核心差异化正在于此）。

**计划审核记录（v1 → v2，reviewer 裁决：有条件可，条件全部满足后收口）**：待验证主张 9 条——7 证实、2 修正（主张② produces_missing 噪声路径证伪 → D20.18 理由改写；主张⑤ session-continuity "一句小改"存疑 → 扩为 :23/:88 两处路径核对）。发现 7🟡+6🔵 全部采纳：D20.18 理由改写（🟡1）、integration-plan:205 与 b15:190 B16+ 括注（🟡2）、AGENTS.md 活指针扩全（🟡3，其中"B15 遗留 D1-D18 未修"在审核后由 §7 指针同步纪律当日消解）、完成仪式三层落笔（🟡4，新增改动面 #10）、Phase 3.6→3.4 + 多批次论证（🟡5）、工序回归主智能体直做（🟡6）、H3 运维项降占位（🟡7）、user-stories 裁决项（🔵1）、session-continuity 路径核对（🔵2）、计数表述（🔵3）、"必加载集"改"按轮上下文增量"（🔵4）、express/bugfix 走查（🔵5）、D20.16 压行时机注明（🔵6）。正面确认：引擎零改动 + --check 零漂移在所列改动面下自洽；D20 与 D11/D15/D16/D13 无未声明冲突；B15↔B16 串行正确；Trellis 引用与测试基线数字可溯源。

**风险与开放项**：
- 按轮上下文增量 +6~8KB（主要落 WP/UG/RA/workflow-changes 阶段文件，按需加载；SKILL.md 必加载集增量极小）——详细规则住 workflow-changes（tier-3 按需），WP 只放判据决策树
- roadmap 增长（5A 同族观察项）→ rollup 模板内建对冲，并入 5A 观察项
- Operations placeholder 悬空 → §6 开放项 "Operations 实义化"（Phase 3.4 第二批候选 B17+）
- 测试基线漂移（B13/B15 顺序）→ 实施时对齐（B09-B13 先例）

**前置依赖与衔接**：
1. 串行链 B13 → B15 → B16 → Phase 4；B16 WP-2 必须等 B15 落地。
2. B15 规格已演进（Trellis 二次吸收 D19.30~34 + 回写时点回退其三 + RA 第一性原理搭车 D19.34）——WP-1 以 **B15 落地后的最新规格**对齐交互面条款（question-format-guide / RA 模式入口 / SKILL.md Question File Format 节触点）。
3. 主文档红线 350（立项后 235 行，余量充足）。
