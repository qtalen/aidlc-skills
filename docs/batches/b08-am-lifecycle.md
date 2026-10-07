# B08 · AM 生命周期批（D16：自主模式绑定工作流轮次）· 2026-09-28

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-28，含同日三轮审核） |
| 触发 | dogfood 反馈——AM"开启一次、代代相传"持久化缺陷 |
| 关联决策 | D16 |
| 测试基线 | 209 → 227（AutonomousExpiryTests 18 例） |
| 材料来源 | 原 integration-plan.md §9 2026-09-28 其二（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**背景与需求（用户）**：dogfood 实证 AM 持久化缺陷——`## Autonomous Mode` 区的 `Enabled: Yes` 在工作流完成后无人翻转，下一迭代（再入/新会话）经 opt-in stub 条件 2 与 AM-09 无询问地恢复 AM 并**沿用旧 question_handling**。期望语义：AM 持续到当前工作流完成或用户显式停止；新迭代默认关闭；重新开启必须重问配置。

**三项用户裁决**：① 过期动作放**引擎侧**（完成转移确定性翻转，不依赖模型合规——"精确归工具"哲学的直接应用）；② 存量自愈放在**再入 jump 分支**一并翻转（覆盖"已完成 + Yes"旧工作区）；③ **暂停即彻底关闭**（恢复需全新 AM-02 重问，废除"挂起可恢复"旧语义）。

**实施前计划审核（reviewer）**：三条待验证主张全部证实。三个阻断项及处置：
- **B1 自复活路径绕过**：workflow-changes.md:16 官方指引"计划行先改 → status 自行复活 → 勿 jump 直接 next"（B07 审核轮专门修正过的次序指引）不经任何转移动词，两个引擎翻转点都不触发。裁决=**模型侧兜底**（AM-10 要求任何方式开启新轮前确保 Enabled: No，模型翻转+审计；不改次序指引，不接受残余风险）。
- **B2 与 Phase 4 移出项张力**："不做"清单曾以"避免 engine-contract 改两次"为由将 AM 专用动词整体移 Phase 4。处置：本批定位为止血窄写（两边界幂等翻转，无新动词/digest/并发），收编路径与剩余范围补记至 Phase 4 设计输入第 1 条；接受契约 §6 二次修订，理由=当下用户痛点优先。
- **B3 残留引用清单**：AM-04 custom 模式 "pause per AM-05"、AM-07 "AM-05 menu Option C"、索引 AM-05 描述、opt-in "AM-01~AM-09"、AM-02 step 4 写死 "Review Stages: None"——全部入实施清单。

## 实施（4 路并行 executor，文件互不重叠）

1. **引擎**（engine.py）：`_expire_autonomous(lines, timestamp)` 宽容翻转（凡解析为 enabled 的行[大小写不敏感]置 No + 既存非空 Last Updated 更新，缺失不添加；区缺失/畸形/已 No → no-op）挂入 `cmd_report`（`new_current is None` 时，写前应用、搭车既有原子写）与 `cmd_jump` 再入分支；ack `autonomous_expired: true` 仅实际翻转时携带；完成转移与 STAGE_JUMPED 审计条目附 detail（EV_FRESH 先例，不新增条目类型）；区头横幅与 `_parse_autonomous` docstring 所有权表述同步。
2. **契约**（engine-contract.md §5/§6/§8/§9/§10）：§6 新增"AM-10 narrow write window——唯一引擎写模型区"条款（**触发互斥=纪律约定非机制保证**：区不在 digest、无锁、多会话并发仍属 Phase 4 开放问题）；§10 `autonomous` 键补"completed 态报 enabled:false，存量 Yes 在再入时自愈"。
3. **AM 规则**（autonomous-mode.md + opt-in）：新增 **AM-10**（三边界：completion=引擎翻转+closing summary 宣告 / re-entry=jump 翻转+自复活路径模型兜底 / fresh=归档即消失；过期后规则休眠；重启=全新 AM-02，持久化旧值仅作预选参考绝不静默复用；同轮内跨会话保持不变[AM-09]）；**AM-05 重写**（暂停=彻底关闭；原 A/B/C/D 菜单废止）；**AM-02 双问**（问题处理方式 + 审核阶段多选**预选**当前列表）；Review Stages 编辑入口迁至激活流+轮内用户显式请求；AM-04 两处单题升级；AM-08 补引擎写窗口；AM-09 插入 completed=expired 条；`stage-names` 生成块随迁 AM-02。
4. **外围**（4 文件 7 处）：session-continuity、SKILL.md、workflow-conventions、workflow-changes。

（注：AM-02 双问/预选/Review Stages 等条款后被 B10[D17]、B11[D18] 连续修订——AM 激活语义现状见主文档决策登记 D17/D18，原文此处保留本批时点事实。）

## 验证

全量 unittest 224 例全绿（209 基线 + AutonomousExpiryTests 15 例）；`generate.py --check` 零漂移；全树 grep 陈旧引用零命中。reviewer 三条规格歧义钉死：翻转匹配=解析语义（大小写不敏感）非精确字符串；无操作时 ack **无**字段；审计 detail 与 ack 同条件。

**语义净效果**（验收口径）：新轮起点 status 报 `autonomous.enabled=false` → stub 不加载规则，标准模式；"开启自主模式"必经一次结构化双问；生效范围恰好覆盖当前轮，轮次终点由引擎确定性收口；completed 空档期激活在再入时被引擎过期（AM-02 宣告已警示）。

**与既有决策/批次的关系**：D13 动词封闭集不动（过期是 report/jump 转移的确定性副作用，非新动词）；D14 fire 点不动（status 保持纯读）；D15 再入语义增强（翻转搭车）；B13 备份批测试基线随本批对齐。

## 实施后审核与修复（同日两轮）

**二轮实施审核（reviewer）**：静态等价核验 + 逐字节比对 + 正则扫描。发现并已修复：
- **B-1 前向 jump 完成漏触（阻断）**：前向 jump 越界终末目标可把活跃工作流置为 completed（中间体标 [S]），但挂钩条件 `current is None` 为假 → AM 不翻转，与再入分支不对称。修复=挂钩条件放宽为 `current is None or new_current is None`（"跳转后处于完成态"即轮次边界），审计注记分流（re-entry / jump completed the round），补测试 `test_forward_jump_completing_round_expires`。
- 加固：`_expire_autonomous` 第二趟扫描显式复位 `in_section`；AM-10"预选"范围修正（仅 Review Stages 预选，Question Handling 永远重问）。
- 文档失步修正：AGENTS.md 决策区间 D1-D15→D1-D16、活指针 209→226；B13 批规格内 engine.py 行号失效→函数名引用。
- 审核建议① 的原断言假设有误（越界再入用例结束态实为 active 而非 completed），按实际语义钉死。
- 测试 209→226（AutonomousExpiryTests 15→17 例）。

**三轮终审（reviewer）**：对二轮修复本体判定"运行时无缺陷"——jump 分支 × (current, new_current) 取值矩阵独立推导证实挂钩条件恰好覆盖"跳转前/后处于完成态"两支、无过度触达与漏触。发现并已修复：契约 **§6 窄写窗口条款残留"两边界"枚举**（与同文件 §8 相抵）→ 改类别表述（"完成工作流的转移[完成 report 或使工作流完成的 jump]＋再入 jump"两类边界）；engine.py 区头注释与测试类 docstring 两处同步残留；§9 jump 行摘要对齐 §10 措辞；补 (再入, 保持完成态) 矩阵格用例。存疑待议项（AM-08/AGENTS/D16 的类别级"两边界"措辞）经 D13 术语考证判为可接受，不改。测试 209→**227**（AutonomousExpiryTests 18 例）。

## 遗留与去向

本批为止血窄写；通解（显式动词覆盖全部切换路径 / digest 覆盖 / slug 校验 / per-claim 并发语义）仍留 Phase 4 收编（见主文档路线图 Phase 4 设计输入第 1 条；slug 校验子项后随 B10 的 AM-06 移除而作废）。
