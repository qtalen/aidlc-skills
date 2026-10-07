# B12 · 文档减法清理批（D-清系列）· 2026-09-29

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-29，三批三 commit + 收尾批；2026-10-06 双臂 dogfood 验收方向性通过） |
| 触发 | 用户发起"做减法"——技能文件遗留大量不再需要的文本，干扰上下文、浪费 token |
| 关联决策 | D-清1~9（见主文档决策登记"减法批子系列"） |
| 测试基线 | 231 → 236（收尾批后 237） |
| 材料来源 | 原 integration-plan.md §9 2026-09-29 其三 + 2026-10-06（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**需求**：Phase 1→3.3 及后续小批在技能文件中遗留大量不再需要的文本（路由遗物/判据三重副本/墓碑/教学冗余/死文件），干扰上下文、浪费 token。经两轮对话定调 + 两轮 reviewer 计划审核，形成计划 v2.2（存 `C:\Users\qianpeng\.opencode\plan\aidlc-doc-slimming-plan.md`，含一审 2 阻断+8 建议+3 存疑、二审 2 阻断+5 建议+2 存疑的全部处置对照表）。

**D-清系列裁决**（九条，全文见主文档决策登记）：

| # | 裁决 | 备注 |
|---|---|---|
| D-清1 | 纯减法·语义等价（五类判据，无法归类不删） | 判据环节等价性由 WP0 三方调和保障 |
| D-清2 | 历史叙事直接删除；仅存量工作区运行时价值者留一行 | |
| D-清3 | 范围=默认上下文优先；opt-in 大文件留下一轮 | |
| D-清4 | legacy pre-engine 分支留代码批，engine.py 零改动 | |
| D-清5 | process-overview.md 整删 | |
| D-清6 | generate.py 例外三项：REGISTRY 条目删除 + scope-matrix 条件渲染特性（含校验/夹具迁移/契约修订）+ 死渲染函数清理 | |
| D-清7 | AWS 世代散文删例子留框架 | RE/infra-design 的检测清单词元不动 |
| D-清8 | 路由散文收口专项 | |
| **D-清9** | **判据唯一权威 = 阶段 frontmatter `condition` 浅映射 `{execute_if, skip_if}`**，生成器渲染进 scope-matrix 生成区（"CONDITIONAL Stage Criteria (authoritative)" 清单），SKILL.md 块判据与 3.1-3.4 副本全删；ALWAYS 保持标量双形态校验 | 取代 A/B 方案 |

**计划审核要点**：一审证伪"判据权威在阶段文件正文"（9 个 CONDITIONAL 中 7 个只有 frontmatter 摘要，且三处判据是**分歧变体**而非副本）→ WP0 升级为三方比对调和；二审抓出 C 方案两个执行面阻断——condition 改映射瞬间两个 legacy 渲染器会把 dict repr 写进恒载文件（改法 b：批次重排为"删除先行"）+ 新校验形态未定义会当场爆红（改法：双形态契约 + 夹具双形态化 + Rule5 拆 4 测试）。主张 A-H 八项全定论。

## 实施（三批三 commit，每批 --check+全测试）

- **Batch 1（70ce2d3）删除先行**：整删 process-overview.md（10.3KB 恒载文件，含与引擎路由直接矛盾的 ":24 No fixed sequences"）与 terminology.md（10.6KB 零引用死文件）；generate.py 删 2 个 MARKERS 条目（7 key）+ 4 个死渲染函数（保留共享的 render_mermaid/render_stage_list）；新增 RenderMapCoverageTests 防"静默死渲染器"复发；同步 SKILL.md 加载清单/stage-contract 引用/AGENTS.md:24。
- **Batch 2（d25a5fc）判据通路**：WP0 三方调和写入 9 个 CONDITIONAL frontmatter（units-generation 剔除 WP 3.3 的 FD 范畴条目——functional-design 判据已覆盖；US 取并集保留 SKILL 独有的 technical debt cleanup/developer tooling 与"边界默认纳入"规则；operations 给占位性映射保持校验统一）；WP1 双形态校验 + 矩阵判据渲染 + stage-contract 三处对齐 + 夹具迁移 + ScopeMatrixCriteriaTests；Step 3.0 指针改向权威清单。
- **Batch 3（本 commit）散文减法与收尾**：SKILL.md 631→343 行（删 US 评估矩阵副本/14 块 Execute IF-Skip IF/Execution 模板复读/审计弹幕去重指向 AUD 组/Checkbox 两级合并/✅❌ 教学块）；workflow-planning 删 3.1-3.4/Step 6 样式内部去重/Step 10 改"report 后引擎路由"/AWS 例子删留框架；WP6 墓碑清扫（AM-06 压缩为两行、D 纪事剥除、engine-contract 旧键举例删但宽忽略机制句保留）；error-handling 17.4→9.4KB；qfg 示例压缩（Evidence-First 注释三处原样保留）；engine-contract 样例区裁决为无操作。

## 验证

unittest 236 全绿（231 + RenderMapCoverageTests 1 + Rule5 拆分净增 3 + ScopeMatrixCriteriaTests 1）；`--check` 零漂移；悬空引用 grep 对账零命中；基线实测——必加载集（SKILL+session-continuity+content-validation+qfg+workflow-conventions）**97,064 → 73,262 字节（-24.5%）**，其中 SKILL.md 39,593→26,602（-33%）；error-handling 17,393→9,422（-46%，按需）；workflow-planning +980B（判据清单按 D-清9 设计迁入该按需文件，非回归）。

**销账**：B01 联合复审遗留 backlog 的"terminology Operations 'Outputs' 与 process-overview 'No fixed sequences' 陈旧散文"项——两文件整删，全销。

**后续登记**：① 代码批·旧格式兼容层退役（engine.py legacy 分支 ~8-10 处 / 宽容解析语义重评 / test_engine.py 旧格式夹具 6+ 处——三层一体，前提=确认无 pre-engine 存量工作区，连带 SKILL.md bootstrap legacy 行与 engine-contract legacy 枚举）；② 代码摸底批（可选）：engine.py/generate.py/trace-matrix.py 同款摸底；③ opt-in 大文件减法（resiliency 28K/security 18K/PBT 18K）留下一轮。

**实施后审核（reviewer，同日）+ 收尾批修复（第 4 commit）**：零阻断；一审/二审共 15 项处置全部验证落地；主张 I-O 定论。收尾批修复：① UG 调和留痕补全（保留 multiple packages 并入 services/modules/packages，剔除五项并注明承接判据）；② US 试写样例摘要 + frontmatter 优先级锚行定死（冲突以 frontmatter 为准）；③ SKILL.md Directory Structure 裁决为保留（no-op）；④ AGENTS.md 测试计数 231→236；⑤ autonomous-mode.md:156 中性化对齐 engine-contract:196；⑥ test_generate.py 模块 docstring 双形态化 + 新增 DeletedNameHygieneTests（把悬空 grep 固化为防回归测试，覆盖技能树 md/py 与仓库根 README.md/README_cn.md，排除测试自身与 AGENTS/docs 历史档案）。

## 双臂 dogfood 验收（2026-10-06，fx991，方向性通过）

**验收结论**：D-清系列行为面验收**方向性通过**——三腿双臂（fx991 日常迭代嵌入：腿1 历史记录功能 / 腿1b 单组件精度字段 / 腿2 evaluate 重构+bug）CONDITIONAL 决策集合逐腿完全一致；臂 B（减重后）判据溯源全部引用新权威清单措辞、零旧判据残留；六会话 F1-F6 探针零失效。token 收益维持静态估计（恒载 −24.5% ≈ −5.8K tokens/会话）；会话级实测三腿 Δ(B−A) = −23.0K / +4.9K / −17.7K，方向 2/3 有利 B 但噪声 >> 信号，不可分辨文档差（实证"制品主导上下文"预判）。完整对账见 `docs/dogfood-records/fx991-calculator-slimming-ablation-2026-10-06.md`。

**证据定级与偏差（如实）**：日常使用嵌入形态，非受控消融。腿1/1b 可信；腿2 两侧快照来源存疑 → **腿2 不构成减重验证证据**，降级为 F2/F4/F5 日常累积。臂副本 .git 重初始化致 lineage 断裂，lineage 证明退化为特征判定——协议 §零.1 源 commit 注记缺失的实证代价。F6 实发冲突样本（引擎按计划行残留 emit user-stories vs frontmatter `refactor: SKIP` → frontmatter wins 裁定 skipped）**重定性为 Phase 2 scopes 权威机制的验证**，非减重锚行。腿1 预注册"UG/FD 双 execute"两臂均未出现——非回归，登记**判据锐度观察**（"触及多模块"与"需要分解"的边界仍靠模型裁量）。

**新发现登记（改进项排队，未立项）**：① 引擎 Windows 自由文本参数三会话复发（`park --note` 空格/分号、`report --reason` 空格被 cmd 拆参）→ 建议 `--note-file`/`--reason-file` 通道或编码约定；② 引擎 emit 未按 frontmatter scope 预剪枝（计划行含 SKIP 阶段仍 emit → 多耗一轮交互）；③ consumes `required:true` × scope 剪枝组合语义待 stage-contract 澄清；④ dogfood-protocol §零 增补快照 STAMP 惯例（源 commit+时间戳）与副本记录卫生。

**部署卫生待办**：主项目 fx-991-calculator 的 `.agents` 仍为减重前快照（`.agents` 末次提交 `5ff1923`）——需更新至当前技能 HEAD，否则后续迭代继续承担胖文档负载。

**遗留观察点与决策回填**：指针化阶段块加载遗漏——本周期 6 会话零观测，转日常累积通道（预注册：多周期阴性方可关闭）。produces_missing 连续六会话零触发（升级议题持续无新证据）；resumed-artifacts info 级"先读后写"正向旁证 ×7。账目勘误：AGENTS.md §3.1 测试计数在收尾批误记 236（DeletedNameHygieneTests 落地后实为 237），随记随修。
