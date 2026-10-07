# B04 · 会话连续性增强（旧称 Phase 3.1：park + 恢复简报 + 传感器第一代）· 2026-09-22

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-22；立项 2026-09-21） |
| 触发 | dogfood/用户反馈——跨会话文件状态漂移（两条真实用户反馈） |
| 关联决策 | D13（动词三层纪律）、D14（传感器 fire 点与 finding 接口） |
| 测试基线 | 102 → 144 |
| 材料来源 | 原 integration-plan.md §7 Phase 3.1 + §9 2026-09-21、2026-09-22 晚/续（含 Node 可移植性追加）（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**触发**（真实用户反馈两条）：①长会话中开头读过的规则/spec 遗忘导致执行偏移；②流程中途新建会话要求"从上次结束的地方继续"后仍发生文件状态漂移（旧制品加载不完整、工作流偏移）。

**根因诊断**（全部代码考证）：路由层未漂（引擎是路由 SSOT），漂在执行层——①状态机粒度是阶段而中断发生在阶段内部，引擎对阶段内进度失明且中断不留痕（`current_stage` 无法区分"未开始"与"中断"，`cmd_status` 无子阶段信息；Unit Progress 预留未用；无收尾动词，中断不留痕，动词集仅 status/init/next/report/jump/rebase）；②恢复协议是"MANDATORY Load ALL"全量散文指令（session-continuity.md:38-57 平铺无优先级无验证，"Load ALL" 物理不可执行 → 模型抽样 → 偏移），且不读审计尾部（audit.md 这个恢复数据源未被使用）；③report 收单不验 produces、半成品无探测（pending 阶段 workspace 产物已存在时引擎沉默）。

**Trellis 对照调研**（2026-09-21，外部工作流框架，docs.trytrellis.app + 本地仓库全量考察）：同一哲学（"判断归 LLM、精确归工具、决定归人类"）的正交投影——我们把确定性押在阶段路由（契约+引擎），它押在状态保活与知识复利（per-turn breadcrumb 注入 + 活 spec 回写闭环）。对本次立项的直接馈赠：①park 是其 task.py 生命周期事件的成熟先例（"生命周期事件 ≠ 状态转移"）；②"必需步骤必须出现在模型必经通道"不变量；③"分析留在聊天里=零"的落盘纪律；④其自身删掉 worktree 管理的历史警示已并入 Phase 4 前置检查意识。其他可借鉴项（knowledge_refs 三代演进、反劝退表、成功度量清单等）记录于当日会话，供后续相位取用（后由 B05 四档清单正式收编）。

**定位**：park 与证据链均为 Phase 3 砍单在案项（B03 档案立项与裁决节——"服务的能力不在分叉范围内，可随时按防返工设计加回"），本次凭真实用户反馈**有据加回最小子集**：park（v2.0 orchestrate 五子命令之一）+ 证据链子集（missing-produces 探测），以传感器形态实现。

**新决策（已录入主文档决策登记表）**：

- **D13（动词三层纪律 + 注记转移不变律）**：引擎动词分三层——读（status/next，无副作用；stamp 于 B06 加入读层）；**转移（report/jump，封闭集合 = 唯二改变 marks/current 的动词，Phase 4/5 永不新增）**；生命周期（init/park/rebase；park 为注记子类）。"转移不变律"：注记动词必须保持 marks 与 current 不变（digest 重算不算转移）。Phase 4 的 claim/release 照此办理——实现为 report 的 additive guard（如 `report --unit` 校验 claim 归属），不新增转移动词。新动词入场券 = 与全部既有 mutating 动词的两两交互测试（交互矩阵自此为 CI 法定成本）。
- **D14（传感器 fire 点与 finding 接口）**：分叉侧传感器的 fire 点 = 引擎动词（status=恢复时 / report=收单时），永久不变（harness 无关性使然，区别于 v2.0 的 write hook）。finding 对象五字段 `{type, severity, subject, message, action_discipline}` 即 Phase 5 传感器接口；本批交付的 artifact_alerts 为第一代实现（硬编码 manifest），Phase 5 manifest 化时**须过输出等价测试**（固定夹具工作区，前后输出逐字节一致）。`type` 集合可增不可删；同一 state_version 内对象 shape 永不破坏性变更。

**方案演进与两轮审查**（全部发现均经逐条考证属实后消解）：

- 一轮（reviewer）：1🔴（传感器 produces 检查语义与 frontmatter 数据现实冲突——RA/B&T 条件产物、`{unit-name}` 占位）+ 6🟡（尾部读冗余、`_audit_events` 改元组砸 integrity、audit 收窄措辞冲突、D13 分类漏 init/rebase、三规格空洞、文档漏三处）+ 8🔵。裁决核心：缺失检查与存在检查采用**不对称语义**。
- 二轮（reviewer）：3🟡（①infra-design 唯一具体产物亦为条件产物+operations 空产物 → 定 **N≥2 且全缺才告警**通用规则，弃硬编码豁免表；②resumed 检查条目参与范围 → 定**全产物参与唯排除引擎自有文件**；③单次读实现二选一 → 写死**可选参数方案**，改返回值会致 `_require_intact` 对非 None 恒 raise、全部 mutating 命令 TypeError）+ 8🔵 + 4 建议（共享正则常量、新解析器限定 Engine Transition 节、violated 时 alerts 照常、terminology 词条——后随 B12 整删），全部采纳。
- 副作用治理（讨论定案）：审计膨胀→**账本分家**（park 记 handoff.md，audit.md 只收转移，天然有界；审计分段降级为 contingency，触发器 512KB/50ms）；Goodhart（告警变任务）→action_discipline 字段禁自行补写；fail-open 不可见→alerts_unavailable 标记；引擎角色扩张→D13/D14 把 ad-hoc 实现定性为"传感器第一代"而非透支（换心脏不换接口）。
- **既有 CTX checkpointing 扩展（opt-in）与新方案互补而非重复**：边界重压缩归 CTX-01 检查点、任意断点轻记号归 park、确定性探测与路由归引擎；CTX 三处修订并入实施清单（CTX-02 措辞对齐分级阅读、CTX-01×park 边界双写、CTX-03 归属澄清）。

## 规格

1. **`park` 动词**：`engine.py park --note "<断点描述>"`。门槛 `_load_active` + `_require_intact`；新增拒绝分支：工作流完成（current=None）→ 错误码 `workflow-complete`（文案对齐 jump 既有拒绝，engine.py:930-936 风格）。效果一：Current Status 区写 `- **Last Parked**: <slug> — <note>`（入 digest；marks/current 不动）。效果二：追加 `aidlc-docs/handoff.md`（懒创建、引擎独写、append-only、integrity 永不解析）——**审计分家**：park 不写 audit.md（转移账本天然有界，审计膨胀与 integrity 解析成本问题就此消解）。写序固定**先 region 后 handoff**（region 是权威源；崩溃窗口=handoff 缺一条历史，resume_note 不受影响）。去重：同 stage+同 note 与 handoff 尾条相同则跳过。note 卫生：必填、换行折叠 `; `、截断 300 字符。清除：`report`/`jump --stage`/`jump --fresh` 前置 `state.parked=None`（fresh 走初始模板天然无行）；`rebase` 保留可解析行。并发：last-writer-wins + handoff 双存，可接受；降级：旧引擎重渲静默丢弃该行、digest 自洽；`--fresh` 归档随 aidlc-docs 整目录——三者均记入契约 §5.5。
2. **region 与解析**：`_render_region_lines(..., parked)` 加参；`load_state` 解析 Last Parked 行 → `state.parked`；无该行 → parked=None → 重渲逐字节同旧格式；**STATE_VERSION 保持 1**。`_initial_state_text` 标记区外加两行读者须知（新会话先跑 status / 勿改标记区；仅覆盖新项目，入负债）。
3. **`status` 升级**（active 分支追加；none/legacy/corrupt 早退分支不携带新键，§10+golden 钉死；integrity=violated 时 alerts 照常计算输出）：
   - **audit 单次读**：`check_integrity` 增缺省参数 `audit_text=None`（缺省自读=现状；`_require_intact` 及 next/report/jump/park 零改动——改返回值方案已否决）。cmd_status 单次读入，供 integrity / recent_events / 计数三方复用。
   - `resume_note`：`{stage, note}` 或 null（region 行权威）。
   - `recent_events`：最近 5 条转移事件（不含 park），元素 `{event, stage, reason, timestamp}`。**新增独立解析函数**：逻辑限定在 `## Engine Transition` 节内（防用户原始输入伪造 Event 行——SKILL.md:571 允许原文入账），与既有 `_audit_events` **共享模块级正则常量**（消双解析器漂移面），后者三元组签名不动（integrity 路径零改动）；时间戳归属"节内最后见到的 Timestamp 归该 Event"，模型条目夹心场景测试锁定。
   - `audit_entries` / `audit_bytes` 计数（单次读顺带，零成本；为审计分段 contingency 提供 512KB/50ms 触发器度量）。
   - **artifact_alerts（不对称语义——缺失断言零误报，存在信号低成本）**：
     - 通用排除：引擎自有文件 `aidlc-state.md` / `audit.md` 不参与任何检查（init 保证存在、零信号价值；WD 阶段因此自然豁免）。
     - **missing-produces**（completed `[x]` 阶段）：N = 非通配具体产物数（`{unit-name}`/`*` 跳过）；**N≥2 且全部缺失/为空才告警**（列出全部路径）；N=0/1 豁免。依据（一轮审查 🔴-1 + 二轮 🟡-A 考证）：RA questions 条件创建、B&T 4/8 产物 As-Needed、infra-design 唯一具体产物 shared-infrastructure.md 亦条件产物、operations produces 为空、WD produces 恰为引擎文件——N=1 时"条件缺席"与"真没写"不可区分，语义鸿沟留待 gen-2 per-produce required。action_discipline: "Report to the user; do not regenerate or fabricate artifacts."（防 Goodhart）。
     - **resumed-artifacts**（current 阶段）：覆盖全部 produces 条目（引擎文件除外）；具体路径=退化 glob 精确存在；`{unit-name}` → `*` 翻译后 glob 展开；**任一匹配存在即告警**（封顶 5，message 注明可能是半成品）。存在信号=中断残留，误报代价低（"先读后写"恰为正确指引），且恰好覆盖 per-unit 阶段中断半成品。action_discipline: "Read existing files before writing; append rather than regenerate (unless in a rejected/revised redo — see session-continuity)."
     - 整体 fail-open：探测异常 → `alerts_unavailable: true` + 空数组（不响亮但可见）；写动词照旧 fail-loud。
4. **`report` 软警告**：completed/approved 时对当前阶段按 N≥2 全缺规则检查 → 输出 `produces_missing: [...]`，**转移照常成功**；检查本身 try/except fail-open（异常省略字段——绝不阻断唯一写入口，否则重试撞 invalid-transition）；rejected/revised/skipped 不查。软警告跑一个 dogfood 周期再议升级硬错误（**2026-09-24 已裁决：不升级，关闭**，见 B06 档案；fx991 三迭代[2026-09-27/28]零触发为追加佐证，累计 5 周期零信号，关闭时点不变，详见 B09 档案）。
5. **测试**（102 → 约 134）：ParkTests(~9)、StatusRecoveryTests(~10，含反误报六连与正例)、ReportWarningTests(2)、BackwardCompatTests(2)、InteractionMatrixTests(4)、GoldenOutputTests(~4)、CliTests(~2)。
6. **文档同步**（10 处）：engine-contract.md（§1 动词分类、§5.5 Park Semantics、§6 收窄措辞、§9 表、§10 样例）；session-continuity.md（恢复协议 v2：status→integrity→resume_note+recent_events→响应 alerts→分级阅读①引擎输出②required consumes③按需→增量续作；Park Ritual 含 CTX-01 边界双写；反劝退条；Welcome Back 模板加 Last parked 行）；checkpointing.md（CTX-02/CTX-03/文案）；checkpointing.opt-in.md（Session Resumption Trigger 段改写）；error-handling.md（"Missing Artifacts During Resumption" 节头定序交叉引用）；SKILL.md（bootstrap active 行补 resume_note；Park 触发规则；枚举补 park；Directory 树加 handoff.md；**运行时缺失指引**：engine 调用报 Python 缺失特征时停止重试，向用户转达需 Python 3.8+ 并给出平台安装命令——Windows `winget install Python.Python.3.12` 或 python.org 安装器、macOS `brew install python3` 或 `xcode-select --install`、Debian/Ubuntu `sudo apt install python3`——装好后重试；零代码，AI 即错误翻译层）；terminology.md（Park/Parked 词条，后随 B12 整删）；AGENTS.md（§3.1 动词列表+park+handoff.md；实施后测试数刷新）；README.md + README_cn.md（运行要求显式化）；integration-plan（决策表录 D13/D14 + 变更记录）。
7. **顺序与验证**：engine.py（region→park/handoff→status→report→头部→CLI/docstring）→ 全部测试全绿 → `generate.py --check` 零漂移（本相位不触 frontmatter/生成物）→ 文档按第 6 条清单 → 终验。
8. **不做（八项）**：per-unit missing 精确覆盖（Phase 4 Unit Progress）｜report 硬阻断｜审计分段实现（contingency）｜CTX 转正（维持两层：默认层确定薄/增强层智能厚）｜missing-produces 自动补写｜handoff 模型直读 API（resume_note 是唯一通道）｜per-produce required 标记（gen-2）｜存量项目头部须知迁移。
9. **负债清单（七条，backlog）**：①N=1 具体产物阶段豁免 missing-produces（gen-2 per-produce required 可解）②per-unit missing 精确覆盖依赖 Phase 4 Unit Progress（`{unit-name}` 逐单元展开）③report 软警告待 dogfood 后议升级——2026-09-24 已裁决关闭（新证据可重开，见 B06）④状态文件头部读者须知仅覆盖新项目⑤审计分段 contingency（触发器 512KB 或解析 50ms，度量=新计数字段）⑥未 park 且当前阶段零制品的中断不可探测（park 是自律层非传感器）⑦handoff.md 无模型直读 API。

## 实施与实施期裁决（2026-09-22）

主智能体实施引擎核心（engine.py 11 处耦合编辑：常量/正则 → State.parked 与 region 渲染/解析 → 审计双解析器 → check_integrity audit_text 复用 → 传感器三函数 → cmd_status 六新键 → cmd_report 软警告+清除 → cmd_park 全套 → CLI/docstring），冒烟验证后按"可分离工作分发 executor"原则四批并行：①测试套件（39 个新测试七类）②engine-contract.md ③session-continuity.md v2 + checkpointing×2 ④SKILL.md/terminology/error-handling/AGENTS.md/README×2（含运行时缺失指引）。全部经主智能体复核。

结果对照计划：测试 102 → **144**（计划"约 134"，超额因反误报正例细化）；文档同步 10 处全落（含当日新增的第 10 处 README×2）；D13/D14 已录入决策表；软警告/传感器 fail-open/审计分家（park 不入 audit）/写序 region→handoff/去重/清除矩阵全部按规格实现。executor 上报一处自主判断：engine-contract 中 audit 分段触发度量只写 512KB 未写"50ms"（本地无可考证实现，50ms 属负债⑤的解析耗时阈值构想，留待 contingency 实施时定）。

## 验证

`python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests` → Ran 144 tests OK；`python .agents\skills\aidlc-workflows\scripts\generate.py --check` → 零漂移；既有 102 测试零回归。

## 实施后审核与修复（2026-09-22，同日）

**审核**（reviewer 子代理，静态全量对照规格 1-9 条）：🔴 阻断 0；🟡 应修 3（①session-continuity 分级阅读第 2 层"required consumes"与生成地图同位语语义冲突——地图列的是各阶段自身 produces 而非 consumes；②workflow-changes.md §6 On Resume 残留"Read all artifacts from completed stages"全量加载旧指令（规格 10 处同步清单的漏网文件，本相位引入分级阅读后成为相抵指令）；③"WD fresh-init 无 resumed"反误报场景无测试承载）；🔵 建议 4。三个待验证主张裁决：A 部分证实（反误报覆盖确有空档，但写序 mock/金样两类强度充分）；B 证伪（当前 produces 无 `[`/`?` 条目，无现行缺陷；未来 frontmatter 引入时需 glob.escape——记入负债⑨）；C 证实且合理（50ms 属计划构想、仓库无实现可考，不写入契约正确）。

**修复**（全部落）：①tier 2 措辞改为"consumes 取自 next 指令；地图是上游产物的查阅地图，非加载清单"；②workflow-changes §6 Handling 补 Park 步骤、On Resume 改指分级阅读；③新增 test_fresh_init_has_no_resumed_alerts_for_engine_files（载荷测试：排除逻辑若被移除即红）+ none/legacy 键集钉死 + note 截断落盘断言；④动词计数改 7（规格原文"列全 8 个"系计划笔误——7 个子命令，非实施缺陷）；⑤早退分支措辞补 hint 说明；⑥AGENTS.md 决策区间改 D1-D14。测试 141 → 144 全绿，--check 零漂移。审核者环境无 shell，命令级验证由主智能体代跑并确认。

**负债清单追加**：⑨produces 若引入字面 `[`/`?` 字符，missing-produces（字面量判断）与 resumed-artifacts（glob 判断）将不一致——届时需 glob.escape 或显式字面量声明。

**第二轮审核（同日，reviewer 复审）**：裁决"修复轮通过，可作为提交依据"。新发现 1🟡+6🔵，全部当场修复：🟡AM-05 断点通道改指 park（原指 audit.md，与 CTX-03 相抵且恢复通道不覆盖）；🔵 workflow-conventions 时间戳枚举补 park、AGENTS.md Phase 3 条目改"当时 77 例，现累计 144"、规格就地注记 8→7 笔误、金样测试补 audit_bytes==文件字节数断言、session-continuity 早退指引改指 status hint+契约 §10、CliTests._run 委托 _run_main 消双实现。终态：144 全绿 + --check 零漂移。

**负债确认（七条不变）+ 新增一条**：⑧测试套件新增 `_run_main`/`make_doc`/`route_to` 等辅助（后续阶段测试可复用，但 route_to 依赖 plan-skip 语义，Phase 4 unit-major 时需复查）。

## 附注：运行时可移植性讨论（2026-09-22 晚，裁决 D6 不变）

担心部分用户环境无 Python，评估"脚本全量改写 Node"方案后**搁置**——macOS/Linux 默认自带 python3 不带 node（缺口互换不缩小）、Node LTS 版本窗远窄于 Python 3.8+、102 测试资产与 Phase 3 验收清零、且"真实用户被阻断"触发器未响。裁决：**D6 不变**，仅文档同步追加零代码兜底（SKILL.md 错误翻译规则 + README 双语运行要求一行）。若未来触发条件出现，正确路径是"先导出语言无关一致性测试向量，再单语言整体替换"，不做双实现并存。
