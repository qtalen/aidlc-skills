# B10 · AM 简化 + Code-Gen Hold 批（D17）· 2026-09-29

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-29） |
| 触发 | 用户需求演进（三轮收敛：加停点 → 去 Q2/AM-06 → 四项拍板） |
| 关联决策 | D17（修订 D16 的双问与暂停语义） |
| 测试基线 | 231（总数不变，1 例改名） |
| 材料来源 | 原 integration-plan.md §9 2026-09-29 当日条目（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**需求演进（用户驱动，三轮收敛）**：① 用户提出激活自主模式时增加一问——是否在代码生成阶段前暂停（方便切换到快速模型做实施），选是则停一次、说"继续"后一路到本轮完成；② 期间用户询问 Q2（审核阶段多选）来历（考古：审核阶段能力初始导入批即有、藏于暂停菜单 Option B，D16 重写 AM-05 废除菜单后才迁入激活流成为必问项）后裁决**完全去除 Q2/AM-06**——人工把关改由"随时暂停"承担：暂停/停止自主模式 → 工作流继续执行到下一个审批门等人工，直到本轮结束全部人工审批、不自动恢复，除非显式重启；③ 四项实施拍板：停点纯模型侧 / 暂停时优雅完成手头工作再停 / 引擎 review_stages 死字段一并移除 / 停点问题每次激活全新问不预选。

**语义终态**：
- **激活** = 双问（Q1 问题处理方式 + Q2 代码生成前停点，**均每次全新问，任何持久化值不作预选**）；AM 期间全阶段自动批准（AM-03 无审核阶段例外）。（Q1 后由 B11[D18] 移除——激活单问，见 B11 档案。）
- **暂停/停止（AM-05 二次重写）** = 模式关闭 + 优雅完成手头工作（到一致状态、不启动超出门的新工作）+ 标准模式继续到下一个审批门（当前阶段自己的完成门，或其后的首个门；含 per-unit 段门；非门阶段照常跨过）+ 挂起的 AM-04 升级问题按标准流程继续 + 直到本轮结束不自动恢复，仅显式 Activate 重激活（全新 AM-02）；调整菜单删除。优先级消歧：AM 激活期 Pause 走 AM-05 而非 Park Ritual；显式"停下"是 Park（模式不动，AM-09 续接）；组合意图（立即停+暂停）= park + 翻转搭车、优雅条款豁免。
- **Code-Gen Hold（AM-11 新增）** = 布防条件"code-gen 工作尚未开始"（含激活时已在当前阶段但未开工的子情形——堵计划审核轮发现的触发空洞：引擎 `remaining` 含当前阶段，若不设此条件 Pending 会悬空、AM-09 恢复条款会在开工后中途停住）；触发三路径（转移到达[优先于 AM-03 的 immediately begin] / 激活即呈现 / 续接重呈现）；放行 = 继续语义 → Pending→Passed + 刷 Last Updated + 审计；其他答复按意图处理后**仍等继续语义**；每次激活最多一次（重激活可在窗口开放时重新布防；backward redo 不重触发）；非 Pause 非 park，模式穿越停点保持开启直到本轮完成。
- **AM-07** 缩为 AM-05 的等价入口（退出/关闭词汇）+ 保留"auto-approved 阶段重审走正常变更请求"。

**计划审核（reviewer，实施前）**：2 阻断 + 10 建议 + 3 存疑全处置（计数沿用当时 AGENTS.md 路线图行的登记）。阻断=清单漏 engine-illustrated.md / AM-11 触发空洞（布防条件由此而来）。

## 实施

主智能体重写 autonomous-mode.md（索引[AM-06 tombstone + AM-11 行]、AM-01 触发表 Pause 行 + 优先级注、AM-02 双问[Q2 含换模型理由/跳过条件/无预选]、AM-03 全阶段 + AM-11 优先、AM-05 优雅暂停六点、AM-06 退役节、AM-07 缩写、AM-08 模板换行 + Code-Gen Hold 四态语义 + 窄写窗口措辞类别化、AM-09 宣告含停点 + 停点等待态重呈现、AM-10 措辞 + 全量重问条款、AM-11 全文、Enforcement 表）+ 外围 6 文件（opt-in 区间、session-continuity 三处、workflow-conventions 两处、code-generation.md Prerequisites 后 AM-11 提示行、engine-contract §10、dogfood-protocol 度量 3 措辞）；executor 后台并行删代码三簇（engine.py `_parse_autonomous` -9 行、test_engine.py 3 处[1 例改名、整字典断言 3 键、删字段断言；fixture 的 Review Stages 行保留以钉死宽忽略]、generate.py stage-names 三处[MARKERS/render/render_map]）+ stage-contract 宿主清单去 autonomous-mode + engine-illustrated.md 行号锚点对账。

**取代登记**：原 Phase 3 规格行项 22（AM-06.6 slug 对齐）作废；Phase 4"AM 注记化"的 slug 校验子项作废、剩余范围收窄（显式动词 / digest 覆盖 / per-claim 并发语义；Code-Gen Hold 通道收编时评估）；D16 的"审核阶段预选旧值"条款废止。

## 验证

unittest 231 全绿（无增删，1 例改名）；`generate.py` 重新生成 + `--check` 零漂移；sweep——功能性引用（读/用 Review Stages 的规则文字）零命中：模式串 `Review Stages|review_stages|stage-names|non-review` 在技能树 .md 仅 2 处移除/遗留注记；`AM-06` 4 处退役注记；`preselect` 3 处全否定句；engine-illustrated 引用对账（executor 报告 17 处，审核轮全数独立复核）。

## 实施后审核与修复（reviewer，同日）

裁决"**无阻断项**"——四项用户裁决与计划审核轮全部处置落地、引擎/契约/测试三方一致、engine-illustrated 17 处锚点独立重定位全验（恰 -9 位移）、B2 修复三路径核实、测试静态计数 231 精确复现（154+22+55）、16 键/渲染器一一对应零 orphan 标记。5 条发现全采纳当场修复：🟡① AGENTS.md:24 生成块宿主清单第二份拷贝漏同步；🟡② sweep 计数口径含混（已分列）；存疑三项裁量落地——③ AM-02/AM-08 自定义停点答复落盘口径统一为 **verbatim 写入状态行**（枚举外加 `[verbatim custom hold instruction]`；AM-11 触发仅认 `Pending`，自定义变体按记录意图生效且跨会话存活）；④ 过期翻转对未知行的保留补 1 行断言钉死；⑤ 索引 AM-07 词汇分工修正（exit/turn-off）。验证边界（审核者标注）：无 git diff 能力的三项以静态一致性与主智能体实跑代验。
