# B01 · 阶段契约化 + 作者期生成器（旧称 Phase 0/1）· 2026-09-11

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-11） |
| 触发 | 路线图分解（Phase 0/1——解决"阶段清单在 8+ 个文件重复硬编码"的结构性痛点，痛点清单见 archive/v2-comparison.md §2.3） |
| 关联决策 | D2（方案 A：frontmatter SSOT + 作者期生成脚本）、D8（脚本目录约定） |
| 测试基线 | 0 → 20（生成器 unittest） |
| 材料来源 | 原 integration-plan.md §4 + §9 2026-09-15"Phase 0/1/2 复审与修复"（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 规格

### 步骤

**Step 1：设计阶段契约规范**
- 新增 `references/common/stage-contract.md`：字段定义、取值约束、校验规则
- 字段（借用 v2.0 子集，见 `opencode/.aidlc/aidlc-common/protocols/stage-definition.md:44-68`）：

| 字段 | 说明 |
|---|---|
| `slug` | 阶段标识，必须 = 文件名 stem |
| `phase` | inception / construction / operations |
| `execution` | ALWAYS / CONDITIONAL |
| `condition` | 执行/跳过条件（把 SKILL.md 里的 Execute IF/Skip IF 散文收编进阶段文件） |
| `produces` | 产物清单（供 session-continuity 加载列表生成） |
| `consumes` | 上游产物依赖 |
| `requires_stage` | DAG 边（软依赖，用于排序与流程图） |
| `gate` | 审批门类型（如 inception 的 approve-continue / construction 的 2-option） |
| `depth` | 深度策略（adaptive 等） |
| `scopes` | **本阶段预留空字段**，Phase 2 填充 |

**Step 2：给 14 个阶段文件加 frontmatter**（机械性；规则正文一字不动）
- inception 7：workspace-detection、reverse-engineering、requirements-analysis、user-stories、workflow-planning、application-design、units-generation
- construction 6：functional-design、nfr-requirements、nfr-design、infrastructure-design、code-generation、build-and-test
- operations 1：operations（占位）

**Step 3：在 8 个消费方文件中圈定生成区**
- 插入 `<!-- BEGIN GENERATED: <key> -->` / `<!-- END GENERATED -->` 标记
- 只生成"清单类"内容；SKILL.md 中各阶段的详细执行块（手写判断指引）**本阶段不生成、不搬动**，SKILL.md 瘦身留给引擎落地时

**Step 4：编写作者期脚本 `scripts/generate.py`**（纯 Python 标准库，仅维护技能时运行）
- 扫描 frontmatter → 校验（slug=文件名、必填字段、consumes 引用存在、DAG 无环）→ 重新生成所有标记区
- `--check` 模式检测漂移（生成物与磁盘不一致时非零退出）

**Step 5：验证**
- 跑脚本逐一审查 diff
- 在真实测试项目 dogfood 一遍技能，确认 AI 行为与改造前一致

### 范围护栏（本阶段不做）

- 不引入 persona/reviewer、五层记忆、学习仪式
- 不动阶段集、不改审批门仪式、不改 extensions 机制
- 不引入任何运行时依赖；`scripts/` 只是仓库内的维护工具，不是技能运行时的组成部分

### 补充说明

- 生成脚本虽在技能目录内（`scripts/`），但属作者期工具；技能分发时它是惰性文件，不影响 harness 无关性。
- ~~顺手修复已知文档不一致（archive/v2-comparison.md §2.3 的 execution-plan 命名问题）~~——**更正（Phase 0/1 审查发现）**：该修复当时未实际落地，`workflow-changes.md` Type 5 仍指向 `workflow-planning.md`；已在审查修复批次中真正修复（改为 `execution-plan.md` + `aidlc-state.md` 的 Depth 行）。OWASP TODO 单独处理。

## 实施与实施期裁决

**交付物**（2026-09-11）：`references/common/stage-contract.md`（契约规范）、14 个阶段文件的 frontmatter、`scripts/generate.py`（stdlib-only 生成器，含校验与 `--check` 漂移检测）、7 个消费方文件的 13 个 GENERATED 标记区。

实施期裁决（executor 实现时对规格做的三个裁决，记录在案）：inline 标记用原位替换；`depth` 缺失视为未声明（不默认 adaptive 标注）；相位副标题按各渲染场景分别取词。

遗留说明（有意为之的规范化，非 bug）：生成清单中的措辞做了归一（如 `CONDITIONAL - Brownfield only` → `CONDITIONAL`，完整条件在阶段文件 `condition` 字段）；workflow-planning 模板不再预置 `(COMPLETED)` 勾选状态；process-overview 流程图因 requires_stage DAG 补全而边更密。

## 验证

- 冒烟测试通过：新增一个阶段文件 + 跑一次脚本即可同步全部 12 个清单元件。SKILL.md 已加契约的按需引用指针（非常驻加载）。
- 本阶段完成后：扩展痛点解决；运行时仍是纯 Markdown 技能；AI 行为应与改造前一致。

## 实施后审核与修复（Phase 0/1 审查，与 Phase 2 审查同修）

🟡 修 execution-plan 命名（workflow-changes.md Type 5，此前声称已修实际未落地，见上方更正）；新增 `.github/workflows/contract-check.yml` CI 兜底（--check 漂移检测）；契约 `depth` 字段语义对齐实现（缺失=未声明，仅显式 adaptive 渲染标注）；depth-levels.md 的 Application Design 产物示例对齐 SSOT（component-diagram.md 系历史残留，已更正为真实产物清单）；解析器 `_strip_inline_comment` 静默截断 bug 修复（引号内 " #" 不再被截）+ 新增 `scripts/tests/` 20 个 unittest（解析边界/校验/幂等/漂移检测）；B5 数据精度三处（WP 补 consumes questions 文件、B&T 的 code 产物 required→true、契约 §4 补 audit.md 归因说明）。

遗留 backlog：`--check` 重复 key 僵尸区与 key 前缀误配两个逃逸场景、保留键报错信息优化、中缀 glob 约定、Operations 的 CONDITIONAL 语义（Phase 4+ 评估 NEVER 值）、welcome ASCII 截断保护；Phase 3 设计提示：execution-plan.md 无消费者、condition 为散文、第三选项在正文（引擎落地时收口）。

## 实施后联合复审（2026-09-15，Phase 0/1 + Phase 2 交付物）

对 Phase 0/1（契约+生成器）与 Phase 2（scope 矩阵）做了一轮双路全面复审。总体结论：机制层零缺陷（契约 16 条校验规则全有实现、84 格 scope 矩阵逐格核对零误差、--check 零漂移、77 测试全绿），无 🔴 发现。落地的 5 项 🟡 修复：

1. **SKILL.md B&T 手写产物清单陈旧（5/8）**：改为指向阶段文件的指针，不再枚举文件名。
2. **依赖建模数据修正**：code-generation 的 `requires_stage` 补 `functional-design`、`nfr-design` 边；infrastructure-design 补 `functional-design` 边；5 处同类 consume（nfr-requirements/CG/infra-design 的 FD/*、CG 的 nfr-design/* 与 infra-design/*）`required: false → true`（对齐契约 §2 语义与 nfr-design 既有写法）。流程图/计划图新增 3 条边，经生成器落地。
3. **FD 前提条件随 scope 条件化**：nfr-requirements / infrastructure-design 的 "Functional Design must be complete" 前提与 Step 1 读取行补"计划无 FD 阶段时改从 requirements.md + RE 产物取数"的条件分支（security-patch/infra scope 下 FD 恒为 SKIP，原措辞每次运行必触发矛盾指令）。
4. **stage-contract §6.1/§6.3 同步 scope 淡化口径**：keywords 字段描述与选择流程改为"无歧义自动选定、不设门；真歧义才走最小候选聊天问题"，消除与 RA Step 2.5 现行行为的冲突。
5. **聊天豁免传播**：question-format-guide 总则/清单与 session-continuity 的"NEVER ask in chat"均补 RA Step 2.5 scope 选择问题的唯一豁免。

验证：generate.py 幂等且 --check 零漂移、无 advisory 告警，77 个 unittest 全绿。

复审遗留 backlog（未修，并入既有清单）：契约硬规则 1-8/10/12 与 advisory 13-15 缺单测（后由 B05 WP-6 清零）；解析器未闭合引号静默通过；未注册文件中的 GENERATED 标记区逃逸 --check；workflow-changes Type 9 混淆 scope-SKIP 与 [S] 标记且决策树缺 Type 9 分支；隐式单单元前提注记遗漏 nfr-design/build-and-test；规则 16 的 for_each 豁免宽于约定覆盖面（Phase 4 扩 scope 前处理）；terminology Operations "Outputs" 与 process-overview "No fixed sequences" 陈旧散文（后由 B12 减法批两文件整删全销）；旧 §4 状态段"13 个 GENERATED 标记区"计数口径与现树（17 个）不符，待下次修订校正。
