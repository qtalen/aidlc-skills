# B22 · load-on-execute 与 PB 瘦身批档案

> 状态：✅ 已实施并收口（2026-10-22 用户裁决惰性加载变体，reviewer 终审后同日实施）
> 性质：PD token 减负——CONDITIONAL 阶段判据先行/判 skip 零加载（D28 ①）+ PB 规则文件瘦身（②）
> 定位：收益窗口 = scope 选定前的 CONDITIONAL 阶段（ chiefly PB 22KB）；post-RA 阶段引擎已剪枝，本批对其为语义统一

## 1. 裁决（均 2026-10-22 用户裁决，登记 D28）

- **需求演进**：PB 阶段 token 消耗过大 → 三路方案（A 文本瘦身 / B 惰性加载 / C 压轮数）——用户裁：C 不上、A 做、B 用自定义变体（load-on-execute：判定执行才加载，判 skip 不加载）。
- **落点裁决**：逐一修改全部 CONDITIONAL 块（用户提出，理由 = 锚点透镜：就近指令赢过远处指令，消除块内 "Load ... and execute" 竞争文本比依赖全局句覆盖可靠）。
- **讨论期补丁**：uncertain→execute 裁决原住 PB 文件 Opening 节，判 skip 不加载后判定现场读不到——镜像至 Loop 契约句与 PB 块（判定时需要的规则住在判定现场）。
- dogfood 观测项随批（后经终审 I4 改为新开 §七 专项 L1/L2，非塞入 §六）。

## 2. 方案终审（reviewer，全新会话）

4 blocking + 9 improvement + 4 suggestion，全采纳。**两处前提证伪订正**（主智能体复核确认）：主张 3 证伪——引擎 `effective_stages()` 已做 plan-skip + scope-SKIP 双重剪枝（engine.py:686-697 + test_engine 锁定），"scope-skip 轮 emit 后 report"仅存在于 scope 选定前（RA 之前）；主张 1 后半证伪——除 PB 外各块只有判据指针无判据文本。关键处置：

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| B1 | blocking | 引擎已剪枝，方案收益窗口错判；integration-plan:210 登记陈旧 | 窗口收窄为 PB/RE/US；:210 划销关闭 |
| B2 | blocking | 9 个非 PB 块零加载后无判据可判 | PB 补 skip 侧全摘要、US 补单行摘要、RE 凭块内 Brownfield Only；AD/UG/per-unit/Operations 回退措辞（判据清单不在上下文可加载文件判定） |
| B3 | blocking | CG 是 ALWAYS（引擎拒 skip），块清单错一格 | 清单改 9 CONDITIONAL + Operations；守卫加 CG 反向断言 |
| B4 | blocking | 零加载消掉 PB 开场宣告，用户失去异议通道 | skip 一行可见告知（PB 版邀请召回），再 report |
| I1~I9 | improvement | 瘦身目标不现实（冻结语义下 ~20.5KB 而非 18）/ 计数守卫弱改逐块 + 反向断言 / 登记漏点（AGENTS 双指针、占用链两处）/ H3 改新开 B22 专项节 / "十句"实为 13 断言以测试类为准 / SKILL.md:25 顶层 MUST READ 竞争指令 / per-unit 判定覆盖整 loop / qfg 本就常驻改措辞 / stage-contract:54 补括注 | 全采纳 |
| S1~S4 | suggestion | 常驻净增披露（"压到最短"）/ 价值框架诚实化 / 清单重命名 / RA 兜底覆盖缺口挂账 | 全采纳（S1 落为实施期一轮收紧 + 档案字节账） |

主张核对：1 前半证实后半证伪；2/4/5/6/7/9/10 证实（9 字节数后经实测确认；10 覆盖面窄于方案所述并挂账）；3 证伪；8 部分证实（"十句"订正为 13 断言）。

## 3. 实施记录（2026-10-22，主智能体单会话）

| 层 | 文件 | 改动 |
|---|---|---|
| 核心 | SKILL.md | :25 顶层 MUST READ 补条件半句；Loop:125 run-stage 加 CONDITIONAL 判据句（judge first / skip 零加载 / uncertain→执行 / 一行告知）；10 块逐一改（RE/PB/US 判据摘要进块，AD/UG 回退措辞，per-unit 四块加整 unit loop 限定，Operations 补零加载括注）；实施期按 S1 收紧一轮 |
| 核心 | engine-contract.md | §4 run-stage 行同步判据句；:24 段补判定不加载/uncertain 语义 |
| 核心 | stage-contract.md | condition 字段行补"正文可省略重述"括注 |
| 语义 | product-brainstorm.md | 删 Execute when/Skip when 段（判据外置 SKILL 块）；uncertain 原句改指针；red flags 判别式化；Stance 四 bullet 与 Opening/Write-back/scaffold 尾注去冗；Tools 节补加载卫生句（common 规则已在上下文、勿载其他阶段文件/勿重读）；22,090→21,511B |
| 测试 | test_rule_invariants.py | 新增 B22LazyLoadTests 三守卫：逐块共现（10 块 × "without loading the stage file" + uncertain 分档）/ CG 反向断言 / Loop-engine-contract 双文件同步 |
| docs | integration-plan.md | D28 行、§6 B22 行 + 两开放项（RA 兜底缺口、SKILL.md 减脂）、基线链 257、占用链六延（→B23+）、:210 划销 |
| docs | dogfood-protocol.md | 新增 §七 B22 专项 L1~L2；原 §七~§十→§八~§十一；数据源补行、模板行 12；§零/§一 指针同步 |
| docs | AGENTS.md | 指针 D1-D28 / B01-B22（:5 与 :15 双位置）；测试计数 257；速览 B22 行；占用链 + P9 挂账 →B23+ |

不动清单：frontmatter / generate.py / stage-graph.json / engine.py；全部既有钉句逐字不动（B21DialogueQualityTests 13 断言 + "Preference questions are never waived" + "never a bundled"，既有测试零改动）；迭代再入结构性不加载 PB 为既有事实（jump 直落 RA），非本批功劳。

## 4. 验证

- 测试套件 **257 绿**（254 + B22LazyLoadTests 3）；`generate.py --check` 零漂移（SKILL.md 编辑均在生成标记区外）。
- 字节账（诚实披露）：PB 22,090→21,511B（−579B，含新增卫生句毛重）；SKILL.md 28,643→31,145B（+2,502B 常驻，已按"压到最短"收紧一轮）。净效果：skip 轮省 PB 全文件加载 + 后续轮驻留（按 30 轮会话估 ~660KB 计费量级）；PB 执行会话与非 PB 会话每轮多付 ~2.5KB 常驻——**token 价值集中于 skip 轮触发时**，L1 观测将给出实际触发频率。
- 功能验收（最小）：dogfood §七 L1~L2；audit STAGE_SKIPPED + 会话记录双核对。

## 5. 遗留与去向

- dogfood 迭代起观测 §七 L1~L2；快照源顺延为本批收口提交。
- RA 兜底覆盖缺口（具体但非产品形状请求误跳无回声）：挂 §6 开放项（B22 终审 S4）。
- SKILL.md 减脂（常驻 31.1KB 为每轮成本大头）：挂 §6 开放项，待 dogfood token 数据定优先级。
- qfg:26 硬门条款与 PB 豁免矛盾（B21 终审 S4 遗留）：仍开放。
