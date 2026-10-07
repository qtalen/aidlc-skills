# B11 · AM 提问零配置批（D18）· 2026-09-29

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-29） |
| 触发 | 用户裁决——"Q1 也不需要问了，默认就是自动选择推荐的问题"（D17 简化的延续） |
| 关联决策 | D18（取代 D17 双问表述及 D16"问题处理方式"半句） |
| 测试基线 | 231（总数不变） |
| 材料来源 | 原 integration-plan.md §9 2026-09-29 其二（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**需求**：激活提问进一步收敛为**单问**（仅代码生成前停点）；问题处理方式不再询问，**固定 auto-recommended**。

**语义终态**：激活 = 单问（停点，每次全新问）；宣告语补"问题将自动选推荐答案"；AM-04 固定行为化（删 `Mode manual` 与 `Custom (Other) mode` 两节，保留 6 点含升级路径；新增"轮内显式指示按意图办理、不改配置不改状态"出口句，措辞可容纳持续性指示）；状态区三行制（Enabled/Code-Gen Hold/Last Updated）；引擎 `autonomous` 键 `{enabled, last_updated}`（宽忽略 legacy Question Handling / Review Stages 行）；人工干预问题出口 = AM-04.6 升级 + 轮内显式指示 + AM-05/07 暂停接管。

**计划审核（reviewer，实施前）**：1 阻断 + 6 建议 + 2 存疑全采纳。阻断=改动清单漏 3 处编号残留（autonomous-mode :46 "TWO questions"、:178/:180 AM-11 的 "AM-02 Question 2" 引用）且清扫串有盲区——修补=补入清单 + 清扫扩展（`Question 2|TWO questions|two questions|both activation questions` + `question[- ]handling` 大小写不敏感全形态 + 裸 manual 收窄为 `Mode \`manual\`|manual/custom|vs \`manual\``）。建议落地：session-continuity 目标措辞写全；AM-04 指示句容纳持续性指示；workflow-conventions 加 AM-04.6 豁免子句；assertNotIn 对称化；登记点名 D16 半句取代；AM-02 内部四点显式枚举改写。存疑两项内容：① 运行类验证边界（unittest/--check 实跑门由主智能体执行）；② 实施清扫的预期残留清单（即验证段白名单）。审核方另给出 engine-illustrated 17 处锚点精确映射直供实施简报。

## 实施

主智能体 autonomous-mode.md 14 处（Overview、索引 ×2、AM-02 单问重构、AM-04 固定化、AM-05、AM-08 模板 ×2 + 键说明、AM-09、AM-10 ×2、AM-11 ×2）+ 外围 3 文件（session-continuity ×3、workflow-conventions ×1、engine-contract §10 键定型 + legacy 示例扩展）；executor 后台并行代码簇（engine.py `_parse_autonomous` -4 行、test_engine.py 3 处断言 [整字典 2 键 / 两处 assertNotIn；夹具 5 处保留钉宽忽略]、engine-illustrated 17 锚点）。

## 验证

unittest 231 全绿（总数不变；一次中间运行 `test_drift_detected_in_temp_copy` 以 0xC0000374[Windows 子进程堆损坏] 失败，隔离运行与全套复跑均过，裁决为瞬时环境抖动——该测试复制技能树跑 generate.py 子进程，generate.py 本批零改动，无因果面）；`--check` 零漂移（本批不触生成体系）；清扫按扩展口径执行，预期残留白名单（逐条说明非残留）：AM-04 节标题与索引行（描述性保留）、契约 §10 legacy 示例（本批有意保留/新增）、5 处测试夹具（钉宽忽略）、question-format-guide :83/:292/:353 与 resiliency-baseline :195（题面模板标题/自文档引用，非 AM）、历史条目（惯例不改）。

## 实施后审核与修复（reviewer，同日）

方法升级——以 GitHub 远端 HEAD（67fa8da，与本地一致）为前基对 9 文件做**等效真实 diff 对账**。发现并已修复 **1 项阻断**：本批档案原插入点拆开了 D17 条目（D17 的"实施后审核"段被挂在 D18 标题之下，且其"3 键/-9 位移"等时点事实会误挂 D18 名下）→ 纯移动归位。其余全部通过：6 项主张证实（含瞬时抖动裁决推理成立）、计划审核 9 项修补全部落地、用户裁决 3 项落地（manual/custom 删除无语义孤儿，三出口闭环）、engine-illustrated 17 锚点双侧对账零偏差、231 静态精确复现（154+22+55）、扩展口径清扫与白名单一致。
