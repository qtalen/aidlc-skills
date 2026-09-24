# engine.py 实现图解

> **阅读对象**：第一次接触本仓库的新成员——不要求了解 AI-DLC，只要懂基本编程概念（函数、命令行、JSON、哈希）就能读完。
> **配图规范**：所有示意图只用 `+ - | ^ v < >` 和空格绘制（与本仓库 `content-validation.md` 的 ASCII 图规范一致），无 Unicode 制表符。
> **深入阅读**：本文是导览；权威契约见 `references/common/engine-contract.md` 与 `references/common/stage-contract.md`，行号以当前 `scripts/engine.py` 为准（约 1650 行）。

---

## 0. 开始前：几个名词

| 名词 | 大白话解释 |
|---|---|
| **引擎** (`scripts/engine.py`) | 一个纯 Python 标准库写的命令行小工具，负责"流程走到哪了"这件事的记账和裁决 |
| **工作区** (workspace) | 被开发的项目所在目录，引擎在其中创建 `aidlc-docs/` |
| **状态文件** (`aidlc-state.md`) | 工作区的"进度存折"：走到哪个阶段、哪些做完了、完整性指纹 |
| **审计文件** (`audit.md`) | "银行流水"：只追加、不修改的事件日志 |
| **阶段** (stage) | 工作流的一步，比如需求分析、代码生成；有 14 个 |
| **模型** (AI model) | 负责干活的 AI：做判断、写文档、回答问题 |
| **digest**（指纹） | 对一段文字算出的 sha256 哈希值。内容哪怕改一个字符，指纹就完全不同——用来发现"有人偷偷改过文件" |
| **图** (`stage-graph.json`) | 编译产物：把 14 个阶段的规则压缩成引擎好读的一张 JSON 地图 |

记住一句话就够了：**判断归 AI，精确归工具，决定归人类。** 引擎就是那个"工具"。

---

## 1. 全景：谁编译、谁判断、谁执行

```
AUTHORING TIME (offline, in-repo)
+------------------------------+
| references/<phase>/*.md      |
|   YAML stage frontmatter     |
|   slug/execution/gate/scopes |
|               |              |
|               v              |
|     scripts/generate.py      |
|               |  compile     |
|               v              |
|     scripts/data/            |
|       stage-graph.json       |
+------------------------------+
         ^
         |  engine reads ONLY this compiled graph.
         |  It never parses frontmatter or condition prose;
         |  generate --check (CI) guards drift.

RUNTIME (every session)
+------------------------------------+
|              AI model              |
|  judgment: Execute-IF / SKIP,      |
|  scope pick, question files,       |
|  artifacts, gate presentations     |
+-----------------|------------------+
                  |  reads stage rules, writes artifacts,
                  |  and calls the 8 engine verbs (below)
                  v
+------------------------------------+
|         scripts/engine.py          |
|  precision: routing, transitions,  |
|  digest, audit, park, stamp        |
|  (Python 3.8+ stdlib only)         |
+-----------------|------------------+
                  | atomic read/write
                  v
+------------------------------------+
|             aidlc-docs/            |
|   aidlc-state.md     audit.md      |
|   handoff.md (engine-only writer)  |
+------------------------------------+
```

### 这张图在画什么

图分上下两半，对应引擎的两种人生：**作者期**（开发者改规则时）和**运行期**（AI 带着用户干活时）。

**上半：AUTHORING TIME（作者期）**

- 每个阶段的规则写在 `references/<phase>/*.md` 里，文件**开头**有一段用 `---` 包起来的 YAML 元数据（叫 frontmatter），声明这个阶段叫什么、是否必做、有没有审批门禁、各适用场景下执行还是跳过。人写规则就写这一处。
- `scripts/generate.py` 是"晒图车间"：把所有 frontmatter 编译成一份机器友好的 `scripts/data/stage-graph.json`。这一步叫**编译**——把人喜欢写的格式变成程序喜欢读的格式。
- 编译产物受双重保护：开发者跑 `generate.py --check` 能发现"规则改了但没重新编译"的漂移，CI 在 push 时也会自动查。

**下半：RUNTIME（运行期）**

- **AI 模型**做所有需要动脑的事：判断某个条件阶段当前适不适用、选定工作场景（scope）、写需求文档、向用户提问。
- **引擎**做所有不需要动脑但需要绝对精确的事：路由（下一步该做哪个阶段）、状态转移（把某阶段标记为完成）、完整性校验、记账。模型每次调用引擎就是执行一条命令行，引擎回一个 JSON。
- 引擎对 `stage-graph.json` **只读**，对 `aidlc-docs/` 下的三个文件做原子读写。

### 为什么这样设计

关键在图中间那句箭头注释：**引擎只读编译产物，永不解析 frontmatter，也不解析散文条件。**

打个比方：stage 规则是建筑图纸，`generate.py` 是晒图车间，`stage-graph.json` 是装订成册的标准图集。引擎是施工监理——监理只认盖章的图集，不认工头口头转述的"图好像改了"。这样规则解析出错的概率被压缩在编译期一处（作者改规则时当场就能发现），运行期引擎读到的永远是结构化、已校验的数据。

另一个细节：`(Python 3.8+ stdlib only)`——引擎只用 Python 标准库，零第三方依赖。用户拿到技能就能跑，不需要 `pip install` 任何东西。

### 一句话类比

> 图纸（frontmatter）→ 晒图车间（generate.py）→ 标准图集（stage-graph.json）→ 施工监理（engine.py）照图集监理施工队（AI model）干活，进出货都要记账（aidlc-docs/）。

---

## 2. 状态文件分区所有权

```
aidlc-state.md
+--------------------------------------------------------------+
| MODEL-OWNED ZONE (outside the ENGINE-STATE markers)          |
|   ## Project Information / ## Workspace State                |
|   ## Execution Plan Summary                                  |
|      - Scope: classic      - Depth: standard                 |
|      - Stages to Execute / Stages to Skip                    |
|   ## Extension Configuration   (| CTX | No |)                |
|   ## Autonomous Mode           (Enabled: No ...)             |
|==============================================================|
| <!-- BEGIN ENGINE-STATE -->   ENGINE-EXCLUSIVE ZONE          |
|   ## Stage Progress    - [ ]/[x]/[S]/[R]/[?] <slug>          |
|   ## Current Status    Current Stage / Last Parked           |
|   ## Unit Progress     per-unit marks                        |
|   ## State Digest      sha256: <64 hex>                      |
| <!-- END ENGINE-STATE -->                                    |
+--------------------------------------------------------------+

model-writes -> engine-reads channels (tolerant, junk degrades to null):
  _parse_plan()       engine.py:293   scope/depth/skip drive effective_stages()
  _ctx_enabled()      engine.py:779   gates the checkpoint-missing sensor
  _parse_autonomous() engine.py:730   feeds the status "autonomous" key
```

### 这张图在画什么

一个 `aidlc-state.md` 文件被一道 HTML 注释标记（`<!-- BEGIN/END ENGINE-STATE -->`）切成两个"租区"：

**上半区：模型专属。** 项目信息、工作区扫描结论、执行计划摘要、扩展配置、自主模式开关——都是 AI 按模板自由填写的业务内容，引擎**从不改写**。

**下半区：引擎专属。** 阶段进度勾选表、当前阶段、单元进度、完整性指纹——只有引擎能写，模型手改这里会被完整性校验当场抓住（见第 5 节）。

**三条特殊的"模型写、引擎读"通道**（图下方的注释）：模型在上半区写的三个结构化信息，引擎会读：

1. `_parse_plan()`（engine.py:293）：读"选了哪个 scope、哪些阶段跳过"——这是引擎算出"接下来该做哪个阶段"的依据。
2. `_ctx_enabled()`（engine.py:779）：读扩展配置表里 CTX（上下文检查点扩展）开没开——决定要不要做 checkpoint 检查。
3. `_parse_autonomous()`（engine.py:730）：读自主模式区——喂给 `status` 输出的 `autonomous` 键。

注意"tolerant, junk degrades to null"（宽容解析，坏数据降级为空）：这三条通道读取时**不挑刺**——格式不对、缺字段、写了乱码，引擎不报错，当作"没配置"处理。因为这些区归模型所有，引擎若因区外内容报错，就等于侵犯了自己不该管的辖区。

### 勾选标记速查

进度表每行前面的方括号是一个字符的"印章"（engine.py:70-74）：

| 印章 | 含义 |
|---|---|
| `[ ]` | 还没做（pending） |
| `[x]` | 做完了（completed 或门禁获批 approved） |
| `[S]` | 跳过（skipped，附理由） |
| `[R]` | 门禁被否（rejected） |
| `[?]` | 需要修订（revised） |

### 一句话类比

> 合租公寓的记事本：公共区（上半）谁都能写；带锁抽屉（标记区）只有管理员（引擎）能开。管理员还会从公共区**抄录**三行关键信息（scope/CTX/自主模式），抄的时候很宽容——看不清的字迹就当没写。

---

## 3. 八个动词，按层分工

```
+-------------+----------+-----------------------------------------------+
| layer       | verb     | effect                                        |
+-------------+----------+-----------------------------------------------+
| setup       | init     | create state + audit files (STATE_CREATED)    |
| transition  | report   | the only transition write entry (5 results)   |
| transition  | jump     | re-point current; --fresh archives aidlc-docs |
| annotation  | park     | Last Parked + handoff.md only                 |
| read        | status   | recovery briefing + artifact sensors          |
| read        | next     | emit run-stage directive for current stage    |
| read        | stamp    | authoritative UTC timestamp; zero side effects|
| repair      | rebase   | replay audit transitions into the region      |
+-------------+----------+-----------------------------------------------+
```

### 这张图在画什么

模型操作引擎一共只有 8 个子命令（动词）。这张表按**能改什么**给它们分层：

- **setup（建立）**：`init` 开户，创建状态文件和审计文件，属于一次性的。
- **transition（转移）**：只有 `report` 和 `jump` 能改变"当前阶段"。这是**封闭集合**——除此之外没有任何途径能挪动进度指针。`report` 是常规流转（做完/跳过/门禁通过……），`jump` 是改道（换路线走，`--fresh` 还能把旧 `aidlc-docs/` 归档重开）。
- **annotation（注记）**：`park` 是"临时停车留条"。只往状态文件写一行 Last Parked、往 `handoff.md` 追加一段话，**不碰**进度标记和当前阶段，**不写**审计。会话要中断时用它，下次恢复一看便知停在哪、接着干什么。
- **read（读）**：`status` 出具"恢复简报"（停在哪、最近发生了什么、有什么警报）；`next` 回答"下一步干什么"；`stamp` 只报权威 UTC 时间戳，**零副作用**——模型写审计需要时间戳但本次交互又没调过别的引擎命令时，就用它补一个可信时间。
- **repair（修复）**：`rebase` 是保修通道：状态文件被手改坏时，以审计流水为准重放（replay）修复标记区（详见第 5 节）。

### 为什么这样设计

动词分层（D13 纪律）的本质是**权限最小化**：想改进度？只能走 `report`/`jump` 这扇门，而门后有四道验证关卡（下一节）；只想留个便签？`park` 物理上就摸不到进度数据。一个动作能改什么，由它用的动词决定，而不是由调用者小心不小心决定。

### 一句话类比

> 电视遥控器：换台键（report/jump）、贴便签键（park）、看时钟键（stamp）各管各的——按"看时间"永远不会把频道弄乱。

---

## 4. `report`：唯一转移写入口的流水线

```
report --stage <slug> --result <R> --reason <why>
   |
   v
_validate_transition()                                   engine.py:1216
   |-- [1] slug in graph? ..................... no -> EngineError unknown-stage
   |-- [2] gate coupling:
   |       gate != "none"  and R == completed .......... -> error (use approved)
   |       gate == "none"  and R in {approved, rejected, revised} -> error
   |-- [3] R == skipped requires ALL of:
   |       execution==CONDITIONAL OR scopes[plan.scope]==CONDITIONAL
   |       OR slug in plan.skip        AND  --reason present
   |                                             ...... else -> error
   |-- [4] slug == current_stage()? ........... no -> error (only current reports)
   |
   v
marks[slug] =  completed:[x]  approved:[x]  rejected:[R]  revised:[?]  skipped:[S]
parked = None          # a transition supersedes any park note
   |
   v
_splice_region()  ->  rewrite ENGINE-STATE region (marks / current / digest)
_write_text_atomic(aidlc-state.md)          # temp+replace, never torn
   |
   v
_audit_append(EV_FOR_RESULT[R], stage, reason)     # append-only
   |
   v
R in {completed, approved}? --> produces_missing soft probe   # fail-open
   |
   v
JSON ack {"kind":"reported", "current_stage": <next pending>}
```

### 这张图在画什么

`report` 是整个系统**唯一**的常规进度写入口，全部逻辑是一条流水线：

**四道验证关卡**（`_validate_transition()`，engine.py:1216）：

1. **查票**：阶段名（slug，如 `requirements-analysis`）必须在图里存在。
2. **票种匹配**：带审批门禁（gate）的阶段**必须**用 `approved`/`rejected`/`revised`——不允许用 `completed` 蒙混过关；没门禁的阶段正好相反。这把"该让人拍板的事必须让人拍板"焊死在代码里：AI 想跳过用户审批？引擎直接拒绝。
3. **跳过资格审查**：`skipped` 不是想跳就跳——只有"条件阶段"（CONDITIONAL）、当前 scope 下被裁剪成条件执行的阶段、或计划里显式列入跳过的阶段才允许跳，且**必须给理由**。必做阶段想偷懒，引擎会让你改走 `jump`（人类决定的改道），而不是静默跳过。
4. **本人办理**：只能 report **当前**阶段。不能跳着报、不能补报很久以前的。

**盖章与记账**：四关全过后——

- 按结果盖印章：`[x]` / `[R]` / `[?]` / `[S]`（对应关系见图中那行）。
- `parked = None`：一旦有正式转移发生，之前的停车便签自动作废（你已经重新上路了，便签没意义了）。
- `_splice_region()` 重写引擎专属区（进度表 + 当前阶段 + 重新计算指纹），`_write_text_atomic()` **原子写**入盘。
- `_audit_append()` 往审计流水追加一条事件，附上理由。

**出门提醒（fail-open）**：完成/获批后，引擎顺手检查一下这个阶段承诺要产出的文件（frontmatter 里的 `produces`）是否真的存在，缺了就在 JSON 回执里带一句 `produces_missing` 软警告。它是 try/except 包着的——检查本身出任何错都**静默放行**，绝不因为"提醒"失败而堵死唯一写入口。

**回执**：JSON 告诉模型"记上了，现在轮到哪个阶段"。`current_stage` 的算法很简单：按计划顺序找第一个还是 `[ ]` 的阶段（engine.py:688-700）。

### 名词解释：原子写、append-only、fail-open

- **原子写**：先写临时文件，写成功后再一步替换正式文件。哪怕中途断电，也不会出现"半截文件"。
- **append-only（只追加）**：审计文件只能往后加，永不改写历史。账本不能撕页。
- **fail-open（故障放行）**：辅助功能出错时不拦截主流程。传感器可以坏，大门不能锁死。

### 一句话类比

> 机场登机口：查有没有这趟航班[1]、查票是不是对应这个口[2]、查你有没有资格走这个通道[3]、查是不是你本人的票[4]——全过才盖章，盖完写登机记录，出门时广播提醒一句"您可能落下东西了"（但不拦你）。

---

## 5. 完整性三角：digest / 审计交叉核验 / rebase

```
   ENGINE-STATE region                        audit.md
 (marks / current / digest)            (append-only, engine-only)
           |                                     |
           v                                     v
 [1] _digest_of_region()              [2] _audit_transition_events()
     sha256(region minus digest line)      parse transition entries
           |                                     |
           +------------------+------------------+
                              |
                              v
                   check_integrity()          engine.py:595
                   [1] recomputed digest == stored digest?
                   [2] marks set == audit transitions set?
                              |
              +---------------+---------------+
              v                               v
         both pass                        mismatch
      integrity: ok                  tampered / out-of-band edit
                                            |
                                   repair: rebase (engine.py:1405)
                                   replay audit transitions back
                                   into the region + new digest
```

### 这张图在画什么

状态文件是普通 Markdown——人随时能用记事本打开它。怎么防止"有人手改进度表作弊"？答案是**两道互相独立的证据链**，每次状态操作前都交叉核验（`check_integrity()`，engine.py:595）：

**证据链 [1]：内容指纹（digest）。** 引擎专属区的文字内容（除指纹行本身）被算出 sha256 哈希，存在指纹行里。下次操作前重新算一遍：文件被改过哪怕一个空格，重算的哈希就对不上存的哈希——当场识破。

**证据链 [2]：审计交叉核验。** 每一次合法转移都会在审计流水里留一条事件。引擎把审计里的转移事件解析出来，和进度表里的印章**逐一对账**：进度表说 `requirements-analysis [x]`，审计里就必须有一条对应记录；多一枚章、少一枚章、章对不上事件，都算账目不符。

两道链条抓的是不同的贼：[1] 抓"改了内容"的，[2] 抓"绕过引擎伪造记录"的（哪怕连指纹一起重新算好，审计里没有对应流水，照样露馅）。

**修复通道：`rebase`。** 对不上账怎么办？以审计流水为准——审计是 append-only、引擎独写的，比状态文件更可信。`rebase` 把审计里的转移历史重放一遍，重建整个进度区和指纹。相当于"存折丢了，拿银行流水重新补一本"。

### 一句话类比

> 存折（状态区）和银行流水（审计）必须能对上账：存折上有笔迹防伪（digest），流水只在银行发生真实交易时记录。对不上账？以银行流水为准重抄存折（rebase）。

---

## 6. 实战走线：一次真实运行回放

下面是 2026-09-24 一次真实运行（在临时演示工作区）的完整命令序列，可以直接对照第 3、4 节的图看：

```
status -> state:none                        bootstrap probe
   |
   v
init -> STATE_CREATED (14 stages)           graph + state + audit created
   |
   v
next  -> run-stage: workspace-detection     first pending in plan order
   |
   v
report wd completed -------------------> current = reverse-engineering
   |
   v
next  -> run-stage RE (conditional:true)    engine still emits it;
   |                                        model judges Execute-IF not met
   v
report RE skipped [S] --reason greenfield-skip    passes validation [3]
   |
   v
current = requirements-analysis
   |
   v
[model] questions file -> question tool -> answers -> QT-02 write-back
   |                                        engine untouched in between
   v
park --note "..." -> Last Parked + handoff.md     marks/current UNTOUCHED
   |
   v
status -> resume_note + note_age_seconds:6 + autonomous{...}
          + resumed-artifacts alert (RA half-done artifacts sensed)
```

### 逐行讲解

1. **`status` 探测**：工作区里还没有状态文件 → 引擎答 `state: none`，模型知道这是新项目，走欢迎流程。
2. **`init`**：开户。状态文件、审计文件同时创建，审计里第一条就是 `STATE_CREATED`。
3. **`next`**：引擎查进度表，第一个 `[ ]` 的阶段是"工作区检测"（缩写 wd），于是发一个 run-stage 指令，告诉模型该阶段规则文件在哪、要产出什么。
4. **`report wd completed`**：检测完毕（空目录、新项目，无需门禁），盖 `[x]`，指针移到下一阶段"逆向工程"。
5. **`next` 发出 RE 指令，但带着 `conditional: true`**——注意：**引擎照发不误**。引擎不懂"这个项目是不是老项目"（那是判断），它只负责把条件阶段发出来；适不适用由模型判断。
6. **`report RE skipped --reason ...`**：模型判断是全新项目，RE 不适用。这道 skipped 能通过第 4 节的关卡 [3]，因为 RE 本来就是 CONDITIONAL 阶段。理由落进审计。
7. **RA（需求分析）进行中**：模型写问题文件、调结构化提问工具收集用户答案、回写文件——**这一大段完全没有引擎参与**，因为写文档是模型的活，引擎只管流程账。
8. **`park`**：会话要中断，留停车便签。进度表和当前阶段**原封不动**——中断不是转移。
9. **`status` 恢复简报**：新会话一开场就能看到：停车时留的注记（resume_note）、便签贴了多久（note_age_seconds: 6）、自主模式配置（autonomous{...}），还有传感器警报——发现 RA 的半成品文件已存在，提醒"上次可能干了一半"。

### 这张图在画什么

它演示的是职责分工的**节奏感**：引擎调用（一行命令、一个 JSON 回执）和模型工作（读规则、写文档、提问）交替出现。引擎像地铁闸机——刷一下，过去几步，再刷一下；乘客在两台闸机之间怎么走，闸机不管。

---

## 附 A：行号锚点速查

| 位置 | 函数/常量 | 作用 |
|---|---|---|
| engine.py:70-74 | `MARK_*` | 五种印章字符：空格 / x / S / R / ? |
| engine.py:76 | `RESULTS` | report 结果的封闭集合（5 种） |
| engine.py:183 | `load_graph()` | 只读加载编译产物 stage-graph.json |
| engine.py:293 | `_parse_plan()` | 读模型写的执行计划（宽容解析） |
| engine.py:457 | `_digest_of_region()` | 计算引擎区 sha256 指纹 |
| engine.py:468 | `_splice_region()` | 重写引擎专属区 |
| engine.py:520 | `_audit_transition_events()` | 从审计解析转移事件（对账用） |
| engine.py:595 | `check_integrity()` | 指纹 + 审计双链核验 |
| engine.py:670 | `effective_stages()` | 按 scope/计划裁剪后的有效阶段序列 |
| engine.py:688-700 | `pending_stages()` / `current_stage()` | 第一个 `[ ]` 阶段 = 当前阶段 |
| engine.py:730 | `_parse_autonomous()` | 读自主模式区（宽容解析） |
| engine.py:779 | `_ctx_enabled()` | 读扩展配置表判断 CTX 开关 |
| engine.py:918 | `_artifact_alerts()` | 传感器：半成品/缺产出/缺 checkpoint 警报 |
| engine.py:1030 | `cmd_status()` | 恢复简报（resume_note / recent_events / …） |
| engine.py:1136 | `cmd_stamp()` | 权威时间戳，零副作用 |
| engine.py:1216 | `_validate_transition()` | report 的四道验证关卡 |
| engine.py:1274 | `cmd_report()` | 唯一转移写入口 |
| engine.py:1308 | `cmd_jump()` | 改道（--fresh 归档重来） |
| engine.py:1405 | `cmd_rebase()` | 按审计流水重放修复 |
| engine.py:1519 | `cmd_park()` | 泊车注记（不碰进度、不写审计） |
| engine.py:1562 | `_JsonArgumentParser` | 连命令行用法错误都输出 JSON |
| engine.py:1619 | `main()` | 命令分发入口 |

## 附 B：延伸阅读

- `references/common/engine-contract.md` —— 引擎对外契约：动词语义、状态分区、示例
- `references/common/stage-contract.md` —— 阶段 frontmatter 字段定义与校验规则
- `scripts/tests/` —— 205 个测试（engine 128 + trace-matrix 22 + generate 55），改引擎后必跑
- `docs/integration-plan.md` —— 设计决策（D6/D13/D14 等）与演进史
