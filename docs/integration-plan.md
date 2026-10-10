# AI-DLC v1.0 分叉整合计划（integration-plan）

> 本文档是 v1.0 分叉（原地进化于 `.agents/skills/aidlc-workflows/`）整合 v2.0 先进理念的**主文档与单一入口**。
> 创建于 2026-09-11；2026-10-07 文档重组批（B14）起采用"主文档 + 批次档案"架构：本文只保留背景、决策登记、批次登记表、现状快照、未来路线、开放项总账、维护规程；**全部历史细节住在 `docs/batches/`（执行批次档案）与 `docs/archive/`（冻结档案）**。
> 文档体系与登记规则见 §7 维护规程。主文档行数红线 350。

---

## 1. 背景与目标

- **v1.0**（`.agents/skills/aidlc-workflows/`）：纯 Markdown 技能形态（SKILL.md + references/ 规则文件），已停止维护。用户使用习惯好，但存在结构性扩展痛点。
- **v2.0**（`opencode/`）：opencode 插件形态（`.aidlc/` 核心 + `.opencode/` 原生层 + `aidlc/` 数据树），版本 2.7.1，含 50+ 个 bun/TS 工具、17 个钩子、33 阶段、11 scope、14 agent。
- **任务**：在 v1.0 上发展独立分叉（**不与原版 v1.0 整合**），吸收 v2.0 的先进理念（对比分析见 `docs/archive/v2-comparison.md`）。
- **硬性约束**：保持 aidlc-workflows 的 **harness 无关性**——任何能加载技能且能执行 shell 的 AI 编码工具可用，不绑定特定 harness 的钩子/插件机制。Phase 3（B03）起引入**单一运行时依赖 Python 3.8+**（编排引擎必选，D6 修订；原"零运行时依赖、纯 Markdown"措辞废止，理由见 B03 档案）。
- **演进方式**：原地进化（`.agents/skills/aidlc-workflows/` 直接修改，git 分支保留历史），分批整合，每批可独立测试。

---

## 2. 决策登记

> 决策（D##）= 未来工作必须遵守的语义裁决，编号永不重排；后决策可显式取代前决策（取代关系在条目内注明）。实施叙事见对应批次档案。

| # | 决策 | 结论 |
|---|------|------|
| D1 | 阶段体系 | **保持 v1.0 阶段集**（3 相位 14 阶段），不引入 v2.0 的 Ideation 相位和完整 Operation 相位。〔2026-10-08 D19 取代注记：其六新增 `product-brainstorm` 阶段（RE 后 RA 前），阶段集 14→15——相位结构不变，仍无 Ideation/完整 Operation〕 |
| D2 | 唯一事实源方案 | **方案 A：阶段文件 frontmatter + 作者期生成脚本**（否决方案 B 纯注册表，理由见 §5 路线图节末注） |
| D3 | persona/评审者体系 | 暂不引入，后置到 Phase 3+ |
| D4 | 五层记忆/学习仪式 | 暂不引入，后置到 Phase 3+ |
| D5 | 分叉落点 | 原地进化 `.agents/skills/aidlc-workflows/` |
| D6 | 编排引擎定位 | **必选运行时依赖**（2026-09-14 修订，取代原"可选增强层"立场）：单一依赖 Python 3.8+，无引擎 = HARD STOP 提示安装。修订理由见 B03 档案 |
| D7 | 引擎技术栈 | **Python 标准库**：与 generate.py 同栈，零第三方依赖；"契约设计与引擎语言无关"仍成立 |
| D8 | 脚本目录约定 | **所有脚本（含作者期工具）放技能目录下的 `scripts/`**，遵循 Agent Skills 规范 |
| D9 | 契约消费方式 | **compile-to-JSON**：作者期 generate.py 编译 `scripts/data/stage-graph.json`，引擎运行时只读 JSON，解析器风险关在作者期 |
| D10 | 状态/审计归属 | **引擎原子写** Markdown 状态 + 审计转移条目 + State Digest 完整性校验（检测非阻止） |
| D11 | 多 intent / compose | **不排期，仅记录**：一版本一产品意图，两件事 = 两个 git 版本；若重启须与 Team Construction 协同设计 |
| D12 | 引擎分发形态 | **随技能分发**：用户侧前提仅"harness 能加载技能 + 能执行 python"，不依赖 AGENTS.md 等任何额外文件；裸项目 dogfood 为验收硬标准 |
| D13 | 动词三层纪律 + 注记转移不变律 | 引擎动词分三层——读（status/next/stamp，无副作用）；**转移（report/jump，封闭集合 = 唯二改变 marks/current 的动词，Phase 4/5 永不新增）**；生命周期（init/park/rebase；park 为注记子类）。注记动词必须保持 marks 与 current 不变。Phase 4 的 claim/release 照此办理——实现为 report 的 additive guard，不新增转移动词。新动词入场券 = 与全部既有 mutating 动词的两两交互测试 |
| D14 | 传感器 fire 点与 finding 接口 | fire 点 = 引擎动词（status=恢复时 / report=收单时），永久不变（harness 无关性使然）。finding 五字段 `{type, severity, subject, message, action_discipline}` 即 Phase 5 传感器接口；`type` 集合可增不可删；同一 state_version 内对象 shape 永不破坏性变更；Phase 5 manifest 化须过输出等价测试 |
| D15 | 完成态再入语义 | 同一产品的功能演进**不是**新产品意图——工作流完成态下 `jump --stage <slug>` 放行为**再入**（目标及其后重置 `[ ]`，语义同 backward redo，审计记 re-entry；"jump 不绕过计划过滤"对再入同样生效），是同产品新迭代的正规通道；`jump --fresh` 保留给新产品意图/显式干净重启。D11 不变：同产品多迭代 = 同一意图的多个版本，版本边界由 git 提交承载 |
| D16 | AM 生命周期绑定工作流轮次 | 激活后持续到本轮完成转移或用户显式停止（**暂停=彻底关闭**，恢复需全新重问）；轮次边界确定性过期——完成转移（引擎翻转 Enabled→No）、再入 jump（同翻转，自愈存量）、fresh（归档即消失）；计划行自复活路径由模型兜底翻转。引擎由此获得契约 §6 所有权矩阵**唯一模型区窄写窗口**；通解（显式动词/digest 覆盖/并发语义）留 Phase 4 收编。激活提问形态已被 D17/D18 修订 |
| D17 | AM 简化 + Code-Gen Hold | **审核阶段机制整体移除**（AM-06 规则删除、编号退役不重排、AM-03 全阶段自动批准）；**暂停/停止语义重定为优雅降级**——模式关闭后完成手头工作、标准模式继续到下一个审批门等人工，直到本轮结束不自动恢复，仅显式 Activate 重激活；**Code-Gen Hold（AM-11）**——停点每次激活全新问、任何持久化配置值都不作预选，仅 code-gen 未开工时可布防，停点处模式保持开启，每次激活最多一次；停点纯模型侧实现。修订 D16：双问 Q2 换轨、AM-05 语义演进、预选条款废止 |
| D18 | AM 提问零配置 | 激活提问收敛为**单问**（仅代码生成前停点）；问题处理不再询问，**固定 auto-recommended**（AM-04 固定行为化，保留升级路径与轮内显式指示出口）；状态区三行制（Enabled/Code-Gen Hold/Last Updated）、引擎 `autonomous` 键 `{enabled, last_updated}`。取代 D17"双问"表述及 D16"问题处理方式"半句 |
| D19 | 产品交互（原"提问交互三模式"，2026-10-08 其五证伪后重定义） | **头脑风暴阶段 `product-brainstorm`**（RE 后 RA 前，CONDITIONAL，三层门控：condition 散文首跑/scope 矩阵后轮/RA 路由兜底）承载柏拉图式共建设计对话：理解回写 + 分节结晶 + 一次性写盘 product-design.md（含 roadmap 节，自适应深度一页纸下限）；离散决策混用结构化工具；门上设计讨论回写 roadmap（DOC-04）；AM 延迟至 RA 激活；park 不设机制。历史：三模式设计（问题先落文件·chat=收集模式）经 dogfood 证伪回滚。子裁决 D19.1~44（存量 1~34 逐条处置见其六 D19.44，新增 35~44）见 B15 档案 |
| D20 | 迭代交付 | **一个迭代 = 一轮工作流轮次**（再入→完成转移；同产品永不 fresh，版本边界由 git 承载）：WP 产出 `roadmap.md` 模型侧活文档（随门批准；ship 当刻 rollup 压一行、shipped 不可改写、修订三时点 append-only）；拆分判据——硬 H1 下行闭包/H2 可观测结局/H3 全量回归绿+可演示验收（staging/运维交接物为 DoD 占位，Operations 实义化后升格），软 S1 骨架先行~S4 硬化预留，用户显式拆分永远赢、N=1 合法退化、非 classic 默认不拆；完成仪式三分支（下一迭代预览+**人工门绝对**/最后迭代产品级收尾审查/无 roadmap 现行为）；**引擎零改动**——依赖写在制品、迭代计数由 roadmap+git+audit 推导，roadmap 不进 frontmatter produces（双条件产物语义不符+保 --check 零漂移）。子裁决 D20.1~19 见 B16 档案。**〔2026-10-08 全量并入 B15〕逐条处置见 B15 档案其六处置表（D20.2 roadmap 落点、D20.18 produces 语义被取代，余承接）；实施归属改挂 B15，语义以处置表为准** |

### 减法批子系列（D-清1~9，B12 批裁决）

| # | 裁决 |
|---|------|
| D-清1 | 纯减法·语义等价（五类判据：重复副本/路由遗物/墓碑纪事/教学冗余/死文件，无法归类不删） |
| D-清2 | 历史叙事直接删除；仅存量工作区有运行时价值者留一行 |
| D-清3 | 范围=默认上下文优先；opt-in 大文件留下一轮 |
| D-清4 | legacy pre-engine 兼容层留代码批退役（engine.py 零改动） |
| D-清5 | process-overview.md 整删 |
| D-清6 | generate.py 例外三项：REGISTRY 条目删除 + scope-matrix 条件渲染特性（含校验/夹具迁移/契约修订）+ 死渲染函数清理 |
| D-清7 | AWS 世代散文删例子留框架（检测清单词元不动） |
| D-清8 | 路由散文收口专项 |
| D-清9 | **CONDITIONAL 判据唯一权威 = 阶段 frontmatter `condition` 浅映射 `{execute_if, skip_if}`**，生成器渲染进 scope-matrix 生成区权威清单，全部散文判据副本删除；ALWAYS 保持标量双形态校验 |

---

## 3. 批次登记表

> 批次（B##）= 有规格、有实施、有验证的工作单元，按立项顺序编号。**旧称保留在括号内以维持历史引用可溯源**；详情见 `docs/batches/` 对应档案。

| ID | 批次（旧称） | 日期 | 状态 | 决策 | 测试 | 一句话 |
|---|---|---|---|---|---|---|
| B01 | [阶段契约化+生成器](batches/b01-contract-generator.md)（Phase 0/1） | 09-11 | ✅ | D2/D8 | 0→20 | frontmatter 唯一事实源 + generate.py 消除 8 处重复清单 |
| B02 | [scope 裁剪矩阵](batches/b02-scope-matrix.md)（Phase 2） | 09-12 | ✅ | — | — | 6 scope × 14 阶段裁剪矩阵，RA 选 scope + WP 微调；附注含 scope 淡化与扩展重估搁置 |
| B03 | [轻量编排引擎](batches/b03-orchestration-engine.md)（Phase 3） | 09-14 | ✅ | D6修/D7/D9/D10/D12 | 20→77→102 | engine.py 必选引擎 + compile-to-JSON + 状态分区所有权 + 裸项目 dogfood；含 09-15/16 增量 |
| B04 | [会话连续性](batches/b04-session-continuity.md)（Phase 3.1） | 09-22 | ✅ | D13/D14 | 102→144 | park + status 恢复简报 + 传感器第一代（artifact_alerts）+ 分级阅读取代 Load ALL |
| B05 | [Trellis 借鉴立即批](batches/b05-trellis-batch.md)（Phase 3.2） | 09-22 | ✅ | — | 144→169 | Evidence-First 提问纪律 + DOC-06 + RE 可选产物 + B&T Commit Protocol + dogfood 协议 + 契约单测清零 |
| B06 | [dogfood 反馈批](batches/b06-dogfood-feedback.md)（Phase 3.3） | 09-24 | ✅ | — | 169→205 | stamp + autonomous 键 + note_age + checkpoint finding + Type 10 范围收缩 + trace-matrix.py；负债③关闭 |
| B07 | [完成态再入修复批](batches/b07-reentry-fix.md)（修复批） | 09-27 | ✅ | D15 | 205→209 | 完成态同产品演进走就地再入，修四环链路；附注 D15 代价面→5A 观察项 |
| B08 | [AM 生命周期批](batches/b08-am-lifecycle.md) | 09-28 | ✅ | D16 | 209→227 | AM 绑定轮次 + 引擎窄写过期（唯一模型区窄写窗口），三轮审核 |
| B09 | [收尾小批](batches/b09-wrap-up.md) | 09-28 | ✅ | — | 227→231 | fx991 三迭代收官 + Depth 值纯净 + AUD-05 + 组合边界检查项 + 协议泛化 |
| B10 | [AM 简化+Code-Gen Hold 批](batches/b10-am-simplification.md) | 09-29 | ✅ | D17 | 231 | AM-06 移除 + 优雅暂停 + AM-11 停点 |
| B11 | [AM 提问零配置批](batches/b11-am-zero-config.md) | 09-29 | ✅ | D18 | 231 | 激活单问 + AM-04 固定行为化 + 状态区三行制 |
| B12 | [文档减法清理批](batches/b12-doc-slimming.md)（D-清系列） | 09-29 | ✅ | D-清1~9 | 231→237 | 必加载集 -24.5%；判据权威收编 frontmatter；10-06 双臂验收方向性通过 |
| B13 | [备份遗产清理批](batches/b13-backup-legacy.md) | 09-28 立项；**10-09 立场翻转（事后审核已整改）** | ⏳ 待实施 | D11/D14 | 248→249 或不变 | 删除式 v2：6 处改前备份条款直接删 + :136 "(but backed up)" 假陈述修复；engine glob 排除待裁决；`jump --fresh` 安全闸保留；规格就绪 |
| B14 | [文档重组批](batches/b14-doc-restructure.md) | 10-07 | ✅ | — | —（docs-only） | integration-plan 拆分为主文档 + 13 批次档案 + 1 冻结档案，三层体系（Phase/B/D）归一 |
| B15 | [产品头脑风暴阶段批](batches/b15-interaction-modes.md)（原提问交互三模式批，其五证伪重定义） | 10-07 立项；10-08 实施后回滚+重设计 | ✅ 段一+段二已实施·dogfood #1/#2 全程完成（#1 8/8+P7~P12；#2 六项全收：改形全链/AM 全生命周期/中断/放弃语义/N=1+express 纸面走查，P13[P13b 条款落地]/P14[修复] 当场裁决、P11 维持）· 收口提交中 | D19+D20 | 248（237+3+8 规则文本断言） | 头脑风暴阶段 product-brainstorm（三层门控）+ 对话纪律（opsx+superpowers B1~B8）+ product-design.md/roadmap + 迭代交付环与完成仪式（B16 全量并入）；Phase 3.4 重定义产品演进闭环——见档案其五/其六/实施节/验证节 |
| B16 | [迭代交付批](batches/b16-iterative-delivery.md)（Phase 3.4） | 10-07 立项；10-08 并入 | ♻️ 已并入 B15（未实施） | D20 | —（随 B15） | roadmap 活文档 + 迭代作用域 + 完成仪式三分支 + 拆分判据（Trellis parent/child 同构）；D20.1~19 逐条处置见 B15 档案其六，档案保留为 D20 语义之家 |

---

## 4. 现状快照（2026-10-08）

- **引擎**：`scripts/engine.py` 单文件纯 stdlib（约 1800 行），8 子命令（status/init/next/report/jump[含 --fresh]/rebase/park/stamp）；状态分区所有权 + State Digest 完整性校验 + 审计交叉核验。
- **作者期工具**：`generate.py`（1290 行，9 个生成区）编译 `scripts/data/stage-graph.json`；`trace-matrix.py`（追溯矩阵，不进 CI）。CI：contract-check.yml（--check + 全测试套件）。
- **阶段体系**：3 相位 15 阶段（含 product-brainstorm，D19 其六，2026-10-08 段一落地），全部带机器可读契约；6 scope 裁剪矩阵；CONDITIONAL 判据唯一权威 = frontmatter `condition` 浅映射（D-清9）。
- **测试**：248 例全绿（engine 154 + trace-matrix 22 + generate 61 + rule-invariants 11——B15 段一 3 例 + 段二 7 例 + 收口 1 例）。
- **文档负载**：必加载集 73.3KB（B12 前 97.1KB）；SKILL.md 343 行 / 26.6KB。
- **AM 现状**：单问激活（仅 Code-Gen Hold）+ 全阶段自动批准 + 问题 auto-recommended + 轮次绑定过期（D16-D18 链）。
- **dogfood**：fx991 计算器项目累计 6 周期（首周期验收→三迭代收官→双臂减重验收方向性通过）。
- **文件地图**：`.agents/skills/aidlc-workflows/`（SKILL.md + references/{common,inception,construction,operations,extensions}/ + scripts/）；`opencode/`（v2.0 只读参考，权威导览 `AIDLC-PLUGIN.md`）；`docs/`（本主文档 + batches/ + archive/ + engine-illustrated.md + dogfood-protocol.md + result-oriented-delegation-design.md + aidlc-v2-features-vs-v1.md + dogfood-records/[本地保留] + migration-guide.md + blog 草稿）；`aidlc-workflows-cn/`、`opencode-cn/`（中文对应物，只读）。

---

## 5. 未来路线

**分层架构（不变式）**：

```
阶段文件 frontmatter（唯一事实源，engine-ready）
   ├─ B01：scripts/generate.py 读它 → 生成各处人类可读清单
   ├─ B02：scope 矩阵从 scopes: 字段转置生成
   └─ B03：编译为 scripts/data/stage-graph.json → 引擎只读 JSON 做运行时路由/状态
```

关键架构原则：**地基按"未来要盖两栋楼"设计**——后续工作都是消费方的新增，事实源本身永不动工。（D2 否决方案 B 纯注册表的原因：引擎需要每阶段自声明的契约，注册表路线仍需回头补 frontmatter，属重复改造。之所以不是"引擎先行"：引擎前提是机器可读契约；引擎解决"谁来路由"但不自动解决文档清单重复；契约先行让各批独立可交付。）

### Phase 3.4：Product Evolution Loop（产品演进闭环，2026-10-07 立项为迭代交付，2026-10-08 重定义）

**重定义（2026-10-08）**：B15 dogfood 证伪引发重设计——B16 全量并入 B15，相位更名**产品演进闭环**，一句话定位：非技术用户从一句话许愿到长期演进产品的完整闭环（头脑风暴阶段 + roadmap 活文档 + 迭代交付环 + 完成仪式）。首批 = 合并批 B15（暂唯一）。

**立项动机**：一句话需求场景下一次性长程实施只产出 demo 而非可持续演进的真实产品（执行秩序断裂 + 质量门末端压缩）。战略层（头脑风暴）+ 执行层（迭代分片）合为闭环，先行缩小 Phase 4 多会话协调爆炸半径。

**批次构成**：B15 产品头脑风暴阶段批（头脑风暴阶段 + 迭代交付环全量合并，含 B16 吸收）→ B18+ Operations 实义化（部署/监控/告警/回滚——"线上持续运行"唯一通路，开放项挂账；原"B17+"因 B17 被外线合流批占用而顺延）→ 远期遥测回灌（运行反馈驱动 roadmap 修订，依赖前两者）。

**设计原则（B16 确立、B15 继承，后续批次沿用）**：引擎零改动（依赖写在制品；复用 D15 再入通道为迭代正规通道）；迭代边界 = 人工检查点（决定归人类，v1 无 AM 自动续迭代）；rollup 前置（ship 当刻压一行）；**头脑风暴阶段 = 纯人类领地**（AM 延迟至 RA，任何机制不替用户做产品决定）。

**与 Phase 4 的关系**：正交——迭代 = 垂直时间切片，unit-major 波次 = 单轮构造内水平并行；Phase 4 设计输入⑥（parent/child）的"树不是依赖系统"原则已由 B16 在迭代维度先行操作化，其 D11 张力在迭代维度由 D15 消解（同产品多迭代 = 同一意图多版本），Phase 4 若引入跨意图任务树仍届时裁决。

### Phase 4：Team Construction

**硬依赖链（顺序不可乱）**：单元清单结构化（B03 ✓ 已交付）→ unit-major → claim → merge。每一步都以 unit-major 为前提：没有引擎感知单元就没有可认领的对象，没有 claim 锁多会话就是状态文件互踩。

**前置批 B17 外线合流与傻瓜化（2026-10-09 规格就绪·待排期，详见 batches/b17）**：串行合并语义——外线变更（自助 hotfix worktree 线 / 他人分支 / 另一迭代交付线）合流回当前线的五步协议（git 合并→制品对账→续作判定→一致性核对→恢复执行）+ 想法进入流傻瓜化（P1 机制隐身：路由判断归模型，台前只有产品语言）。零引擎改动，不依赖下方链条任何一步，可独立先行；其串行对账语义即第 2 步 claim/release 并发协调的地基——届时只加并发分配（FR 命名空间/分配器）与争用锁。执行顺序由用户定（2026-10-09 暂缓，有更优先排期）。

1. **unit-major 波次编排**（地基，本身即可交付价值）：`report --unit`、Unit Progress 区启用、单元级审批门节奏（per-stage / unit-end 两种）、单元级恢复。stage-major 保留为默认节奏。**随此项一起做**：指令中的 `consumes` 条目增加计划感知标注（如 `producer_skipped: true`），把 stage-contract §2 "生产者被跳过则 moot" 的语义在指令层面显性化
2. **claim/release + git worktree**（形态 A：多会话团队，harness 无关）：claim 粒度 = unit；所有协调逻辑在引擎。状态文件多会话并发写锁是实现期重点（参考 v2.0 mkdir 锁）。**Trellis 前车之鉴**：其曾实现后又删除 worktree 管理（复杂度收益比不佳）——引入前先评估，能靠 claim 锁 + 目录约定解决就不上
3. **single 单阶段重跑**（~50–100 行）：`next/report --single`，独立审计对、绝不动主指针。用户场景：team 并行试验多个算法变体 → 选定其一单独重跑
4. **swarm 进程内并行**（形态 B：harness 相关，依赖 subagent 能力，可再拆）

**Trellis 设计输入（2026-09-22，源自 B05 四档清单③档，进入本相位设计时逐项核对）**：① 上下文策展清单——派遣文件清单须 `{file, reason}` 二元组 + 字节预算 + 禁预注册代码文件；② 派遣三件套——Active task 首行约束 + 递归守卫 + 任务注入标记-or-回拉双通道；③ channel 事件日志 vs claim 注册表对照——协调状态放文件而非聊天流；④ 单元依赖显式写在工件（units.md 依赖列）；⑤ spec 移植模式——上游规格可整体移植进单元工件。

**Trellis 二次吸收设计输入（2026-10-07，对照源 brainstorm/task-system，忠实度经 reviewer 核验）**：⑥ parent/child 任务树——父任务持需求源/任务映射/跨子验收/终集成审查，子任务独立可验证可归档，**树不是依赖系统**（依赖写进子任务制品、不靠树位置隐含；与 D11"一版本一意图"的张力届时裁决）；⑦（低优先）Journal 会话日志——per-developer、2000 行自动轮转、title+commit+summary 三元组，作多会话/park 增强参考。

**dogfood 反馈移入项（2026-09-24 挂档，与 Trellis 输入并列）**：

1. **AM 状态注记化**（`am --on/off` 或等价机制）——AM 状态切换走引擎注记动词：digest 覆盖（当前 `## Autonomous Mode` 区模型手写，两会话并发修改互踩且不可检测）、per-claim 并发语义。**必须与 claim 并发锁同批设计**（AM 是全局还是 per-claim？两会话配置不一致以谁为准？）。B08 已先行落地两边界窄写（D16），本项收编该窄窗口并二次修订契约 §6；slug 校验子项已随 B10 的 AM-06 移除作废；Code-Gen Hold 行（模型写-模型读通道）收编时一并评估是否引擎化
2. **per-unit checkpoint 锚点**——`unit-{unit-name}-checkpoint.md` 存在性检测（B06 只做了两条全局锚点）。依赖第 1 步 Unit Progress 启用。unit checkpoint 同时是跨会话交接核心载体
3. **checkpoint 契约化（层 2，可选，视证据决定）**——阶段 frontmatter 条件产物声明 → 编译进 stage-graph.json → 复用 produces_missing 软警告管线。**前置**：checkpoint-missing finding 跑一个 dogfood 周期，误报率可接受才立项；construction 锚点以 `_is_done` 判定完成与 build-and-test 被跳过场景的张力届时一并评估
4. **CTX 去留最终裁决**——多会话 dogfood 中做最终裁决。评估点：跨会话交接里 checkpoint 的实际价值、与知识树（Phase 5A）的分工。fx991 三周期"产出未消费"观察（B09）为输入
5. **多会话范围变更语义（设计期开放问题，非必做）**——"一个会话砍需求、其他会话有进行中工作"的失效通知/回滚语义（jump 重置与 claim 锁的交互）在 claim 设计时一并考虑

**架构原则（长期适用）**：扩展的判断与决定留在规则文本，扩展的**精确部分**（状态、时机、存在性、时间戳）才下沉引擎——"扩展进引擎"以此线为准，防止扩展生态污染引擎纯度（层 3 完全收编明确不做）。

### Phase 5A：单层活知识树与学习闭环（Phase 4 后、5B 前；骨架见 B05 规格）

- 知识树：`aidlc-docs/knowledge/<domain>/index.md`（index 只路由不存内容）；条目 frontmatter 预留 `governs:`
- 写入仪式双触发（B&T 收尾自问 + 复盘触发器——模型判定、同单元连续失败计数窗口、跨会话 best-effort 续）+ 学习双出口（约定→知识树条目 or→传感器提案[D14 finding 形态]）
- knowledge_refs：按 `task`/阶段声明需要加载的知识引用；完整设计见 `docs/result-oriented-delegation-design.md`（现为"讨论记录待并入"状态，Phase 4 设计输入第 6 项处理并入/延后）；空树期回退引用 RE working-conventions 与既有规则文件
- 种子关系：RE working-conventions.md = 知识树初始种子/导入源，唯一"约定"存储为知识树

**观察项：活文档单文件单调增长与 rollup 规程（dogfood 实证后再设计，讨论全录见 B07 附注）**——单树活文档模式的代价面。触发条件：dogfood 中核心活文档过 500 行，或再入/设计场景全量读 stories.md 产生可感知的上下文压力。届时方向：shipped-stable 条目 rollup 为一行索引（编号 + 标题 + 一句话 + git commit 指针），编号永不回收；DOC-06 升"超线必做"评估。首批实证（fx991：stories.md 356 行、requirements.md 自发 rollup，两制品不对等提示分治）见 B09。

**Trellis 二次吸收设计输入（2026-10-07，对照源 update-spec/break-loop/spec index，忠实度经 reviewer 核验）**：① 知识树 index 采用 Pre-Development Checklist 触发式路由（按任务特征 → 具体条目文件，强于纯链接索引）；② Code-Spec vs Guide 二分——"怎么安全实现"（条目）vs"写前想什么"（guide 为指向条目的短清单，不复制规则）；③ 七类条目模板（Design Decision/Convention/Pattern/Forbidden Pattern/Common Mistake/Gotcha 等，各带固定骨架）；④ 写入仪式强度备选：required·once 门（每任务收尾必走）——无 breadcrumb 载体，**仅作软强度标记**；⑤ break-loop 五维归因（根因五分类/修复失败四因/预防机制六型/系统性扩展/知识捕获）与贝叶斯排查框架（先验→证据→更新→区分性证据→置信分级行动）作学习闭环输入。

### Phase 5B：reviewer 及其他（逐项独立可交付，纯增量无返工）

- reviewer 状态机（启用契约 §5 预留字段 reviewer/review_artifact/reviewer_max_iterations）
- 传感器自检清单 → report 时阻塞校验（required-sections / upstream-coverage / traceability / claim-sources；fire 点与 finding 接口已由 D14 预定）
- persona 体系（轻量版 inline 扮演先行；完整版另议）
- 五层记忆 + §13 学习仪式（与 5A 关系——5A 先交付项目级单层闭环，五层届时复用其条目模板与写入仪式）
- 门仪式精细化（HARD STOP、revision 逃生舱、non-matching reply 处理）
- 完成消息 5 段契约、声音/沉默规则、PRE-GENERATION SUMMARY STOP 强化
- **report+next 合并评估**（2026-09-15 结论：不合并——破坏 CQS 边界；**仅当** Phase 4 多单元循环使转移次数成倍增长、编排开销成为真实痛点时再议，届时形态为 `report --and-next` opt-in 标志）

### 不排期（仅记录）

- **多 intent / compose**（D11）：一版本一产品意图；重启前提与 Team Construction 协同设计——claim 注册表天然按 intent 隔离；`aidlc-docs/` 路径需加 intent 维度，属目录结构级重构，所有后置项中侵入最深
- **Trellis ④档三项**（触发条件出现再议）：**技能版本戳**（技能分发/多版本共存场景）；**模板升级保护**（用户本地定制模板与上游升级冲突场景）；**evidence-first 扩展范式**（将 evidence-first 纪律推广为扩展作者的结构性模板；≠B05 WP-1 提问纪律）

---

## 6. 开放项总账

> 单行指针纪律：本表每行一句话 + 出处，永不展开散文。项被立项为批次后，本行改指批次档案。

| 项 | 状态/触发 | 出处 |
|---|---|---|
| B13 备份遗产清理批 | ⏳ 规格就绪·**删除式 v2**（2026-10-09 立场翻转：非 git 工作区亦不留 `.backup`——历史只由 git 承载，无 git 不记；`jump --fresh` 安全闸保留），可开工 | batches/b13 |
| B15 产品头脑风暴阶段批（含 B16 合并） | ✅ 段一+段二已实施；dogfood #1/#2 **全程完成**（#1 2026-10-08：8/8+P7~P12 与提问不可免定律；#2 同日：改形再入全链/AM 延迟+Hold+轮末过期全生命周期/中断放弃语义/N=1+express 纸面走查六项全收——发现 P13[回合边界条款]、P14[B&T 规则 3 条件] 均当场裁决落地，P11 维持；《棋伴》迭代 2 本机双人 shipped：49/49、E2E 五景、56.45 kB） | batches/b15 |
| B16 迭代交付批（Phase 3.4 首批） | ♻️ 已并入 B15（未实施，2026-10-08 全量合并——处置见 B15 其六） | batches/b16 |
| B17 外线合流与傻瓜化批（Phase 4 前置：外线变更五步合流协议 + 想法进入流 + P1 机制隐身） | ⏳ 规格就绪·待排期（2026-10-09 用户暂缓，有更优先排期；零引擎改动可随时先行；含事前审核已整改收口 + dogfood #3 草案） | batches/b17 |
| 全量去术语化：P1 机制隐身推广到既有 Type 1~10 用户话术与恢复菜单（B17 实施时既有文本不动） | 待 B17 实施后评估 | B17 计划审核 P1 处置 |
| Operations 实义化（部署/监控/告警/回滚——"线上持续运行"通路；B16 DoD 占位字段待升格） | Phase 3.4 第二批候选（B18+） | B16 立项 |
| 阶段规则审查透镜：强制步骤必须在当阶段实际加载的文件里有锚点，否则被静默跳过（Trellis breadcrumb 不变量，两次事故实证） | 观察项（批次审查时核对） | B15 规格修订 |
| bugfix scope 增强：break-loop 五维归因 + 贝叶斯排查框架移植（error-handling 或 scope 材料） | 低优候选 | B15 规格修订（Trellis C-4） |
| 代码批·旧格式兼容层退役（legacy 分支/宽容解析/旧格式夹具三层一体） | 前提=确认无 pre-engine 存量工作区 | B12 后续登记① |
| 代码摸底批（engine.py/generate.py/trace-matrix.py 同款减法） | 可选 | B12 后续登记② |
| opt-in 大文件减法（resiliency 28K/security 18K/PBT 18K） | 下一轮 | B12 后续登记③（D-清3） |
| 扩展配置成熟度重估（M1-M4 信号方案已细化） | 搁置，待 Operations 补全 | B02 附注二 |
| 引擎 Windows 自由文本参数通道（`--note-file`/`--reason-file` 或编码约定） | 改进排队（三会话复发） | B12 验收发现① |
| 引擎 emit 按 frontmatter scope 预剪枝 | 改进排队 | B12 验收发现② |
| consumes `required:true` × scope 剪枝组合语义 | 待 stage-contract 澄清 | B12 验收发现③ |
| dogfood-protocol §零 STAMP 惯例 + 副本记录卫生 | 改进排队 | B12 验收发现④ |
| 部署卫生：fx-991 主项目 `.agents` 快照更新至当前技能 HEAD | 待办 | B12 验收 |
| 观察项（多周期阴性方可关闭）：指针化阶段块加载遗漏；produces_missing 持续零触发；判据锐度（UG/FD 边界靠模型裁量） | 观察中 | B12 验收 |
| Phase 5A 活文档 rollup 观察项 | 触发：核心活文档过 500 行或可感知上下文压力 | B07 附注 + B09 |
| B04 负债清单 9 条（①②④⑤⑥⑦⑧⑨ 开放；③已关闭 2026-09-24） | 详见档案 | B04 规格·负债 |
| B05 负债六项（①②③未决；④登记表漂移风险已对冲；⑤消融无引擎臂违宪=永久；⑥已消解） | 详见档案 | B05 遗留 |
| OWASP "2025" 版本存疑 TODO（security-baseline.md:295，B01 时代遗留） | 开放（处置承诺见 b01） | b01 规格·补充说明 |
| B02/B03 档案内部遗留小项：infra brownfield RE=SKIP 代价提示；scope depth enum 是否加 `adaptive`（Phase 4+）；B03 P3 观察项 4 条（planned_skip 分支不可达 / jumped 豁免未入契约 / END 标记文档语法不符 / CRLF 混行尾） | 详见档案 | B02 审核·遗留 / B03 审核 |
| B01 复审/审查遗留 backlog 未销项（解析器未闭合引号、--check 未注册文件逃逸、Type 9 决策树分支、隐式单单元注记遗漏、规则 16 豁准面[Phase 4 扩 scope 前处理]、--check 重复 key 逃逸×2、保留键报错信息、中缀 glob 约定、Operations CONDITIONAL 语义[Phase 4+]、welcome ASCII 截断保护、"13 vs 17 个 GENERATED 标记区"计数口径待校正） | 详见档案 | B01 |
| error-handling 补 WinError 5 条目 | 低优，暂不动 | B09 观察项④ |
| audit 引擎 append 动词 | Phase 4/5 输入（D13 交互矩阵成本） | B09 观察项⑤ |

---

## 7. 维护规程

### 三层体系与判定规则

| 层 | 本质 | 寿命 | 判定测试 |
|---|---|---|---|
| **Phase（战略）** | 意图的方向（要往哪盖楼） | 长，多批次覆盖 | 是不是一个需要多个工作单元才能实现的战略方向？ |
| **B##（批次）** | 干活的单位（何时做了什么） | 一次性，完成即冻结 | 是不是一次有规格、有实施、有验证的仓库变更？ |
| **D##（决策）** | 语义的锚点（为什么是这样） | 永久，被取代不删除 | 是不是一条未来工作必须遵守的裁决/约束/取舍？ |

新工作依次四问：① 含必须遵守的语义裁决吗 → 登记 D（可零实施，如 D11）；② 是路线图既有相位的一部分吗 → 相位分解出的批次；③ 是需要多批次的全新战略方向吗 → 先在 §5 立新相位再分解；④ 都不是（dogfood/用户即期需求）→ 独立批次，触发注明来源。

转化关系：Phase 开工时必然物化为一个或多个 B（Phase 4 将来 = B17+，B15/B16 已被占用）；D 永不"变成"B——D 被 B 实施（或永不实施），D 约束 B；B 实施中可产出新 D（B03 产出五个 D）。**同一主题可在三层各有存在**（如 AM：D16-D18 语义链、B08/B10/B11 已执行批次、Phase 4 输入中的战略遗留），三者靠登记表与取代链互引，不追求归并为一个条目。

### 批次生命周期

1. **立项建档**：`docs/batches/b<NN>-<slug>.md`（状态：待实施），按统一模板预置七节（立项与裁决/规格/实施与实施期裁决/验证/实施后审核与修复/遗留与去向/附注，**节可按材料有无裁剪**）；§3 登记表加一行。
2. **过程中追加**：计划审核、用户裁决、实施期裁决随发生随追加进档案对应节。
3. **完成归档（零文件搬移）**：档案翻转状态 `待实施 → ✅ 已完成（日期）`，补齐实施/验证/审核/遗留四节；登记表该行更新（状态/测试基线/一句话）；产出新决策则 §2 加行；新遗留/观察项 §6 加行，已解决项划销。
4. **历史档案冻结**：已完成的批次档案原则上只追加"附注"（后继批次对它的补充裁决），不改正文；原文保留优先，仅在明确重复处二选一。

### 纪律

- **单行纪律**：§2 决策表、§3 登记表、§6 总账只放单行（决策表条目本身除外），永不展开散文——否则长成第二个变更流水账（旧 §9 的老路）。
- **指针同步**：§2/§3 出现新 D##/B## 编号时（立项或完成时点皆然），同步根 `AGENTS.md` 导语的决策/批次区间指针（D…-D…、B01-B…）——该指针无其他 Owner，漏同步即留错（2026-10-07 B15 立项实证，当日补修）。
- **主文档红线 350 行**：触线即触发减法评审（候补减法：已完成批次的表格行合并、路线图节收缩为指针）。
- **非批次讨论**：改既有交付物的讨论 → 追加相关批次档案"附注"节；悬而未决 → §6 总账一行；日期化叙事文档（blog 草稿）的历史性提及不适用引用纪律。
- **引用纪律**：本文与批次档案引用的仓库内文件必须存在于 git 跟踪中，失联时在引用处标注"已佚"；冻结档案与历史叙事文本中的历史性提及豁免（引用对象以写作时点为准）；`docs/dogfood-records/` 为本地保留目录（.gitignore，不入 git），引用其内容时标注"本地保留"。
- **语言**：技能文件（SKILL.md、references/）用英文；docs/ 下工作文档用中文。
