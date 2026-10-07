# B06 · dogfood 反馈批（旧称 Phase 3.3）· 2026-09-24

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-24，单日内完成，先例同 B05） |
| 触发 | dogfood 反馈——fx991 首周期验收产物 + 验收后三轮讨论 |
| 关联决策 | —（P0 裁决：CTX 维持 opt-in，推迟 Phase 4 终裁） |
| 测试基线 | 169 → 205（引擎 14 + trace-matrix 22） |
| 材料来源 | 原 integration-plan.md §7 Phase 3.3 + §9 2026-09-24（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

### 前置：fx991 dogfood 首周期验收（两迭代，快照 bc04dd7，验收通过）

验收报告（含证据完整性/事实核验/六度量/消融/逐项裁决）：`docs/dogfood-records/calculator/acceptance-2026-09-24.md`（已佚——本地记录，git 全历史零记录，本节摘要即留存）。要点：

- **负债③裁决（关闭）**：produces_missing 软警告**不升级**硬阻断。两迭代触发 0 次；传感器定位 = 灾难检测（N≥2 全缺），正常流程天然不触发；本周期实际观测的制品类缺口（checkpoint 遗漏/audit 误替换/计数失准）全部在传感器管辖外，加严现有警告对已观测问题零解。证据强度声明：0 触发 = 无正例，属"无证据支持升级"的保守裁决，后续周期出现新证据可重开。
- **记录表两处定性修正**（验收人对照引擎代码核实）：①"强制扩展未说明"不实——SKILL.md:51 已声明，真因是 Loading process 编号步骤未覆盖该段落级规则，属"流程步骤未覆盖"；②"park note 无失效机制"收窄为"长阶段内无转移的多次中断"（转移本就清除 parked），与负债⑥同族。
- **度量遗留**：度量 4（换工具稳定）两周期均无样本；引擎内开关对照未执行（全引擎开）。后续周期补。
- **候选批次八项（建议立项"dogfood 反馈批"，Phase 4 前执行，待用户确认）**：高优先三项——强制扩展发现流程化、engine 轻量 stamp 注解动词、范围变更上游失效显式规程；中低五项——追溯矩阵脚本、DOC-04 redo 历史文本保护示例 + sweep 声明附模式集、传感器扩展 checkpoint-missing finding、resume_note 附 note 年龄。
- 立项理由：高优先三项均伤单会话可靠性，Phase 4 多会话会放大（更多恢复/更多审计条目/更多时间戳交叉）；"立即批"模式有 B05 先例。

### 定位与批次原则

**来源**：fx991 首周期验收 + 验收后三轮讨论（时间戳归因考证 / CTX-AM 引擎整合分层 / CTX 去留）。全部工作项均有 dogfood 实证或考证依据，非想象需求。定位：Phase 4 前的最后一批单会话可靠性加固——多会话会放大本批所修的全部问题。

**批次原则**（验收三轮核验的规律沉淀）：记录表三处定性偏差均为"模型对规则文本的引述失真"——修法优先选择**把正确行为变成最省力路径**（流程步骤/一条命令），而非追加规则条文。

**P0 前置裁决（用户，开工前）**：CTX 扩展去留三选一——a) 维持 opt-in 现状，推迟到 Phase 4 多会话 dogfood 后裁决（**推荐**，用户选 a）；b) 降级 advisory（去合规负担）；c) 删除。WP-1-④ 跟随：a→warning 级实施；b→info 级实施；c→作废。

## 规格

**WP-1 engine 扩展（主智能体直做，~3h）**——engine.py + 契约 + 测试，四项：
1. **`stamp` 注解动词**：零副作用子命令，输出 `{"engine":"ok","kind":"stamp","timestamp":"<ISO 8601 UTC>"}`；不写 state/audit/handoff（区别于 park 的注记留痕——stamp 是纯读）。docstring/usage 同步。
2. **status 增加 `autonomous` 键**：只读解析 state 模型区 `## Autonomous Mode`（先例：Execution Plan Summary 模型写-引擎读通道）；宽容降级（缺失/畸形 → null，不挂 status）；不参与 digest、不改变该区模型所有权。
3. **resume_note 附 note 年龄**：复用 handoff.md 最后 Park 条目的 Timestamp，输出 `note_age_seconds`（int|null）——只输出客观数字，不做 stale 判定（判断留模型）。
4. **checkpoint-missing finding（视 P0）**：artifact_alerts 新增类型，fail-open 不变，不做硬门（D14）。锚点映射简化为两条全局规则：inception 全部阶段完成 → `checkpoints/inception-checkpoint.md` 存在；build-and-test 完成 → `checkpoints/construction-checkpoint.md` 存在；仅当 Extension Configuration 表显示 CTX 启用时检查。per-unit 锚点留 Phase 4（依赖 Unit Progress）。
5. **配套同步**：engine-contract.md；workflow-conventions.md AUD Timestamp Acquisition 修订（preferred 扩为"同交互引擎输出 timestamp（含 stamp）"；条目 Timestamp 行附来源标注 `(engine|stamp|clock)`；fallback 收窄为"引擎完全不可用"场景）。
6. **测试**（169 → 预计 185±5）。

**WP-2 SKILL.md 强制扩展发现步骤（~0.5h）**：Extensions Loading 的 Loading process 加第 4 步——"列出各子目录全部规则 .md，减去有 `*.opt-in.md` 伴生者，余下为强制扩展，立即加载"（修 09-23 异常 1：规则存在于 :51 但步骤序列未覆盖）。零 frontmatter 改动。

**WP-3 workflow-changes.md 范围变更节（~1h）**：新增类型 "Scope Reduction / Requirement Invalidation"（砍需求/上游制品失效）——APG 分类 change request → 影响分析 → `report --result rejected` → `jump --stage <最上游受影响阶段>` → **redo 通道就地修订**（边界二分：问答/决策历史文本=DOC-04 保护不改写、以追加修订步骤记录更正映射；计划清单行与当前态制品=就地更新）→ **Deferred/Reserved 编号保留不回收**（追溯连续性）→ 逐阶段重走关卡 → 决策树补分支。素材：fx991 迭代 2 audit 实录。

**WP-4 workflow-conventions 修订包（~1h，与 WP-3 同批分发）**：①DOC-04 补判例（问答历史 vs 计划清单行的保护边界）；②DOC-01 sweep 节增句——清扫类审计完成声明必须附所用 grep 模式集与扫描范围（对治自证风险）。

**WP-5 追溯矩阵脚本（~2h）**：`scripts/trace-matrix.py`（纯 stdlib，作者期工具纪律放 scripts/）：输入 aidlc-docs 根，解析 requirements.md 的 FR 编号与 Deferred 标记 + stories.md 的追溯映射表/编号引用，输出 FR 覆盖矩阵、计数核对、Deferred/Reserved 保留核对。不进 CI（用户侧按需运行）。

**WP-6 提问工具能力抽象（~1h，2026-09-24 用户补充）**：修 harness 无关性违规——`question` 是 OpenCode 特定工具名。改动：①QT-01 顶部加 **structured question tool 能力定义**（"凡能在同一交互内呈现一组带选项的问题并收回答案的工具，无论何名；按能力特征识别，不按名字匹配"）；②QT-01 mapping rules 从参数映射改写为**语义映射**；③能力差异就近补齐条款；④autonomous-mode.md 7 处同步为能力表述；⑤QT-04 降级链不动。

**顺序与验证**：P0（用户裁决）→ WP-1（主智能体直做）→ WP-2 / WP-3+4 / WP-5 / WP-6 四路并行分发 executor → 收尾。总工时 **~9-11h，单日内可完成**。

**不做（明确移出，六项）**：AM 专用注记动词（`am --on/off`）→ **Phase 4 与 claim 并发锁一起设计**；produces_missing 升级硬阻断（负债③已裁决关闭）；checkpoint 硬门（违反 D14 fail-open 哲学）；audit_entries 改键名；SKILL.md 强制扩展清单生成物；per-unit checkpoint 锚点（依赖 Phase 4 Unit Progress）。

## 实施与实施期裁决

P0 用户裁决选 a（CTX 维持 opt-in）后开工，单日完成全部 6 个工作包。分工：WP-1（engine.py：docstring/stamp/模型区解析器 `_parse_autonomous`+`_ctx_enabled`/checkpoint 锚点探测/status 两新键/handoff 解析重构/CLI）与 WP-2（SKILL.md Loading process 第 4 步）主智能体直做；WP-3 / WP-4+6（同文件合并避免冲突）/ WP-5 三路 executor 并行，全部经主智能体逐 diff 复核。

**实施期裁决（记录在案）**：①`note_age_seconds` = 当前 park 注记的年龄，仅 resume_note 非空时输出——转移清除泊车后即使 handoff 留有历史条目也输出 null；②锚点语义：inception 锚点 = effective plan 内全部 inception 阶段 done（[x]/[S]），construction 锚点 = build-and-test done；status 时点探测，过期照报（fail-open warning）；③`autonomous` 宽容降级：节缺失或 Enabled 行缺失/非法 → null（不代猜 off，AM-09 模型侧回退仍是权威）；④trace-matrix 继承源限**节级标题**（不含条目 ID token），含 `USxx-x`/`FR-x` 的标题只作用于自身条目不向兄弟传播（US2-24→US2-25 反例单测锁定）；计数口径：占位 story 标题计入 story_total；⑤stamp 输出 `{"engine":"ok","kind":"stamp"}` + main() 统一注入 timestamp，归类：stamp 落 D13 **读层**（规格原文"注记类扩充"表述不准——stamp 零写入非注记，契约 §1 已按读层记录）。

executor 复核发现与裁决：①AM 文件两处清单外残留（AM-02 无条件 Other 禁令与 QT-01 新条件规则语义张力、AM-05 `multiple: true` 参数名残留）——主智能体裁决为 WP-6 同源问题并直接补修；②trace-matrix 解析把 US2-25 误继承 US2-24 的 Deferred——发回原 executor 会话修复 + 反例单测锁定；③WP-3 简报内一处 DOC-04 相对路径自相矛盾——executor 按磁盘现实取 `../extensions/...` 并验证链接目标存在，裁决正确。

## 验证

**205 测试全绿**（169 + 引擎 14 + trace-matrix 22）、`generate.py --check` 零漂移、trace-matrix 真实数据冒烟 fr_total=29（24 active + 5 deferred=FR-30~34）与 fx991 文档自述一致、story deferred=4 与修订记录一致；sweep：动词枚举/`question` 工具名绑定/"7 subcommands"/旧计数全树零残留。文档同步 8 处：engine-contract、workflow-conventions、session-continuity、SKILL.md、autonomous-mode（8+2 处能力化）、AGENTS.md、integration-plan、新增 trace-matrix.py + test_trace_matrix.py。

**使用约定（非缺陷）**：trace-matrix 对组级 Deferred 标题内引用 FR 编号者不作继承源——组级继承请保持标题无 ID token，或逐条目标记。

## 实施后审核与修复（同日，reviewer 静态全量审查）

审核对象为本批 12 项制品，背景对照 D13/D14、stage-contract、CTX-01、fx991 真实数据。裁决"**有条件通过，可作为提交依据**"：0🔴 / 1🟡 / 6🔵，四条待验证主张全部独立考证。发现全部当场修复：🟡#1 Type 10 缺"最上游受影响阶段=当前阶段"分支（该场景 `jump --stage <当前>` 必被引擎 invalid-jump 拒绝）——步骤 4 与决策树补"跳过 jump、就地修订重走本阶段关卡（report revised/approved）"；🔵#2 D13 读层枚举两处补 stamp + 裁决⑤补归类说明；🔵#3 trace-matrix 波浪号范围静默只取首号（fx991 真实追溯行 `FR-30~34` 实证）——改为 span≤50 展开 + 上限外维持旧行为 + 测试更新；🔵#4 占位 story 计数口径补入工具 docstring；🔵#5 `_note_age_seconds` 加 handoff 尾条与当前泊车注记的对应性守卫（不符返回 None，+1 测试）；🔵#6 AUD fallback 触发括注自相矛盾——改写为"引擎不可供时戳而会话仍在运行"；🔵#7 QT-02 残留 `Edit` 工具名绑定（既有非本批引入）——能力化表述。修复后 205 全绿 + --check 零漂移。

## 遗留与去向

遗留观察（非债务）：组级 Deferred 标题内引用 FR 编号不作继承源（使用约定已入验证节）；AM-06.6 的 Review Stages 显示名对齐问题维持原状（Phase 4 AM 注记化时随 slug 校验一并解决——后由 B10 随 AM-06 整体移除而消失）。主张 A 场景（CTX 误报评估输入）挂 Phase 4 设计输入第 3 条。
