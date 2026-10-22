# B20 · 规则层精简批档案

> 状态：✅ 已实施并收口（2026-10-21 用户裁决立项，10-22 单会话实施）
> 性质：规则层精简——APG 审批门规则退役（D25）+ DOC 瘦身与合规只报例外（D26）
> 定位：B19 审查接线后的交互与 token 减负；APG 属 v1.0 基座遗产，本批为其终局

## 1. 裁决（均 2026-10-21 用户裁决，登记于主文档决策总账）

- **D25 APG 退役**：APG-01~05 整组删除，硬门（PB/RA）与规则级停点（Code Generation 首单元方向停点）交互回归阶段模板原生语义——approve / continue 及同义表述（任意语言）→ `report --result approved` → 同交互立即继续；无 hold 状态、无意图分类层。显式指令优先：回复中携带的其他显式指令按字面执行、门保持等待。理由：B19 三位置委派审查已承担把关职能，approve-hold 分层成为多余摩擦。组号映射：APG=原 Group 2（删除）；AUD/QT/BRF = 原 Group 3/4/5 → Group 2/3/4。引擎零改动。
- **D26 DOC 瘦身 + 合规只报例外**：DOC 六条编号与主体语义冻结，仅文本瘦身（DOC-01 删 typical-mapping 教学段、"approved change"→"change" 触发澄清、verification 三判据原样；DOC-04 worked example 压缩为判别式 + 先例指针，reviews.md/RV-07 句测试锁定不动）。合规报告全局改只报例外：全合规静默，仅列 non-compliant 与 N/A（附简短理由）——落点 = workflow-conventions Enforcement 段、SKILL.md 扩展合规段、三份扩展基线合规节。
- 批内默认项（用户确认）：DOC-06 保留（advisory）；F4 走全局同步（三扩展基线合规节一并改例外式）。

## 2. 方案终审（reviewer，全新会话）

方案全文经 reviewer 独立审查（findings-only 契约 + 5 项待验证主张核对）。结果：**7 发现（2 高 / 5 中）+ 5 改进 + 5 建议，全处置**；待验证主张 P-a/P-b/P-e 证实、P-c 半证伪（test_doc04 锁定 DOC-04 :51 内容）、P-d 修正后加强（workflow-changes 实为 6 处 DOC-04 引用，编号不动结论被强化）。

### 处置表

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| F1 | 高 | SKILL.md:56/58 逐条合规表与 D26 互斥（常驻上位指令冲突，D26 大概率落空） | 采纳：SKILL.md 两行改例外式 |
| F2 | 高 | code-gen :51 改写可能连带删掉"停点不跑 report"不变量（B18 R1 教训） | 采纳：改写规格保留原子句 + 新增测试钉住 |
| F3 | 中 | stage-contract.md:77 "Group 5 (BRF)" 漏网（主智能体 grep 截断所致） | 采纳：补清单项 + 残留扫描纳入组号 |
| F4 | 中 | 三扩展基线逐条合规清单与只报例外冲突 | 采纳：全局同步改例外式（用户确认） |
| F5 | 中 | B20 编号与"Operations 实义化 B20+"四处引用冲突 | 采纳：B20+→B21+ 顺延 + 占用链补记 |
| F6 | 中 | D26"语义全冻结"与两处实际改动自相矛盾 | 采纳：D26 措辞改"编号冻结、主体语义不变、两处显式登记微调"；:38 三判据不压 |
| F7 | 中 | D25 绝对表述会压过"同意但先别继续"类显式指令 | 采纳：D25 行补"显式指令优先"句（不恢复 hold 层） |

改进 5 项全采纳（先例指针指向技能内 workflow-changes.md 而非 docs/；v2 对比表组名更新；删除区间收尾避免双横线；dogfood 协议新开 §五 专项 + 模板行 10；AGENTS.md 计数算式更新）。建议 5 项取 4（提交拆分不取——小批同套验证，单笔提交理由登记；其余全采纳）。审查方一处史实修正被主智能体复核采纳：APG 系 v1.0 基座遗产而非 B06 引入（aidlc-workflows-cn 同名文件含 APG-01~05 为证）。

## 3. 实施记录（2026-10-22，主智能体单会话）

| 层 | 文件 | 改动 |
|---|---|---|
| 核心 | workflow-conventions.md | 概览五组→四组、删 APG 条目；Enforcement 改只报例外；Blocking 段删 APG 字样；删 Group 2 整组（连尾随 `---` 一并收）；AUD/QT/BRF 重编 Group 2/3/4；QT 辖区句去 APG-05；Enforcement 表删 APG 行；DOC-01 删教学映射段+触发词现代化；DOC-04 判例压缩 |
| 核心 | SKILL.md | :56/:58 合规段改例外式；:129/:301 Group 5→4、:298 Group 3→2 |
| 语义 | code-generation.md :51 | 方向停点去 APG 引用；"approval or continuation semantics releases"；保留"no `report` runs at the stop"不变量 |
| 语义 | workflow-changes.md :290 | 去 APG-01 指针，改"gate stays until approval/continuation semantics" |
| 组号 | requirements-analysis / build-and-test / workflow-planning / stage-contract / 三扩展基线 | Group 4→3（QT）×1、Group 5→4（BRF）×6、stage-contract SSOT ×1 |
| F4 | 三扩展基线合规节 | "listing each rule as compliant" → 例外式 |
| 测试 | test_rule_invariants.py | :146 断言改锚 Group 4；新增 ApgRetirementTests 两守卫（APG-/Group 5 禁现 + stage-contract Group 4 在位；停点 no-report 不量钉住） |
| docs | integration-plan.md | D25/D26 行、批次登记表 B20 行、:96 基线链补 B20 后 251、:123 与 :197 B20+→B21+（占用链四延） |
| docs | dogfood-protocol.md | 新增 §五 B20 专项（C1 硬门 approve 直续 / C2 合规只报例外，判据化）；原 §五~§八顺延 §六~§九；模板表新增行 10；增补日志追加 |
| docs | aidlc-v2-features-vs-v1.md :20 | 组名 DOC/APG/AUD/QT → DOC/BRF/AUD/QT |
| docs | AGENTS.md | 指针 D1-D26 / B01-B20；测试计数 251（算式链更新）；速览新增 B20 行；B20+→B21+ 两处（占用链 + P9 挂账） |

不动清单：engine.py / frontmatter / stage-graph.json 零触碰；DOC 六条编号与语义（B19 锚点 build-and-test:337 与 review-delegation:163 的 DOC-03 引用、DOC-04 双落点原样）；历史档案与决策旧行 append-only；QT/AUD/BRF 三组内容本身。

## 4. 验证

- `generate.py --check` 零漂移（无 frontmatter 触碰）
- 测试套件 **251 绿**（249 + APG 退役/组号守卫 + 停点不变量守卫）
- 技能侧残留扫描零命中：`APG-|Approve-and-Hold|approve-hold|Group 5|approve-and-continue`（references/ 与 SKILL.md；测试文件中的断言字面量除外）

## 5. 后续

- dogfood 迭代二观测：协议 §五 C1~C2（硬门 approve 直续无 hold 追问；全合规静默无逐条清单）；快照源顺延为本批收口提交。
- 遗留观察：C1 若出现"approve 后仍二次确认"，属 APG 残留行为，回填异常行。
