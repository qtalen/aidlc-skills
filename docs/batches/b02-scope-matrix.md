# B02 · scope 裁剪矩阵（旧称 Phase 2）· 2026-09-12

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-12） |
| 触发 | 路线图分解（Phase 2：Workflow Planning 从"逐阶段临时判断"升级为"先选 scope 再微调"） |
| 关联决策 | —（scope 精简取舍见"立项与裁决"） |
| 测试基线 | —（Phase 3 完成时点生成器累计 30 例） |
| 材料来源 | 原 integration-plan.md §5 + §9 2026-09-14"scope 淡化 + 扩展配置成熟度重估"（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

关键决策（本轮确认）：精简 6 个 scope——`poc`/`mvp`/`workshop` 依赖 Operations 补齐后才有区分度，届时再引入；`enterprise` 用 depth 表达；命名对齐 v2.0 以便 Operations 补齐后各 scope 只需"扩行"（如 bugfix 追加 deployment 阶段），定义本身不改。

## 规格

- ~~给阶段 frontmatter 填充 `scopes:` 字段~~ ✅
- ~~生成脚本转置出 scope 矩阵表（EXECUTE/SKIP），注入 Workflow Planning 规则~~ ✅
- ~~Workflow Planning 升级：先按任务特征选 scope（关键词/显式指定），再做单阶段微调~~ ✅

## 实施与实施期裁决

**交付物**：`references/common/scopes/` 6 个 scope 定义（classic[默认]/bugfix/refactor/security-patch/infra/express，v2.0 对齐命名）；14 个阶段 frontmatter 填充 `scopes:` 映射；stage-contract.md §6（scope registry 规范、成员语义、选择与 depth 绑定）+ §7 校验规则 9-12；generate.py 新增 scope registry 解析、完整性校验与两个渲染器（`scope-catalog` 注入 Requirements Analysis、`scope-matrix` 注入 Workflow Planning）；RA 新增 Step 2.5（关键词启发式推荐 + 用户确认，显式指定优先）；WP 新增 Step 3.0（scope 基线 + 单阶段微调），计划/状态模板记录 Scope/Depth。

运行时上下文纪律：AI 只看生成的矩阵/目录表（~35 行），scope 文件本体按需加载（仅被选中的那个）。

有意分歧（记录在案）：`infra` scope 保留 code-generation EXECUTE（v2.0 跳过它用独立 ci-pipeline 阶段，我们的 CG 负责写 IaC）；矩阵列序 = default 优先 + 字母序（classic, bugfix, express, infra, refactor, security-patch）。

## 验证

（含于联合复审——2026-09-15：84 格 scope 矩阵逐格核对零误差、--check 零漂移，见 B01 档案"实施后联合复审"节。）

## 实施后审核与修复（reviewer 全面审查后）

🔴 隐式单单元约定——scope 跳过 units-generation 时 per-unit 阶段对全任务执行一次（WP Step 3.0 约定 + CG/FD/NFR-req/infra-design 前提条件化 + 生成器 advisory 规则 16 防回归）；🟡 SKILL.md 加 scope 总则（scope SKIP 的阶段不得重新评估）、RA Step 2.5 明确确认为门式聊天选择（豁免问题文件规则）+ 新功能请求优先 classic 的关键词优先级规则 + audit 显式记录、depth-levels.md 更新两层选择描述（"Scope"因子改名 "Change footprint" 消歧）、契约 default 字段语义对齐生成器（恰好一个）；🔵 workflow-changes.md 新增 Type 9（re-scope）、terminology.md 加 scope 消歧词条、session-continuity 恢复时读取活跃 Scope（无记录按 classic）。

遗留 backlog：infra 在 brownfield 下 RE=SKIP 的代价提示、解析器 `_strip_inline_comment` 对含 " # " 引号字符串的边界 bug、scope depth enum 是否加 `adaptive`（Phase 3 再评估）。

## 附注一：scope 选择淡化（2026-09-14 已落地，修改本批交付的 RA Step 2.5 行为）

- 动机：对最终用户淡化 scope 概念，减少明显场景下的审批门（用户原话："明显是一个 bug，直接给 bugfix 就好；classic 既然知道太重，就不需要让用户选"）。
- 改动：`requirements-analysis.md` Step 2.5 第 4 条重写——无歧义（用户显式指定，或关键词唯一命中且无优先级冲突）→ **自动选定、不设门**，事后一句话告知并记录 state/audit；有歧义 → **最小候选**（1-2 个最可能的，永不展示完整目录，不列已知不合适的 scope）；Workflow Planning 门作为选错的安全网。`SKILL.md` scope 段落同步（"selected with the user" → 自动选定优先）。纯正文改动，`generate.py --check` 通过。
- 注意：本附注修改了本档案规格中"用户确认"的原始描述——Step 2.5 现行为以本附注为准。

## 附注二：扩展配置成熟度重估（2026-09-14 搁置，待 Operations 阶段补全后处理）

- 背景讨论：淡化 scope 后用户不会主动选 scope；scope 机制靠"默认 classic + 轻量信号触发"自动按请求分类（功能请求自动回落 classic，机制已保证）。但"产品从 MVP 转向企业级"的真正载体不是 scope，而是**项目级的扩展插件配置**（Security Baseline / Resiliency / PBT 强度）——它持久生效，却缺少重估触发时机（opt-in 问题挂在 RA 澄清问题文件里，需求太清晰时不生成文件就不会重问，存在盲区）。
- 已细化的方案要点（未实施）：
  1. **位置**：RA 新增 Step 5.2（扩展重估），Step 5.1 加交叉引用（已配置不重问，除非信号触发）。
  2. **触发信号**：M1 用户措辞含"上线/正式/生产/企业级/合规/付费/用户数据"（强）；M2 需求涉及敏感面（认证/支付/个人数据/外部集成）而 Security Baseline=No（强）；M3 迭代 ≥3 轮且从未重估（弱，仅提示）；M4 棕地代码规模增长（弱，仅提示）。强信号→必须重估；弱信号→完成消息里一句话提示。
  3. **关键不对称**：scope 可自动选定（选错可零成本纠正、不引入约束）；扩展**绝不自动开启**（开启即引入阻塞性约束，静默开启会让用户莫名被门拦）——重估只能"问"，且只问信号指向的 1-2 个扩展，一句话说清后果。
- 搁置原因（用户决定）：Operations 阶段尚未补全，扩展配置的处理与 Operations 内容（部署/监控/生产就绪）强相关，待 Operations 补全后一并设计，届时回填为正式方案。（主文档"开放项总账"有登记。）
