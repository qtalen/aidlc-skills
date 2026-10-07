# B03 · 轻量编排引擎（旧称 Phase 3）· 2026-09-14

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-14；09-15/09-16 两轮增量修复见"实施后审核与增量"节） |
| 触发 | 路线图分解（Phase 3——"判断归 LLM，精确归工具，决定归人类"落地） |
| 关联决策 | D6（修订：引擎必选）、D7、D9、D10、D12 |
| 测试基线 | 20 → 77（生成器 30 + 引擎 47）→ 增量后 102 |
| 材料来源 | 原 integration-plan.md §6 全部 + §9 2026-09-14 其二/其四/其五/其六（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**过程**（2026-09-14）：先完成双侧技术摸底（v2.0 编排工具 8.6k 行 orchestrate + 6.8k 行 state 的机制拆解；分叉侧状态/路由/契约/解析器现状盘点），随后逐条审议了"相对 v2.0 砍掉清单"（steering 续传、team/swarm、per-unit 波次、single、Kiro 遗留、compose 多意图、ownership env 门、传感器/证据链、jump/resume 机器、park）——确认砍的都是"**它服务的能力不在分叉范围内**"，没有一项是"移植不了"，全部可按防返工设计（见规格节末）的扩展路径加回。**注**：其中 jump/resume 机器经裁剪后保留子集入 Phase 3（jump 独立子命令 + status 恢复探针），被砍的是 v2.0 的完整机制（aidlc-jump.ts 的 resolve/execute 分层、resume 菜单引擎内路由等）。

**技术摸底依据**（2026-09-14 完成）：v2.0 侧 `aidlc-orchestrate.ts`（8.6k 行，next/continue/report/park/team-board 五子命令）+ `aidlc-state.ts`（6.8k 行）；选阶段算法 = 全图线性扫描 + scope 网格过滤 + state 覆盖 + checkbox 跳过（`aidlc-lib.ts:21852`）；v2.0 状态文件也是 Markdown。分叉侧现状：契约除 `condition` 外全机器可读；`execution-plan.md` 无程序化消费者（路由靠模型记忆）；状态/审计由模型在 20+ 处散文约定中手维护；`gate` 的下一阶段名散落在阶段正文。

**关键决策与理由**：

- **D6 修订（引擎必选）**：用户定调——引入引擎的动机就是践行"判断归 LLM，精确归工具，决定归人类"；原"可选增强层"立场隐含的双模镜像成本（每个引擎功能都要写一份 Markdown 约定镜像）会掐死后续演进。分叉对 v2.0 的差异化定位随之明确为"**同等理念、更轻的可移植性**"（Python 3.8+ vs bun + opencode 钩子体系），而非"零依赖"。
- **三归理念可行性结论**：精确归工具 ✅（引擎接管路由/状态/审计）；判断归 LLM ✅（condition 散文永不进引擎，v2.0 同此分工）；决定归人类 ⚠️ 诚实边界——无钩子环境防不住模型伪造批准（v2.0 同局限），靠提示词纪律 + 审计留痕。
- **状态完整性校验入 Phase 3**：引擎必选使"只有引擎能写状态"从空强制变为可检测（State Digest + 审计交叉核验 + halt + 人工重定基线）。检测非阻止，威胁模型是模型疏忽而非对抗。
- **jump 入 Phase 3**：完整性校验堵死歪路后，jump 是"改主意"的正规执行通道，二者阴阳配套；拆开交付会让每次正常需求变更都以"完整性告警"形态呈现（体验裂缝）。
- **Team Construction 死结消解**：引擎必选使 claim 锁可行（原死结：引擎可选则锁不可靠）；拆为形态 A（多会话团队，harness 无关，优先）与形态 B（swarm 进程内并行，harness 相关，殿后）；unit-major 是其硬地基（claim 粒度 = unit）。
- **single 入 Phase 4**：用户场景——team 并行试验多算法变体后选定其一单独重跑（试验-收敛闭环）。
- **多 intent / compose 不排期**（D11）：用户原话"一个版本就应该是一个产品意图……那应该是两个 git 版本的事"。
- **分发自包含确认**：技能目录内对 AGENTS.md 零引用（已查证）；用户侧前提仅两条——harness 能加载技能 + 能执行 python。裸项目 dogfood 列为验收硬标准。

**决策汇总表**：

| # | 决策 | 结论 |
|---|---|---|
| D6（修订） | 引擎定位 | **必选运行时依赖**。启动探测失败（无 Python 3.8+）→ HARD STOP 提示安装，工作流不启动。原"可选增强层 + 双模镜像"立场废止（镜像成本会掐死演进：每个引擎功能要写两份文档） |
| D7 | 技术栈 | **Python 标准库**（与 generate.py 同栈，3.8+，零第三方依赖） |
| D9 | 契约消费 | **compile-to-JSON**：generate.py 编译 `scripts/data/stage-graph.json`；引擎只读 JSON，**永不解析 frontmatter，也永不解析 condition 散文** |
| D10 | 状态/审计归属 | **引擎原子写** Markdown 状态 + 审计转移条目；State Digest（sha256）+ 审计交叉核验，漂移即 halt + 人类确认重定基线 |
| D12 | 分发形态 | 引擎随技能分发（`scripts/` 下）；验收硬标准 = **裸项目**（只复制技能目录、无任何其他文件）dogfood 通过 |

**审查修订（2026-09-14 其三，reviewer 审查后落地）**：🔴 D 组补系统性收口项（12+ 处手改 state 指令逐一改写，原清单仅覆盖 5 个文件）+ error-handling.md 恢复协议整体重定向为独立项；🔴 补状态文件分区所有权矩阵（B11：引擎辖区 digest 覆盖 / 模型辖区不入摘要）与 scope/计划覆盖的模型写-引擎读通道（原 report 无 payload 通道的空白改为混合所有权解法，report 不引入结构化参数）。🟡 jump 改独立子命令（保持 next 纯只读）；next_stage 标注为预测值；补 `--workspace` 调用约定与 python/python3 双命令名探测；补 report 转移语义矩阵（B8 表，E26 测试基准）；砍单注明 jump/resume 裁剪口径；"契约零改动"限定为字段集零改动（A3 散文修订含 Runtime neutrality 段）；WP 的 state-template-stages 生成区定为删除（D25）。🔵 SKILL.md 行数勘误（556）；AGENTS.md §1 字段清单补 scopes；引擎体量预估上调至 1000–1500 行；error directive 字段契约（code/message/hint）写入 B7。清单总数 26 → 31。

## 规格

**主题："判断归 LLM，精确归工具，决定归人类"落地。**

### 三归理念 ↔ 机制映射（实施自查表）

| 理念 | 机制 | 诚实边界 |
|---|---|---|
| 精确归工具 | 引擎独占跨阶段路由、状态机、审计转移；compile-to-JSON 防漂移；完整性校验防手改 | — |
| 判断归 LLM | condition 散文不进引擎：CONDITIONAL 阶段照常发射并标 `conditional: true`，模型判断不适用则 `report --result skipped --reason`；scope 推荐、深度自适应、需求澄清全留模型 | — |
| 决定归人类 | 门内容/双选项/NO EMERGENT BEHAVIOR 不变；jump 是"改主意"的正规执行通道 | 无钩子环境下"模型伪造批准"工具层防不住（v2.0 在无钩子 harness 同局限）；靠提示词纪律 + 审计留痕 |

### 实施清单

> 注：本清单内的 B5/B7/B8/B11、D23/D25、E26、A3 等标号为**原 31 项清单的分组条目号**（A-F 分组 + 序号），非批次（B##）或决策（D##）编号。

**A. 契约编译层（generate.py 扩展）**

1. 新增编译渲染器，产出 `scripts/data/stage-graph.json`：有序阶段数组（slug/name/phase/execution/gate/for_each/workspace_writes/produces/consumes/requires_stage/scopes）+ scope registry（name/default/depth/keywords）+ `state_version`
2. `--check` 覆盖 JSON 漂移（frontmatter 改了未重编译 → 非零退出；现有 CI contract-check.yml 自动兜底，无需改）
3. 修正 stage-contract.md 两处散文：worked example 的 condition 折行写法（与解析器单行能力对齐）；文首 Runtime neutrality 段（"pure Markdown" 表述在 Phase 3 后失效，改为"单一运行时依赖 Python 3.8+"口径，与主文档 D6 修订一致）
4. 契约 **frontmatter 字段集与取值约束**零改动（兑现 stage-contract §8 对 Phase 3 的承诺；A3 仅为散文修订，不触字段）

**B. 引擎本体（`scripts/engine.py`，单文件纯 stdlib，预估 1000–1500 行）**

5. 调用约定：`python <skill>/scripts/engine.py <subcommand> [--workspace <path>]`（workspace 默认取 CWD）；启动探测兼容 Windows `python` 与 Linux/macOS `python3`（探测序列两者都试）
6. `status`（只读）：双重职责——启动探测（python 可用 + 引擎完好）+ 会话恢复数据源；输出 `{engine, state: none|active|completed, current_stage, scope, depth, last_completed, ...}` JSON
7. `next`（纯只读路由）：线性扫描 + scope 过滤 + state 覆盖 + 勾选跳过；输出**单个** directive JSON（`run-stage` / `done` / `error`）；run-stage 含 stage/phase/gate/stage_file/produces/consumes/conditional/next_stage（**next_stage 是"假设本阶段 completed"的预测值，仅供呈现，不作为路由依据**）；error 字段契约 `{kind, code, message, hint}`（code 机器可读类别 / message 人类可读 / hint 补救提示）
8. `report`（唯一转移写入口）：`--stage <slug> --result <r> [--reason]`；原子写状态 + 追加审计转移条目。**转移语义矩阵**（E26 的测试基准）：

   | result | 勾选 | 指针 | 适用 |
   |---|---|---|---|
   | `completed` | `[x]` | 推进 | 非门阶段完成 |
   | `approved` | `[x]` | 推进 | 门阶段用户批准后 |
   | `rejected` | `[R]` | 停本阶段 | 门拒绝 |
   | `revised` | `[?]` | 停本阶段 | 修订后再提交 |
   | `skipped` | `[S]` | 推进 | 仅 CONDITIONAL 或计划 SKIP，须 `--reason` |

9. `jump --stage <slug>`（**独立子命令、写操作**；`next` 保持纯只读）：方向解析 + 指针移动 + 中间阶段重标 + `STAGE_JUMPED` 审计。**与完整性校验是阴阳配套**：校验堵死歪路，jump 敞开正门；缺它则每次正常改主意都会以"完整性告警"呈现。附带 Start Fresh（归档 aidlc-docs + 状态重置，resume 菜单执行层闭环；可独立为 `jump --fresh`，实现时定）
10. 状态完整性校验：写引擎辖区附 `State Digest`（sha256）；每次读先校验 + 审计交叉核验（勾选 vs 转移事件一致性）；漂移 → error directive + halt + 人类确认后重定基线。检测非阻止（无钩子收不走模型的 Write/Edit），威胁模型是"模型疏忽/偷懒"而非对抗。**digest 只覆盖引擎辖区**（见 B11），模型辖区不入摘要——其改动的合法来源是用户指令，由审计中的用户输入记录兜底
11. **状态文件分区所有权矩阵（设计项，实施的首件产出）**：

    | 状态文件的区 | 写入方 | digest 覆盖 |
    |---|---|---|
    | Stage Progress 勾选区、Current Status、State Digest、Unit Progress（预留） | **引擎独占** | ✅ |
    | Project Information、Workspace State、Code Location Rules、Extension Configuration、Autonomous Mode、Execution Plan Summary（含 Scope/Depth 与计划覆盖行） | 模型按模板写 | ❌ |

    WP 计划覆盖（Stages to Execute/Skip）由模型按结构化行格式写入 Execution Plan Summary，引擎读取消费（**收口"execution-plan.md 无消费者"**）；Scope/Depth 同理（模型写、引擎读，`next` 的 scope 过滤依赖它，为 load-bearing 通道）
12. 状态文件确定性创建（取代 workspace-detection Step 4 内联模板）：含 `State Version: 1`、`Engine` 字段
13. **单元清单结构化**：units-generation 把单元表（slug/名称/**依赖字段预留**/规模估计）以结构化形式落 state（模型辖区）；state schema 预留 `## Unit Progress` 区（引擎辖区，本阶段不启用，为 Phase 4 unit-major 留位）

**C. SKILL.md 引擎化改写**

14. 启动序列：跑 `engine.py status` 探测（`python`/`python3` 双命令名，见 B5）；失败 → HARD STOP + Python 3.8+ 安装提示
15. forwarding loop 入主循环：`next → 按 directive.kind 行动 → report → 重复`；directive 消费契约（error 原样呈现即停；不伪造 report；放弃 directive 直接丢弃不 report；**消费方忽略未知字段**——向后兼容条款，写进契约）
16. 阶段执行块瘦身：撤路由散文（"自动继续下一阶段"清单归引擎）；**保留** CONDITIONAL 的 Execute-IF/Skip-IF 判断散文与阶段内执行指引（判断归 LLM）
17. 所有权纪律：MUST NOT 手改引擎辖区（B11 矩阵左列）；模型辖区各区按模板正常维护；用户原始输入记录仍归模型（模型是唯一可见源）

**D. 关联规则文件同步**

18. workspace-detection：状态创建步骤改为引擎执行
19. workflow-planning：计划批准后由模型把覆盖决策按结构化行格式写入 state（引擎读取消费）
20. session-continuity：恢复菜单数据源改为 `status` 输出（呈现层保留 Markdown）
21. workflow-changes：收敛为"**判断在约定、执行在引擎**"——redo/跳步的执行一律走 jump，不再手工移指针
22. autonomous-mode 扩展：Review Stages 按显示名匹配 → 补 slug 对齐说明（消命名耦合风险；生成器 `_derive_name` 会剥离括号，显示名可能随 H1 变化）**（已作废 2026-09-29，D17：AM-06/Review Stages 机制整体移除——见 B10 档案）**
23. **系统性收口**：grep 全 references/ 树中所有 `aidlc-state.md` 手写指令（12+ 处：全部 construction 阶段文件、application-design、user-stories、units-generation、requirements-analysis、workflow-conventions 扩展等），逐一改写为 report 调用或删除——否则模型同时收到"引擎独占写状态"与"Mark stage complete"两组矛盾指令，dogfood 必撞
24. **error-handling.md 恢复协议整体重定向**（独立工作量）：备份重建/reset/标 SKIPPED/标 incomplete/修正 current stage 等手改 state 路径，统一改为"完整性 halt → 人工确认 → 引擎重定基线"新流程
25. workflow-planning.md 的 `state-template-stages` GENERATED 生成区归宿：**删除**（含 generate.py MARKERS 注册清理）——引擎确定性创建 state 后，该"教模型手写 Stage Progress"的模板成为矛盾指令/死代码

**E. 测试与验证**

26. `scripts/tests/test_engine.py`（stdlib unittest）：路由（scope 过滤/覆盖/跳过/完成判定）、状态原子写、report 转移语义矩阵全分支（B8 表）、status 探测、摘要漂移 halt（含**模型辖区改动不触发 halt**的反例）、stage-graph.json 与 frontmatter 一致性
27. 既有 20 个 generate.py 测试零回归 + 二次运行幂等
28. **裸项目 dogfood（验收硬标准）**：只复制技能目录的新项目全工作流跑通；另测 brownfield、手改 state 触发 halt、中断恢复

**F. 文档回填**

29. integration-plan.md（本节定稿 + 排期 + 讨论记录）
30. AGENTS.md §3 护栏修订 + 路线图速览
31. README / README_cn：使用前提（Python 3.8+）与分发形态（自包含技能目录）

### 范围护栏（本阶段明确不做）

- steering token 续传、team/swarm、per-unit 引擎路由（per-unit 阶段 = 单次 run-stage 发射，单元内循环模型负责）、single、park、ownership env 门、多 intent
- condition 结构化、gate 第三选项契约化（留正文）
- 传感器、reviewer/persona/五层记忆（Phase 5+）

### 防返工设计备忘（扩展性五支点）

1. **compile-to-JSON 单数据源**：所有消费方从同一编译产物取数，新数据只编译一次
2. **dispatch 子命令结构**：新动词 = 新 handler + 一个 case，无侵入
3. **directive JSON 可扩展**：消费方忽略未知字段（向后兼容条款）
4. **State Version 迁移机制**：状态格式演进不伤旧档案
5. **契约 §5 预留命名空间**：reviewer/sensors/lead_agent 等字段语义已定义，启用 = 白名单放行

**三档重跑语义边界（勿混淆）**：redo（workflow-changes 决策协议 → jump 执行，回拨主指针）/ jump（移动指针的路由行为）/ single（脱钩主线、绝不动主指针、独立审计对，Phase 4）。

**error directive 是统一逃生舱**：任何新失败模式走"呈现并停止"，不发明新协议。

## 实施与实施期裁决

按规格清单全部 31 项落地（2026-09-14）。分工：4 个 executor 并行（generate.py 编译层 + WP Step 8 重写 / 四规则文件引擎化 / state 指令收口 + error-handling 重定向 / SKILL.md + engine-contract.md），引擎本体（engine.py + test_engine.py）由主智能体亲自实现。

**交付物**：`scripts/engine.py`（Python stdlib 必选运行时引擎，子命令 status/init/next/report/jump/jump --fresh/rebase，~1000 行）+ generate.py 编译渲染器（`scripts/data/stage-graph.json`，--check 覆盖漂移）+ `references/common/engine-contract.md`（B11 分区所有权矩阵 + directive 消费契约 + 转移语义矩阵 + 完整性/rebase 流程）+ SKILL.md 引擎化改写（Engine Bootstrap 启动探测 HARD STOP + Orchestration Loop 主循环 + 阶段块撤路由散文 + per-unit report 总注）+ 全部 references/ 手改 state 指令收口（D23，含清单外捕获的 reverse-engineering.md）+ error-handling.md 恢复协议重定向（halt→人工确认→rebase）+ WP Step 8 重写（Execution Plan Summary 结构化行，state-template-stages 生成区删除）+ 单元清单结构化（units-generation Step 19 写 `## Units` 模型辖区，state 引擎辖区预留 `## Unit Progress`）。

实施期裁决（记录在案）：①per-unit（for_each）阶段引擎单次发射、单元内循环归模型，`report` 在最后一个单元门批准后调用一次（5 个 construction 阶段文件均补 per-unit note）；②审计交叉核验在存在 STATE_REBASELINED 事件后豁免（否则 rebase 无法真正"重定基线"）；③`jump` 到计划外阶段返回 `note` 提示需补 Stages to Execute 行（路由纯化，jump 不绕过 scope/计划过滤）；④`--workspace` 参数位子命令之后（调用约定 `engine.py <subcommand> [--workspace <path>]`）；⑤CLI 错误一律 error JSON + 退出码 1（usage 错误同形）；⑥engine-contract.md 将 init/report/jump/rebase 的成功输出记为"通用 JSON 确认对象"（消费方忽略未知字段兜底）。

## 验证

测试：`scripts/tests/` 共 77 例（生成器 30 + 引擎 47）全绿、generate 二次运行幂等、--check 零漂移；裸项目 dogfood 通过（greenfield 全流程走通至 done、brownfield bugfix scope 裁剪、篡改触发 integrity-violated halt→rebase、中断恢复、backward jump、jump --fresh 归档）。

遗留 backlog（Phase 4+ 评估）：scope depth enum 是否加 `adaptive`；welcome ASCII 截断保护；--check 重复 key 僵尸区逃逸场景；Operations 的 CONDITIONAL 语义。

## 实施后审核与增量

### 审查修复（2026-09-14 其五，reviewer 全面审查后落地）

🔴 workflow-changes.md Type 5/9 把引擎消费的 Scope/Depth 通道错指到 `## Project Information`（引擎只读 `## Execution Plan Summary`）——改为指向正确位置并明示"engine consumes ONLY the Execution Plan Summary copies"；RA Step 2.5 同步改为直接填 Execution Plan Summary 的 Scope/Depth 占位行。🟡 argparse 用法错误与未捕获异常绕过"一律 error JSON"契约——新增 `_JsonArgumentParser`（error → JSON + exit 1）与 main() Exception 兜底（code: internal）；SKILL.md per-unit 阶段块缺"report 恰好一次"护栏——Per-Unit Loop 节加总注；workspace-detection Step 3/6 残留路由散文——Step 3 重构为纯 brownfield/RE 适用性判断、Step 6 改为 report completed + 引擎路由。🔵 B&T 完成消息的 Operations 预测改中性措辞；engine-contract §6 补 Skip>Execute 优先级与节标题严格性说明；死代码清理（EV_FRESH 投入 --fresh 归档审计使用、generate.py `regenerate(check)` 死参删除）；补 4 个测试（CRLF 摘要稳定性、argparse JSON、jump→已完成阶段、未知 scope 名），引擎测试 43→47。

### 复审修复（2026-09-14 其六，二轮 reviewer 复审后落地）

🔴-1 同源残留两处清除——SKILL.md State Ownership 条与 B11 矩阵行的"Scope/Depth 属 Project Information"旧口径（改指 Execution Plan Summary）。卫生项：删除仓库根 dogfood 遗留垃圾目录（cmd 变量未展开产物）；AGENTS.md 测试数 73→77、旧 §8（原参考文件索引）SKILL.md 行数 556→620 勘误。改进项落地：RA Step 2.5 代码块归属消歧（state 填写格式与 audit 记录分开表述）；5 个 construction per-unit note 的 "approval" 统一为 "gate outcome"（覆盖 skipped 收尾）；engine-contract 规则 4 措辞精确化（仅该行回落，Skip 行仍生效）；workspace-detection Step 5 完成消息的下一阶段预测改"Decided by the engine"；engine-contract §10 error 样例补尾注对齐实际输出；test_jump_fresh_archives 补 WORKFLOW_FRESH 断言。

### 二次 dogfood 与增量修复（2026-09-15，course-schedule 真实项目 dogfood）

结论——引擎下限收益已兑现（长离题后状态零歧义恢复、契约缺陷 fail-fast 暴露逗号解析 bug、审计双轨），上限收益（多单元循环、多会话、完整性防漂移）待 Phase 4 场景验证；单单元线性小项目中 stage-major 够用，佐证 Phase 3 排序正确。落地三项增量修复：⑦`_slug_list` 注册表感知容错重组（理由含英文逗号不再误报 unknown slug）；⑧所有 JSON 输出（含 error 与 usage 错误）统一注入 `timestamp` 字段（ISO 8601 UTC 秒级），AUD 时间戳获取规则改为优先读引擎输出；⑨节标题静默回退让位于 fail-fast——`_parse_plan` 检测"计划形态行存在但精确 `## Execution Plan Summary` 标题缺失"并报 plan-invalid（信息性副本与占位符模板豁免，不违背契约 §6 informational-copies 条款）。配套：workflow-conventions QT-02 补"唯一上下文 Edit 回写、勿用临时脚本"实现提示；AGENTS.md §4 新增"先考证，后修复"编辑纪律（考证 integration-plan 决策/契约字段语义后再动手）；测试 77 → 96 全绿，--check 零漂移。考证修正两条初判：consumes 的 `required` 语义本就写明"生产者被计划跳过则 moot"（stage-contract §2），非缺陷；节标题回退是记录在案的已知弱点，修复方案因此收窄检测条件。

### 技能加载 token 测量与 engine-contract 加载策略调整（2026-09-15，同日讨论后落地）

course-schedule dogfood 全程实测——共加载 18 个技能文件约 171 KB（≈4.3 万 tokens，字节数÷4 粗估），另加引擎 JSON 输出约 1.5k tokens；相对无引擎版本净增约 +15%，其中最大单项是 engine-contract.md（18.7 KB，被 SKILL.md Common Rules 块强制每次加载）。考证结论：integration-plan 无任何决策要求强制加载，属 Phase 3 SKILL.md 改写时的分组惯性；stage-contract.md 已有"维护文档按需加载"先例；SKILL.md 自身在 5 处（legacy/integrity/完整契约/directive/所有权矩阵）已按指针使用。决策（用户批准方案 A）：engine-contract.md 移出 Common Rules ALWAYS 清单，改为按需加载——触发条件集中在 SKILL.md bootstrap 表后的指引句（legacy/integrity 行指向、jump/rebase 前、引擎错误或状态格式争议时）；engine-contract §1 Load 口径同步改写。安全性依据：happy path 实证不依赖契约内容（指令 JSON 自描述 + 错误消息自解释），误用由引擎 fail-fast 校验兜底。瘦身方案（契约 §10 Mermaid 样例下沉）经评估暂缓——按需加载后频率低，性价比不足。预期效果：引擎 token 增量从 +15% 压至 ~+3-4%（余量为 SKILL.md 引擎化改写净增与 JSON 输出）。注：本次真正省 token 的是 Phase 2 扩展延迟加载（4 个扩展全 opt-out，只读 opt-in 文件），非引擎。同日评估 SKILL.md 本体瘦身（Phase 3 使其 27.4→35.4 KB，+29%）：per-stage 样板与 Orchestration Loop 第 3 步纯冗余（可省 ~1.5-2KB）、Bootstrap 安装指引可压缩（~0.3-0.5KB）、阶段块步骤摘要（~22KB，pre-engine 存量，涉 v1.0 设计性格）可单独立项——**全部暂缓**（2026-09-15 决定），因 engine-contract 按需化节省的 18.7KB 已超 SKILL.md 引擎化净增，引擎版每会话加载量已低于无引擎版（后由 B12 减法批大幅收敛）。reviewer 复审（2026-09-15）有条件通过并落地两处修复：①契约 §4 三条 MUST（禁止伪造 report——non-gated 阶段引擎无法甄别、放弃 directive 由 next 重发、忽略未知字段）压缩进 SKILL.md Orchestration Loop 纪律行，原 L135 指针降格为出处注记，contract §1 触发枚举删去 "or orchestration loop"；②session-continuity.md 恢复菜单 B（jump）补预警——后跳会把目标及其后所有阶段重置为 `[ ]`，执行前须告知用户（该菜单是唯一由必载文档直接驱动 jump 的路径）。遗留：legacy handling 仅为契约 §10 样例旁注（存量问题），留待下次契约维护。

### reviewer 全面复审与修复批次（2026-09-16，Phase 0-3 复审）

reviewer 只读复审 + 主智能体逐条实码验证（文档步骤、引擎代码路径、测试反证三层证据链），确认三项实质缺陷并当日修复：⑩workflow-changes.md Type 1/2 执行协议与引擎路由语义冲突（引擎每次调用按计划行即时重算 current，且 Skip > Execute 恒胜）——Type 1"加 Execute 行后 jump"会被 invalid-jump 拒绝（目标通常已成 current，hint 不对症）或 forward jump 误标中间未执行阶段 `[S]`，且未指示先删 Skip 行时加回静默失效；Type 2"先写 Skip 行再 report"必报 invalid-transition（current 已被重算移走）。修正为与引擎语义对齐：Type 1 = 删 Skip 行（如在）→ 加 Execute 行 → 直接 `next`；Type 2 = current CONDITIONAL 阶段先 `report skipped` 后写 Skip 行，其余阶段先写 Skip 行再 `next`；jump 保留给重做/回退（Type 3/4）；error-handling.md 同族步骤与决策树同步修正。⑪截断状态（BEGIN 在 END 缺）原被误判 legacy（绕过完整性流程且 status 报 integrity: ok 掩盖损坏）——`load_state` 细分为 legacy（完全无标记，维持原语义）与 corrupt（标记残缺/乱序）：status 报 `state: corrupt, integrity: violated`，变更类命令报新错误码 `state-corrupt`（hint 给出精确 END 行内容与恢复路径），`jump --fresh` 仍可恢复；engine-contract §10 状态枚举与 SKILL.md bootstrap 表补 corrupt 行。⑫CI contract-check.yml 只跑 --check 不跑测试套件（engine.py 回归对 CI 完全不可见）——补 unittest discover 步骤（纯 stdlib 零依赖）。新增 6 例测试锁定语义：skip 行恒胜 execute 行、正确顺序（先 report 后写行）、错误顺序必拒（invalid-transition）、截断与孤 END 标记判 corrupt、fresh 恢复 corrupt；测试 96 → 102 全绿，--check 零漂移。P3 观察项（planned_skip report 分支不可达、jumped 豁免未入契约、END 标记文档语法不符、CRLF 混行尾、terminology 陈旧计数等）记录在案暂不动；其中"Skip > Execute 优先级"与"jump 不绕过计划过滤"经考证系故意设计（实施期裁决③、契约 §5/§6），非缺陷不改。
