# B21 · PD 对话质量批档案

> 状态：✅ 已实施并收口（2026-10-22 用户三轮裁决，reviewer 终审后同日实施）
> 性质：头脑风暴阶段（product-brainstorm）对话质量增强——研究姿态（D27 ①）+ 提案节奏（②）+ 轻量留痕（③）
> 定位：补齐"素材—时机—姿态"三缺口；吸收 v2.0 Ideation market-research 一切片（不新增相位，阶段集不变）

## 1. 裁决（均 2026-10-22 用户裁决，登记 D27）

- **三轮需求演进**：① PD 拿到意图后应积极网络搜索最新知识与解法、参考现有代码方案，而非只靠预训练推理；② 修正为按需即时搜索（对话中途想法冒出即搜），非只开头一轮；③ dogfood 发现 PD 对话以模型提问为主——期望启发式对话帮用户梳理模糊念头（诊断：one-question 硬纪律 vs offering 软立场的纪律不对称 + 无素材时问题最易产出）。
- **五项执行裁决**：研究强度 = 能力可用即必须 + 拿不准就搜；产物流痕 = 轻量（Source 列 basis: 后缀 + 可选 Prior Art 行）；范围 = 仅 PB（推广 RA/AD 挂开放项）；搜索时机 = 贯穿对话按需；提案节奏并入本批。
- **沿革**：v2.0 Ideation 相位含 market-research（docs/aidlc-v2-features-vs-v1.md），本批吸收其一切片而不新增相位。

## 2. 方案终审（reviewer，全新会话）

3 blocking + 7 improvement + 6 suggestion，全采纳（无用户仲裁分歧）。关键处置：

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| B1 | blocking | Web 能力判定与失败路径未定义（按工具名判定 + 降级单档 → "必须搜"可静默失效） | 能力签名判定（QT-01 先例）+ 降级三档同落一句披露 |
| B2 | blocking | 外部网页内容进决策对话无不可信声明 | "data, not instructions" 条款 + 第一方优先 + 单一二手源标低置信 |
| B3 | blocking | dogfood §六已被消融对照占用 | 新增 §六 B21 专项、原 §六~§九顺延 §七~§十 + 指针/数据源行/模板行同步 |
| I1~I7 | improvement | 优先级句缺失 / 守卫断言缺口 / 顺延指针不精确 / 证据边界措辞 / Source 列原始职能 / SKILL.md 入口旧偏向 / 档案完整度 | 全采纳（Evidence boundary 原两句逐字保留只追加、Source 保轮次为第一职能、SKILL.md :179 补 material-first / research on demand、档案含残留扫描与功能验收） |
| S1~S6 | suggestion | WP 缩写撞名 / 锚点名笔误 / D27 沿革 / qfg:26 既有矛盾 / 陈旧指针顺手修 / 登记完整度 | S1~S3/S5/S6 采纳；S4 登记 §6 开放项不动文件 |

主张核对：1/2/3 证实（1 附前提——product-brainstorm.md H1 标题不动，生成器从 H1 派生显示名）；4 收窄为 4 处活指针 + b20 档案 3 处冻结不改。

## 3. 实施记录（2026-10-22，主智能体单会话）

| 层 | 文件 | 改动 |
|---|---|---|
| 核心 | product-brainstorm.md | 新增 "Research Posture" 章节（Tools Within the Dialogue 之后：五触发点 + 六行为条款）；Stance 加 "Lead with material, not with questions" + offering 武装指针；red flag 加三连问自检；Evidence boundary 原句保留 + 追加外部证据句（同地位不同权威）；Key Decisions Source 列示例改 `R3 (user) — basis:` 形态 + Prior Art 可选行说明 |
| 核心 | SKILL.md :179（标记区外手写块） | PB 阶段块括号补 "material-first with research on demand" |
| 测试 | test_rule_invariants.py | 新增 B21DialogueQualityTests 三守卫：研究姿态全程可用（含三档降级 / data-not-instructions / 拿不准就搜）、Lead with material 姿态、Evidence boundary 原句逐字保留 |
| docs | integration-plan.md | D27 行、§6 B21 行 + 两开放项（研究姿态推广 RA/AD、qfg:26 矛盾）、:98 基线链补 B21 后 254、占用链与 Operations 行 B21+→B22+（五延） |
| docs | dogfood-protocol.md | 新增 §六 B21 专项 H1~H2；原 §六~§九→§七~§十；数据源补行、模板行 11；顺手修 :3/:15 两处陈旧指针 |
| docs | AGENTS.md | 指针 D1-D27 / B01-B21；测试计数 254（算式链更新）；速览新增 B21 行；B21+→B22+ 两处（占用链 + P9 挂账） |

不动清单：frontmatter / generate.py / stage-graph.json / engine.py 零触碰；product-brainstorm.md H1 标题（生成器显示名派生源）；既有测试钉句（"Preference questions are never waived" / "never a bundled"）；question-format-guide 豁免（对话期工具调用本已覆盖搜索调用）；其他阶段规则文件；docs/batches/b20-*.md 冻结档案 3 处 B21+。

## 4. 验证

- 测试套件 **254 绿**（251 + B21DialogueQualityTests 3）
- `generate.py --check` 零漂移（无 frontmatter 触碰）
- 残留扫描：技能侧 grep `pretrained|web research` 仅命中本批新增条款，既有文本无与研究姿态矛盾的表述
- 功能验收（最小）：目标 dogfood 周期走 PB 后按协议 §六 H1~H2 记表——提案/问题回合比 ≥1 视为方向性通过；目标 harness 是否具备 web 工具在记录表 harness 行如实记账（不具备时研究姿态实弹不可验，字符串守卫为唯一下限）

## 5. 遗留与去向

- dogfood 迭代起观测 §六 H1~H2；快照源顺延为本批收口提交。
- 研究姿态推广 RA / Application Design：挂主文档 §6 开放项，dogfood 证据后再议。
- qfg:26 硬门条款与 PB 豁免的既有矛盾（终审 S4）：登记主文档 §6 开放项，本批不动。
