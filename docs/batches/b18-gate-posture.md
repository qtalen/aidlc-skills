# B18 · 门姿态与 AM 退役批（待实施）· 2026-10-19 立项

| 项 | 值 |
|---|---|
| 状态 | ✅ 已实施并提交（e3cad57 主体 + fef020c 二轮终审修复；2026-10-19 立项·四项裁决全按推荐，10-19~20 实施；两轮收口终审〔一轮 5+8+4、二轮 5+6+3〕全部处置；239 全绿 + `--check` 零漂移） |
| 归属 | 独立姿态批（无 Phase 建设链硬依赖；Phase 5B reviewer 接线的姿态地基；与 B17 触面小交叠、先后自由） |
| 触发 | 四会话设计讨论 2026-10-08~10-19：审批门价值分析 → AM 两难与值班模型 → reviewer 合成形态 → openspec 失败案例回灌 → 门姿态处置地图 → 只读遏制（设计底稿 = 用户级 plan brief v4，见 §9） |
| 关联决策 | D16/D17/D18（被本批 AM 退役 D 显式取代）、D19（PB 硬门）、D20（完成仪式绝对人工门）、D15（设计级修复再入，处置地图引用）、DOC-04（取代注记纪律）、D13（本批零新生命周期动词）、B17 设计原则 P3"AM 中立"空位由本批填充 |
| 量级 | 本体 = 一个实施会话 + 一轮收口终审 + 一次提交（触面 ≈ 11 阶段 frontmatter + 2 处阶段条款改写 + stage-contract 3 处 + 生成器 2 处 + 引擎 AM 清理 + AM 引用清扫约 11 文件 + 测试增退） |
| 测试基线 | 立项时 253 全绿 + `--check` 零漂移（2026-10-19 实测）；实施后 **239 全绿 + 零漂移**（253→239 精确对账：AM 测试退场 -21、新增 brief 门型映射 2 + BRF 姿态断言 5、终审残留守卫 +1、门规则测试改锚 PB 硬门净 -1） |

## 1. 立项背景

现行 classic 流程 15 阶段中 13 个带门（8×approve-continue + 5×two-option，code-generation 系 per-unit 门随单元数翻倍）。用户实测姿态：RA 阶段做主要需求确认，其后机械点继续，迭代末用端到端黑盒测试验收。设计讨论（brief §2/§3）结论：

1. **橡皮图章门是负价值不是零价值**：假审计记录（`approved` 进审计但用户没读——审计最核心字段系统性失真）+ 警报疲劳（肌肉记忆腐蚀 RA 门与 D20 仪式的严肃性）+ 覆盖错觉（流程看似处处把关，低估 E2E 该投的注意力）。
2. **门的存在判据**：门上发生的事会改变用户或模型一方的行为 ⟺ 门值得存在；门按决策价值存在，不按产物边界存在。
3. **AM 两难是假二元**：全手动 = 均匀耗注意力、检测率≈0；AM 全开 = 静默停点但不新增探测。共同缺陷：流程里没有坑探测器。用户恐惧的坑主体（静默缩水/完成幻觉/不可见质量）全部机器可检——缺的是传感器不是门（传感器提前为独立开放项，见 §5）。
4. **值班模型（on-call，用户认可）**：注意力由事件召唤（机器报警 / fork 升级 / 行为验收），不由阶段边界召唤。目标姿态下"自主"不再是模式而是默认——AM 作为"自主/监督"模式开关随被压制物一起消失。
5. **AM 退役用户决策原话（2026-10-09）**："我觉得AM可以去除掉。但是三门模型里 Code Gen Hold 可以保留。"——Code-Gen Hold 转正为常设方向门（本批交付物 B）。

## 2. 设计原则（六条，统领全批）

1. **门按决策价值存在**：中间门拿不出 20 行以内用户愿意付费读的决策备忘 → 它就该是简报（自检准则，见 §3.E）。
2. **值班模型**：简报制 + 真门 + 事件召唤；反对随时可以（口头，workflow-changes Type 机制 + jump 承载），批准只在门上——注意力的正确经济学。
3. **审计从源头不说谎**：brief 阶段 `completed` 即诚实语义，`approved` 只出现在真门（§3.D）。
4. **单向安全**：姿态只允许 brief→hard 升格方向，永不反向；v1 阶段级 frontmatter 为 SSOT，scope 级姿态维度缓议（避免 6 scope × 15 阶段组合矩阵）。
5. **校准回路**：简报被忽略是常态（它首先是审计轨迹）；坑事后追溯到某阶段简报 → 学习闭环两出口：升回硬门或加 tripwire。门的数量也是标定出来的，不是一次性判决。
6. **零引擎语义改动**：brief 门型经编译映射为 `none`，引擎门判定逻辑（engine.py:1281 字面比较）不动；引擎唯一的改动是 AM 清理（翻转逻辑与 `autonomous` 键退场），不新增行为。

## 3. 交付物

### A. `gate: brief` 第四门型（机制前置）

语义 = `none` + 模型侧简报义务：阶段完成后呈现 ≤5 行简报（关键决策/风险/产物位置），不等待、不请求批准；引擎侧报 `--result completed`。

**生成器两处前置（10-10 reviewer 代码级核对修正的产物，勿走"只加 stage-contract 一行"捷径）**：

- (a) `GATE_VALUES` 扩入 `brief`（generate.py:85，现封闭三值枚举；:444-446 校验会拒绝新值）；
- (b) 编译 stage-graph.json 时把 `brief` 映射为 `"none"`（generate.py:713 现为原样透传）。

若漏 (b)：11 个 brief 阶段的 `report --result completed` 会被引擎拒绝（engine.py:1281-1287）、模型被迫报 `approved`——恰好制造本批要消灭的假批准。

stage-contract.md 同步三处：§3 门型表、§2 字段表枚举（:55）、§7 校验规则。

### B. 处置地图（四硬门 + 简报制）

口径：三门（契约/方向/行为）是概念骨架，落地为**四硬门 + 简报制**——PB 是概念模型之外的"产品领地门"（D19 纯人类领地，本就是硬门）。

| 阶段 | 处置 | 备注 |
|---|---|---|
| product-brainstorm | 硬门（保持 approve-continue） | 纯人类领地；无门前审查 |
| requirements-analysis | 硬门（保持 approve-continue） | 契约门；"RA 自洽审查先跑"为 Phase 5B 门前顾问接线，本批不落地 |
| code-generation | **方向门**：每轮首单元开工前停一次，≤10 行方向简报（单元数/顺序/设计阶段关键决策/风险/相对 RA 漂移），approve-continue 式交互；后续单元简报 | 不新建阶段，改写 code-generation.md:50 条款（AM-11 同构）。机制载体待 ⭐4 裁决（推荐：frontmatter `brief` + 规则级停点） |
| 完成仪式 | 硬门（绝对，D20） | 行为门；迭代边界人工门（B16 交付环承载），非阶段门型；"B&T 证据审查先跑"为 Phase 5B 接线 |
| workflow-planning | brief + **偏差升级例外**：计划偏离 scope 默认网格（增删阶段）时升为问句 | fork 升级第一应用点〔形态待 ⭐3〕 |
| user-stories / application-design / reverse-engineering / units-generation | brief | 单元清单与顺序由方向门兜底 |
| functional-design / nfr-requirements / nfr-design / infrastructure-design | brief（per-unit 亦然） | 补 L5 缺口靠 Phase 5B RA 自洽审查，不靠这些门 |
| build-and-test | brief | 证据进仪式呈现；commit 纪律归仪式（§3.C 遗产升格③） |
| workspace-detection / operations | none（不动） | 本就无门 |

效果（按 ⭐4 推荐形态）：classic 从 13 个带门阶段 × per-unit 翻倍 → **2 个引擎阶段硬门（PB/RA）+ 1 个规则级方向停点 + 仪式人工门 + 11 阶段简报**；express = RA 门 + 方向门 + 仪式直线到底。（若 ⭐4 选备选则计为 10 简报 + 3 引擎硬门。）

### C. AM 退役（遗产三分 + 清理面）

**自洽性**：目标模型默认姿态 = 简报制 + 真门 + 事件召唤，"自主"不再是模式而是常态——压制器随被压制物一起消失。删除的不是自主能力，是"自主/监督"二元的模式开关本身。B17 设计原则 P3"AM 中立"为此预留空位（"撤 AM 时清理面零牵连"），本批即填充该空位，两批先后自由。

**遗产三分**：

- **升格为通用规则（不随模式消亡）**：
  1. AM-11 → 常设方向门（交付物 B）；
  2. AM-04 语义 → 简报阶段通用提问规则：自动选推荐项 + 回写 rationale；真正不可裁量的单个问题升级给人（同时成为值班模型 fork 升级事件的通用形态）。边界规则：四硬门所属阶段的问题问人，其余阶段提问自动答 + 升级例外。落点 question-format-guide.md（现 :130 为 AM 引用，本条改写即完成该处清扫）；
  3. build-and-test.md:385"never commit automatically"（现为 AM-03 条款形态）→ 挽救后独立成文，归完成仪式纪律。
- **删除**：AM-01/02/03/05/07/08/09/10、激活问题、`## Autonomous Mode` 状态区（D18 三行制）、引擎的 AM-10 轮末翻转逻辑与 status JSON 的 `autonomous` 键。
- **架构红利**：engine-contract §6"引擎写模型区的唯一例外"（AM-10 轮末过期翻转）随之退役——状态分区所有权变纯，引擎回到"永不碰模型区"的干净不变量；Phase 4 挂账的"AM 状态注记化"开放项整个坍缩（claim 并发锁设计不受影响，继续保留）。
- brainstorm"纯人类领地"不受影响：AM 延迟激活规则删除后靠 PB 自身的门继续成立，无缺口。

**清理面**（2026-10-19 抽查锚点未漂移；实施时以全量 AM 关键字枚举为准）：

| 动作 | 位置 |
|---|---|
| 删除整个目录 | `extensions/workflow/autonomous-mode/`（规则 + opt-in 桩两文件） |
| 改写（不是删） | `construction/code-generation.md:50`——AM-11 引用改写为常设方向门条款 |
| 挽救后删 | `construction/build-and-test.md:385`（commit 纪律独立成文） |
| 引用清扫 | SKILL.md（101/102/297）、engine-contract.md（§5/§6/§8/§10 约 8 处）、session-continuity.md（4 处）、workflow-changes.md（2 处）、workflow-conventions.md（3 处，含 AM 规则索引表）、question-format-guide.md（130，由 §3.C 升格②改写覆盖）、product-brainstorm.md（97/194-198）、checkpointing.md（43，"同 AM-03 惯例"类比措辞重写） |
| 引擎与测试 | engine.py 的翻转逻辑与 `autonomous` 解析、状态模板删区、AM 相关测试退场（计数下降正常） |

### D. 审计语义（结构性消解）

brief 阶段从头不产生批准记录——`completed` 就是它的诚实语义；`approved` 只出现在真门。不需要 `auto-continued` 新 result 值，审计从源头不说谎。（旧开放项"approved vs auto-continued 审计语义"就此消解。）

### E. 配套条款

- **反对通道保留**：任何简报后可口头反对（workflow-changes Type 机制 + jump 承载）；形式化否决点收缩到四硬门。
- **自检准则双向化**：某阶段的简报持续压不到 5 行以内 → 它有真决策内容，该升回硬门。阈值关系（对象不同、互补）：≤5 行 = brief 完成消息；≤10 行 = 方向门简报；20 行 = 值得用户读的下限判据。门姿态不是一次性判决——frontmatter 一个字段的事。
- **风险轴正交**：不可逆/高爆炸半径动作（数据迁移、对外契约、安全敏感）保持硬门哪怕简报姿态开着——机制声明形态仍开放（brief→hard 单向升格已定，见 §5 非目标）。

### F. 测试与治理登记

- 生成器：`brief` 进 GATE_VALUES 枚举校验测试；stage-graph.json 映射断言（`brief` → `"none"`）；`--check` 幂等。
- 引擎：AM-10 翻转与 `autonomous` 键相关测试退场（枚举清单以实施时 grep 为准）；门判定测试不变（映射后引擎行为不变，回归验证）。
- 规则文本：test_rule_invariants.py 抽样钉短语（方向门条款、AM-04 升格规则句、commit 纪律独立条款）——同 B17 D1 口径：断言只能证规则句存在、不能证遵守，真验收靠 dogfood。
- 治理：两条新 D 随实施登记——AM 退役 D（**显式取代 D16/D17/D18**，决策只取代不静默删除；B08/B10/B11 批次档案是历史不动）+ 门姿态 D（brief 门型与处置地图）。原"D 登记时机"开放项随本立项收口：等实施一起登记。

## 4. 批内裁决（已裁定 2026-10-19，实施首步，四项全部采纳推荐/主选项）

**裁定结果**：⭐1 **一步走**（全包一次落地）；⭐2 **方向门 = AM-11 原槽位**（code-gen 首单元前——吃到单元级设计决策汇总 + 换模型窗口）；⭐3 **认 WP 偏差升级形态**（brief + 计划增删阶段升问句——fork 升级第一应用点）；⭐4 **规则级停点**（code-generation frontmatter 降 `brief` + :50 条款停点；代价声明生效——无引擎强制，dogfood 观察被跳过则升级引擎机制）。以下为裁决时的选项原文：

1. **⭐1 一步走确认**：本批全包（brief 门型 + 处置地图 + AM 退役 + AM-04 升格，一条 D 链一次落地）。〔推荐一步走〕理由：硬依赖批内满足（实施顺序先方向门后 AM 清扫）/ 两步中间态 = 门照旧 + 无 AM = 纯手工点继续，无观察价值 / 全部文本级改动 git 可逆、阶段粒度可单独回调 / 少一轮生成器与测试基线翻动。
2. **⭐2 方向门位置**：AM-11 原槽位（code-gen 首单元前——吃到单元级设计决策汇总 + 换模型窗口）〔推荐〕vs 构造边界（units-generation 后、任何单元设计前——更便宜但信息更少）。
3. **⭐3 WP 偏差升级形态**：workflow-planning 降 brief + 计划偏离 scope 默认网格（增删阶段）时升为问句——fork 升级的第一应用点，认不认这个形态（设计底稿无记录推荐，需用户裁量）。
4. **⭐4 方向门机制载体（立项复核新增，设计底稿二义性）**：方向门的"每轮首单元停一次、后续单元简报"如何落地——
   - 〔推荐〕**规则级停点**：code-generation frontmatter 降 `brief`（引擎视角 none，各单元报 completed），停点锚定 code-generation.md:50 条款（"强制步骤须在当阶段实际加载文件里有锚点"透镜满足——阶段必载自身规则文件）。AM-11 同构（它本就是规则文本 + 停点形态）。推荐理由：备选形态下 per-unit 的 `approved` 全进审计而人只停第一次——单元 2..N 是假批准记录，恰好复活本批要消灭的东西；且备选要求引擎支持"轮内首单元门"语义，违背零引擎改动。
   - 备选：frontmatter 保持 approve-continue + 条款改写（审计含未停的 approved 记录，见上，不推荐）。
   - 代价声明：推荐形态下方向停点无引擎强制、无审计事件（同 AM-11 原状）；若 dogfood 观察到被静默跳过 → 再升级为引擎机制（届时动引擎，属新批）。

## 5. 明确非目标

- **reviewer 机制本体**（合成形态：通用执行器 + rubric 库 + 事实型 brief + 降级链 + 三位置接线 + 修复验证体系）→ Phase 5B 立项（全量素材见 §9 设计底稿）；处置地图中"RA 自洽审查先跑 / B&T 证据审查先跑"为 Phase 5B 接线预留语义，本批不落地。
- **reviewer 只读遏制 L3 三明治契约**（内容层 hash 主检 + 结构层 `(rev-parse HEAD, status --porcelain)` 辅助）→ 挂账待实践证据（触发条件：出现一次 reviewer 越界或审查窗口内无法解释的变更 → 立即上线）；L0/L1/L2 三层常设。
- **最小传感器集提前**（traceability + claim-sources）→ 独立开放项（值班姿态可放心离场要等传感器齐——提前论据仍成立，另行立项）。
- **风险条件升级机制**（不可逆动作硬门的声明形态：scope 级/阶段属性/动作级判定）→ 开放（单向安全方向已定）。
- **scope 级姿态维度** → 缓议，跑出证据再加。
- 不动 B17（P3 空位填充零牵连）；不动用户级 reviewer.md（非仓库文件）。

## 6. 实施顺序（一步走版，已按序执行完毕 ✅ 2026-10-20）

0. ~~实施首步：四项裁决（§4）~~ ✅（全按推荐）
1. ~~生成器扩值与映射~~ ✅（GATE_VALUES + 编译映射 + 枚举/映射测试先行）
2. ~~stage-contract.md §2/§3~~ ✅（枚举 + 门型表 + 编译映射说明）
3. ~~11 阶段 frontmatter 降级 + code-generation.md:50 改写（方向门条款）~~ ✅（4 个 per-unit 设计阶段委派 executor，其余主智能体；模板块统一 COMPLETION BRIEF 形态）
4. ~~AM-04 语义写入通用提问规则~~ ✅（question-format-guide「Stage Question Posture」+ workflow-conventions QT 组对齐段）
5. ~~AM 全量清扫~~ ✅（目录删除 + SKILL/engine-contract/session-continuity/workflow-changes/workflow-conventions/product-brainstorm 清扫；checkpointing.md 条目过期——D21 已随 CTX 删除该文件；三个扩展〔security/resiliency/PBT〕阻断条款措辞随门型同步）
6. ~~跑生成器 → --check 零漂移 + 测试套件绿~~ ✅（238 绿；对账见头部测试基线行）
7. 收口终审一轮（reviewer）+ 提交（含两条 D 登记）→ **D22/D23 已登记；终审与提交为余留步骤**

## 7. 风险与回调

- **最大风险 = 映射遗漏**（brief 未映射 none → completed 被拒 → 假批准复活）——生成器测试先行（§6 步 1）即为此；该缺陷形态 2026-10-10 已被 reviewer 代码级核对抓过一次，属已知陷阱。
- **AM 清理遗漏** → 全量关键字枚举兜底（§6 步 5）。
- **方向停点无引擎强制**（⭐4 推荐形态的代价）→ 锚点透镜（当阶段必载文件）+ dogfood 观察；被静默跳过则升级为引擎机制。
- **回调手段**：全部改动文本级 + frontmatter 字段级，git 可逆；单阶段升回硬门 = 一个字段的事（§3.E 自检准则）。

## 8. 与后续批次 / Phase 的接口

- **Phase 5B**（reviewer 状态机、传感器 report 阻塞校验、门仪式精细化）：本批四硬门即其"门前顾问/证据核验"的接线点；stage-contract §5 预留字段（review_class / sensors / summary_confirmation 等）本批不启用。
- **Phase 4**：claim 并发锁设计不受 AM 退役影响；"AM 状态注记化"挂账项坍缩（B18 消化）。
- **Phase 5A**：校准回路（坑→tripwire/升门）共享学习双出口闭环。
- **B17**：P3"AM 中立"空位由本批填充；触面交叠 = workflow-changes.md / session-continuity.md 两文件（AM 引用处 vs B17 新增节，不同区域），先后顺序自由，后实施者以 grep 复核。
- **roadmap 指针**：integration-plan.md 路线图中"B18+ Operations 实义化"随本立项顺延为 B19+（登记时一并修正）。

## 9. 设计底稿与素材（用户级路径，非仓库文件）

- **plan brief v4**：`C:\Users\qianpeng\.opencode\plan\2026-10-08-aidlc-gates-am-reviewer-design-brief.md`——四会话完整设计讨论（§5 reviewer 合成形态全量细节 / §5b 修复验证 / §5c 只读遏制 / §8 AM 退役 / §9 openspec 教训 / §11 门姿态）。Phase 5B 立项时的底稿；本档案为其"门姿态 + AM 退役"可实施部分的规格化。
- **reviewer.md v2**（已落地）：`C:\Users\qianpeng\.config\opencode\agents\reviewer.md`——现实锚定三档落位/完整性基线规则/三元组内联 = 已验证条款形态，Phase 5B rubric/brief/findings 契约直接继承；两次实跑验证高质。
- **openspec 失败案例**（教训源非工作对象）：`C:\Users\qianpeng\.agents\skills\openspec-workflow\SKILL.md.bak` + `C:\Users\qianpeng\.config\opencode\agents\openspec-reviewer.md.bak`。教训三原则：审风险不审转录 / 单发不循环 / 锚现实不锚散文。

## 10. 事前审核与立项复核记录

- **2026-10-09**：reviewer.md v2 改动清单经 reviewer 子智能体独立审核（6 问题：5 接受 1 折中）。
- **2026-10-10**：brief v3 更新清单经 reviewer 审核，**代码级核对抓出实现阻断缺陷**——`GATE_VALUES` 封闭三值枚举（generate.py:85）会拒绝 `brief`、引擎按 `gate != "none"`（engine.py:1281）会拒绝 brief 阶段报 completed——§3.A"生成器两处前置"即该次修正产物。
- **2026-10-19**：brief v4 更新清单经 reviewer 审核（2 问题 + 5 改进 + 4 建议 + 5 假设；处置：全收 11 / 折中 1 / 不采纳 2）；同日二次修订（快照规格分层化）未再送审。
- **2026-10-19 立项复核（本档案定稿前实测）**：门分布 grep 实证 = approve-continue ×8 / two-option ×5 / none ×2，与设计输入一致；generate.py:85（三值枚举）/ :713（原样透传）/ engine.py:1281 / code-generation.md:50（AM-11）/ build-and-test.md:385（AM-03）/ SKILL.md:101/102/297 均未漂移；测试 253 全绿（40.8s）+ `--check` 零漂移。两处底稿修正：①"九阶段降 brief"为计数遗漏（漏 B&T 与 code-generation）——实际 11 阶段；②"3 个引擎硬门"表述含方向门引擎形态的二义性——按 ⭐4 推荐读法修正为"2 引擎阶段硬门 + 1 规则级方向停点"，备选形态计数见 §3.B。

## 11. 实施记录（2026-10-19~20）

**触面清单**（31 改 + 2 删 + 1 新档案）：

- **机制层**：generate.py（GATE_VALUES 扩 `brief` + 编译映射 brief→none）；engine.py（`_parse_autonomous`/`_expire_autonomous` 删除、status `autonomous` 键移除、report/jump 过期块移除——引擎净减法、零新增行为）；stage-graph.json（再生成）。
- **契约层**：stage-contract.md（§2 枚举 + §3 门型表 brief 行、two-option 标注 currently unused + 编译映射说明）；engine-contract.md（§5/§6/§8/§10 AM 条款墓碑化或退场，§6 改"引擎永不写模型区"干净不变量，status schema 与 JSON 金样例去 `autonomous`）。
- **规则层**：workflow-conventions.md（五组化、APG 范围改硬门、QT 组 brief 提问姿态段、**新增 Group 5 BRF-01~03**、阻断发现条款双姿态化、执法表）；question-format-guide.md（**新增 Stage Question Posture 节**、`(Recommended)` 标记语义句改引、Summary 增行）。
- **阶段层**：11 阶段 frontmatter `gate: brief` + 完成模板块统一 COMPLETION BRIEF 形态 + Wait/Record 步改 Proceed/Log。特型：workflow-planning（⭐3 偏差升问句条款 + Step 8/10/11 连带改写）；code-generation（:50 方向停点条款、Part 1 计划审批退场、Step 15/16 合并）；build-and-test（commit 协议改授权问句 + 无条件 never-commit 纪律、AM 行删除）。functional-design / nfr-requirements / nfr-design / infrastructure-design 四文件同构改写委派 executor（12/12 编辑，验证零残留）。
- **清扫层**：`extensions/workflow/autonomous-mode/` 目录整删（规则 + opt-in 桩）；SKILL.md（bootstrap 表 2 行、编排循环 brief 行、11 阶段 blurb、per-unit 报告规则、所有权原则、NO EMERGENT 条款）；session-continuity.md（4 处）；workflow-changes.md（3 处，:291 变更流双姿态化）；product-brainstorm.md（红旗行 + "Autonomous Mode and Park"→"Park (and the Human-Territory Invariant)"）；security / resiliency / PBT 三扩展阻断条款措辞随门型同步。
- **测试层**：test_generate.py +2（枚举接受 brief、真树编译映射断言 11 阶段→none）；test_engine.py −21（AutonomousExpiryTests 整类 18 + autonomous key 3）+ 门规则测试改锚 product-brainstorm 硬门 + recent_events 事件序列更新 + golden 键集/金样本去 autonomous；test_rule_invariants.py 换 **BriefGatePostureTests**（5 断言：BRF 组在场、P13 措辞、方向停点锚定、提问姿态、never-commit 与 WP fork）。
- **治理层**：integration-plan.md（D22/D23 登记、B18 行翻转）、AGENTS.md（§3.1 所有权不变量 + 测试计数 238 + 路线图 ✅ 行）、本档案。

**验证**：`--check` 零漂移 + 238 全绿（终态复跑两次一致）；AM 残留 grep 复核——剩余命中全部为有意墓碑/出处注记；门语义 grep 复核——PB/RA 保留 approve-continue 全套、error-handling 恢复文本兼容双姿态。

**实施偏差**（相对规格，4 条）：① §3.F 所列"stage-contract §7 校验规则"无 gate 专项条款（§7 规则 4 泛化覆盖枚举违规），实际改 §2/§3 两处闭环；② 清理面表 checkpointing.md 条目过期——D21 已随 CTX 删除该文件；③ engine-contract / SKILL / engine.py 的 AM 条款采用墓碑句式（RETIRED/REMOVED 注记）而非整删，保可追溯；④ 规格外新增——三个扩展（security / resiliency / PBT）的阻断条款措辞随门型同步（构造阶段已无 "Continue to Next Stage" 选项可禁）。

## 12. 收口终审记录（2026-10-20，reviewer 子智能体，发现全部处置）

**结论**：机制层落地干净——stage-graph 实际分布 2×approve-continue + 13×none 与设计一致、引擎净减法、AM 在技能树内退场彻底（残留命中全为有意墓碑）、生成区不含 gate 字段故门型改动不可能造成漂移。抓出**规则层清扫不完整**（早期章节的计划审批/等待作答/选项模板残留 + 一处规则互斥），全部修复（触 20 文件；测试 238→239）。

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| R1 | 高 | APG-02/03 的 `report --result approved` 在方向停点必被引擎拒（code-gen 编译为 none），错误兜底会把阶段提前标完、搁浅剩余单元 | code-generation.md 停点条款改为"APG-01 意图分类适用；APG-02~04 转移记录不适用——停点不跑 `report`，hold/continue 只门控阶段工作是否开始" |
| R2 | 高 | 计划审批指令未退场且与新步骤同文件互斥：code-gen（condition/Overview/Rules/Criteria 四处）、units-gen（Step 9/10 硬停 "DO NOT PROCEED" + 三处）、user-stories（EXPLICIT APPROVAL 规则 + 两条判据） | 全部改呈报制措辞；units-gen Step 9/10 重写为 Proceed/Log Interaction；判据改 "presented and consistent" |
| R3 | 中 | 三扩展阻断条款第 3 条仍要求"只呈现 Request Changes 选项"（简报阶段无法落账、与 BRF-01 冲突） | 改双姿态条款：硬门只呈 Request Changes；简报阶段先解决再简报或升级（BRF-01） |
| R4 | 中 | 七个简报阶段的提问步仍写"等待用户作答"，构造期免打扰收益落空 | 统一改 Stage Question Posture 自动作答步（7 文件 × Request/Collect 两步重写或单行替换） |
| R5 | 中低 | "Workflow Planning gate/approved" 残留约 10 处（SKILL:21、stage-contract ×2、engine-contract ×2〔含 Execution Plan Summary 的 load-bearing 锚〕、workflow-changes ×2、RA ×3、engine.py init 模板占位） | 全部改 brief 措辞；init 占位改 `[filled at the Workflow Planning brief]`（测试无钉该串，实证安全） |
| 改进 ×8 | — | engine-contract 转移表未收录 brief；方向停点"每轮一次"判定锚不存在（Unit Progress 恒 reserved）；BRF-01 fork 定义装不下自点名例外（commit 授权/方向停点）；error-handling 补记顺序；D22 删除面"AM-01~11"与 ① 自相矛盾；engine-illustrated.md AM 节未同步（8 处）；stage-contract none 行计数；QT-03 澄清文件条款与姿态矛盾；workflow-changes "in every mode"/"re-run gates"；welcome-message 营销措辞；QFG "all other stages" 字面过宽 | 全部采纳：转移表 completed 行收录 brief、approved 行标两硬门；停点锚改"会话上下文 + 计划文件判定，存疑重呈（安全方向）"；fork 定义扩为 human-only（plan/scope/direction/history writes）；D22 改"AM-01~10（AM-11 升格见 ①）"；engine-illustrated 八处同步；其余措辞逐条修 |
| 建议 ×4 | — | 升级问句无文件时落 audit；静态残留断言；welcome 措辞；QFG 字面 | 采纳全部：QFG 补"无问题文件的升级问句记 audit（含原文）"条款；test_rule_invariants 新增 `test_brief_stage_files_carry_no_approval_residue`（11 文件 × 5 禁句静态守卫，239 例之一） |

**终审工具限制注记**：reviewer 会话无 shell/git 工具——`--check` 与测试套件未在其会话复跑（由主会话代跑：零漂移 + 239 绿）；其对生成区完整性的结论以渲染函数静态比对为据。

## 13. 二轮终审记录（2026-10-20，reviewer 复审提交态 e3cad57，发现全部处置）

**结论**：机制层再次确认干净（brief→none 映射、引擎门判定零改动、AM 残留 9 处全为墓碑、frontmatter 11×brief+2×approve-continue 与 stage-graph 完全对齐、测试计数算式自洽且 `def test_` 实测 239）；薄弱面在规则文本与治理文档——5 项第一层 + 6 改进 + 3 建议，全部处置。

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| 2R1 | conflict | integration-plan Phase 4 dogfood 输入仍列"AM 状态注记化"未标坍缩，与 D22 冲突；:146"依赖第 1 步"指代含混 | 改坍缩登记（划线 + 指向 D22；claim 并发锁指向硬依赖链第 2 步）；:146 改"依赖硬依赖链第 1 步（unit-major 启用 Unit Progress）" |
| 2R2 | ambiguity | RA（硬门）正文仍命令"交给用户手填并 STOP"，与 QT-01/新姿态点名 RA 走 QT 全流程互斥（预先存在，一轮清扫绕过了它） | RA Step 6 收集改 QT-01 工具流程（同交互调用、不交接文件）；GATE 块改"Answers Collected"语义；:140 "at any gate" 改硬门/异议双通道 |
| 2R3 | ambiguity | resiliency 扩展 User Decision Points 强制问用户 vs nfr-design 简报自动答（工艺选择不落 fork 定义清单） | 双侧落笔：扩展条款注明"brief 阶段 = extension-mandated fork，结构化工具问"；QFG 例外 2 扩充"extension-mandated user decision points 计入 fork" |
| 2R4 | conflict | welcome-message 四处仍承诺"approve the plan / approve implementation plans"，与同文件 :19 新口径自相矛盾 | 四处改新口径（真实决策门 + 偏差才问 + 异议随时 + 构造期走简报） |
| 2R5 | ambiguity | 三个简报阶段早期章节残留"get approval / approved plan"（units-gen Overview ×2、application-design ×2、user-stories ×2）——R2 同族漏网 | 六处清理；守卫断言扩充两条正则（`(get|proceed to) approval`、`approved (plan|methodology)`） |
| 改进 ×6 | — | RE/WP 双 report 指令（第二次必撞 invalid-transition）；QFG Summary "Always wait"；engine-illustrated 行号索引整体失准 + 类比行"自主模式"第 9 处残留；b18 状态行过期；CG 完成模板带 `[unit-name]` 后缀；守卫断言面与声明意图不符 | 全部采纳：RE/WP 各留 Step 13/Step 10 单一 report 入口；QFG 改"仅手动回退等待"；engine-illustrated 13 行行号按当前 engine.py 重排 + 类比改两行；状态行更新；模板标题改 "(all units)"；断言扩正则 |
| 建议 ×3 | — | Code-Gen Hold 可检索括注；workflow-changes :22 对齐双姿态；depth-levels/RA "at any gate" 族 | 全部采纳（停点条款加 "(formerly Code-Gen Hold / AM-11)"；:22 双姿态化；两处 gate 措辞改） |

**验证**：`--check` 零漂移 + 239 全绿（含扩充后的正则守卫——`approved plan/methodology` 与 `get/proceed-to approval` 在 11 个简报阶段文件零命中）。
