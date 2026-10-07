# B09 · 收尾小批（fx991 三迭代 dogfood 收官）· 2026-09-28

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-28，规格经 reviewer 独立审核收口后实施） |
| 触发 | dogfood 验收——fx991 三迭代（2026-09-27~28）收官登记 + 验收产物修复项 |
| 关联决策 | — |
| 测试基线 | 227 → 231 |
| 材料来源 | 原 integration-plan.md §9 2026-09-28 其三（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 前置：fx991 三迭代 dogfood 验收登记

（记录与证据包：`docs/dogfood-records/fx991-calculator/`，本地保留不入 git）

- **D15 闭环端到端验证通过**：迭代 2（旧快照 89f81cc）新会话复现"completed → jump --fresh"四环链路（归档迭代 1 文档树 + 重跑逆向工程 + 编号连续仅靠模型自觉读归档维持）→ 本仓库 D15 修复（`42302f1`）→ 技能快照同步至 dogfood 项目（`18559bf`，与源字节级一致）→ 迭代 3 新会话正确选择原地重入 `jump --stage requirements-analysis`（audit 记 "from complete (backward); re-entry"、RE 未重跑、FR-6/US-12 续编、无新归档树）。fresh 与 re-entry 形成干净 A/B 对照，D15 所消除的三项代价均有实证。
- **六度量三周期要点**：重复解释 ~0（AM-04 自答 + 逆向产物复用）；PRD 清晰度递升但"组合行为盲区"连续两迭代复发（迭代 2 DEL×Ans 交付后实测 bug、迭代 3 DEL×幂后缀未显式声明靠实现侥幸未炸）；重复评审恒 0（AM 配置结果，无信息量）；换工具零样本；新人独立完成两迭代连续近似观测成立（仅凭 status 探针正确路由）；RCA 累计 8 例、沉淀 0（Phase 5A 未落地）。
- **produces_missing 升级议题**：关闭时点不变（2026-09-24 裁决，见 B06），本三迭代零触发为追加佐证，累计 5 周期零信号；后续周期验收时抽样复核即可，不再逐周期写专项回填行。
- **自主模式跨轮持续观察已被 D16 消解**（B08 的触发证据即此观察——迭代 2/3 新会话沿用上轮 AM 配置），不重复登记。
- **观察项登记**：① Phase 5A rollup 首批实证（stories.md 达 356 行/6 个全量 Gherkin 故事，已过 300 行阈值且未维护 DOC-06 导航索引；requirements.md 出现自发 rollup——已交付 FR 压为一行摘要 + git 提交指针 + 编号永久保留；两制品不对等提示 rollup 策略需按制品类型分治）→ 见主文档路线图 Phase 5A 观察项；② CTX 检查点三周期"产出未消费"（消费场景=跨会话恢复始终未出现；唯一实际用途是 executor 交接底稿）→ Phase 4 CTX 终裁输入；③ 首次多 executor 并发实施一次通过（文件级互斥 + 接口契约由计划固定）→ Phase 4 契约先行模式的正向先例；④ WinError 5 环境事件（IDE 句柄占用 aidlc-docs）→ error-handling 补条目为低优候选，暂不动；⑤ audit 引擎 append 动词（机械保障模型写条目的 append-only；D13 交互矩阵成本，Phase 4/5 输入）。

## 立项与裁决（收尾小批四项）

1. **Depth 行值纯净双侧修复**：引擎 `_parse_plan` 新增 `_strip_inline_note`（首个半/全角括号截断）仅用于 Depth 分支（Scope 保持粘连注解 plan-invalid 硬阻断 + hint，"机器可校验项从严"）；`requirements-analysis.md` Step 2.5 模板行改裸值（原括号引导是注解诱因，dogfood 三迭代两次实录 `standard（scope` 截断）；`engine.py` init 模板改裸枚举占位；`workflow-planning.md` Step 8 补值纯净规则；契约 §6 格式注精确化（Depth 剥除从宽 / Scope 不剥除：粘连注解硬阻断、空白分隔尾注静默丢弃）。+4 测试。
2. **AUD-05 追加纪律**：workflow-conventions Group 3 更名 "Audit Discipline" + 新增 AUD-05（新条目锚定文末单次追加，禁以既有标题行为编辑锚点；依据=迭代 3 三次标题锚点失误均同交互自愈留痕，此依据留本档案不进技能文件——DOC-05 边界）+ 概览行/映射表同步；SKILL.md 同步一行。
3. **组合边界检查项（普适）**：requirements-analysis.md Step 7 加一条——凡引入新交互/行为维度（新输入 token/实体类、按键/命令/手势、状态或转移、数据实体、外部接口），必须对每项既有横切行为（编辑/删除、重置/清空、错误处理与恢复、结果态/空闲态续算、撤销重做、持久化）的组合边界逐项声明——被 FR 覆盖（或注明由后续故事的 AC 承担）或显式声明范围外并给理由；对新项目与再入迭代同构生效（连续两迭代复发的唯一真实产品缺陷类别）。
4. **dogfood-protocol 泛化 + 登记**：协议 produces_missing 关闭表述 + 度量 3/4 在 AM/单 harness 周期记 N/A + 决策回填行泛化；integration-plan 登记（引用纪律两类分治、两处失联引用标注已佚、Phase 5A 首批实证）；AGENTS.md 测试数 227→231 + 路线图行。

## 实施

WP-1 主智能体直做（引擎+契约+RA 双点+测试，引擎多耦合），WP-2 与 WP-4+5 两 executor 并行（文件互不重叠），主智能体逐 diff 复核通过。executor 执行裁决两处记录在案：文内引号按文件实际直引号处理（简报弯引号假设有误）；协议 :3 保留"软警告是否升级"字样属 NEW 文本自身的关闭表述，非残留。

## 验证

测试 227→**231** 全绿（+4 例）；`generate.py --check` 零漂移（零 frontmatter 改动）；冒烟——临时目录 `init` 后填 `standard（scope 默认）`，`status` 报 `depth: "standard"`（修复前截断为 `standard（scope`）；sweep 全过——`Audit Attribution` 全树零命中、教注模板清零（`scope default` 剩 4 处均为有意保留）、AGENTS.md 活指针 227 清零、协议"待裁决"专项措辞清零、失联引用均已标注"已佚"。

## 实施后审核与修复（reviewer，2026-09-29，两轮）

**首轮**：裁决"**可作为提交依据**"（0🔴/3🟡/3🔵；8 条待验证主张全证实）。发现全部当场修复：🟡① engine-illustrated.md 行号锚点失步——正文内联引用与附 A 全表刷新、补 `_strip_inline_note` 与 `_expire_autonomous` 两行、头注与附 B 测试数同步；🟡② B13 备份批基线"227→228"与本批落地后状态矛盾→改 231→232 并指向本档案；🟡③ B3"由后续故事 AC 承担"分支在 user-stories 被 SKIP 的 scope 下悬空→重排为"被 FR 覆盖或显式声明范围外并给理由；仅当 user stories 在计划内才可显式推迟到后续故事的 AC"；🔵 RA 禁令理由句与修复后行为不同步；🔵 旧 §8（原参考文件索引）SKILL.md 行数 620→631；🔵 旧 §7（原排期节）RA 行号引用改语义锚点。

**修复轮复审**：六项发现逐项验收——5 项修复完整、1 项主诉完整；engine-illustrated 全部 37 处引用逐一对账无一漏改取错。新发现 1 条 🔵（RA/WP 对 Scope 的简化表述漏"空格分隔尾注静默丢弃"分支）——已当场修复：RA 与 WP 两处均补全三分支表述，与契约 §6 完全对齐。终态裁决：**可作为提交依据**。

## 遗留与去向

B13 备份遗产清理批仍待实施，engine.py 改动点不同函数（`_parse_plan` vs `_stage_resumed_artifacts`）零冲突可串行；其测试基线随本批落地后为 231→232，实施时对齐（后又随 B12 收尾批变为 237→238）。
