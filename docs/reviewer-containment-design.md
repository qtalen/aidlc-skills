# Reviewer 只读遏制 · L3 快照检测设计（修正版）

| 项 | 值 |
|---|---|
| 状态 | 设计定稿（2026-10-20，独立审查 5 第一层 + 4 改进全采纳 + 本机 PoC 实测）· **未立项** |
| 落地形态 | Phase 5B 或触发条件点火的独立小批（`scripts/` Python 工具 + review-delegation.md 强制步骤） |
| 来源链 | plan brief §5c v4（四会话设计讨论，2026-10-19）→ 快照配方提案 + reviewer 独立审查（2026-10-20）→ 本文 |
| 取代 | brief §5c 的结构层规格〔`(rev-parse HEAD, status --porcelain)` 二元组〕与挂账触发条件〔"出现一次 reviewer 越界"——经审查证实本机结构性不可达〕 |

## 1. 问题与原则

harness 无关 ⟹ "禁止 reviewer 编辑文件"不可移植承重。"只读"四层防线中的 L3 观测层兜底：检测审核窗口内（委派前 → 返回后）的项目文件变更。原则：**用观测变化替代禁止变化**。

## 2. 四层防线（上下文，不变）

| 层 | 手段 | 性质 |
|---|---|---|
| L0 语义 | findings-only 输出契约（返回通道单向文本） | 结构性，永远有 |
| L1 约定 | 委派任务书只读条款 + D13 声明 | 对齐非安全，永远有 |
| L2 机制 | harness 权限（本机 reviewer.md deny write/edit/bash/skill 为实例） | 尽力而为 |
| L3 观测 | **本设计**（三明治契约·修正版） | 挂账待触发（§6） |

## 3. 三明治契约·修正版

快照与重算均由**委派方**执行（reviewer 侧 bash 受禁时无执行通道，不依赖其自报）。

**判定值**（一次 capture 产出）：

1. `tree`——工作区快照哈希（tracked + 非忽略 untracked 的全部内容）
2. `HEAD`——提交指针（挡 commit 逃逸：工作区内容不变但窗口内提交了东西）
3. `.git/index` sha256（可选）——挡"reviewer 只执行 `git add` 动索引不动工作区"的越界形态
4. 忽略区清单 hash（可选，仅告警通道）——本仓库 `.gitignore` 忽略 `aidlc-workflows-cn/`、`opencode-cn/`、`docs/dogfood-records/`，前两块正是 reviewer 做现实锚定会读的只读语料

**capture 配方**（必须**单进程原子执行**，理由见处置表 #1；Windows cmd 形态仅本机备注，最终工具为 Python）：

```bat
mkdir %TEMP%\aidlc-snap 2>nul
setlocal
set GIT_INDEX_FILE=%TEMP%\aidlc-snap\T0.idx
git read-tree HEAD || exit /b 1
git add -A || exit /b 1
git write-tree
git rev-parse HEAD
endlocal
```

实测要点：

- 临时索引**必须放工作区外**——放仓库内会被自身快照捕获，且锁文件出现/消失产生假差异
- `read-tree` 缺父目录即 fatal（errorlevel 1，失败可见）——故 mkdir 前置、失败即中止
- 空/新建索引上 `add -A` 同样产出有效树——`read-tree` 仅为 `ls-files -m` 语义存在，捕获链路可容忍其失败
- 判定用 **tree 字符串直接比较**为主；`git diff --quiet tree0 tree1` 三态：0 一致 / 1 差异 / ≥2 **检测本身失败**（必须报错，不得降级为 verified）；`--stat` 仅在差异时作路径诊断
- 环境变量不跨 shell 调用（本 harness 实测，每次调用新进程）——**禁止拆成逐条命令执行**：否则 `read-tree`/`add -A` 作用于真实索引，丢弃用户暂存态并违反 B&T"绝不静默暂存"红线（build-and-test.md:370）与"report 前不写 git"（:363）
- cmd 内联 `set VAR=value & ...` 会吞尾随空格（真实事故复现过）——脚本形态无此问题
- `ls-files -m -o --exclude-standard` 降级为**可选诊断**（pre-window dirty inventory，解释假阳性用）：须在 `read-tree` 后、`add -A` 前跑，CWD 在子目录时静默截断，不参与判定

**判定规则**：

- `tree0 == tree1` 且 `HEAD0 == HEAD1` → **verified(full-tree)**
- 否则按**证据集**分级（不按文件类别——测试输出常常正是证据核验的现实锚点）：
  - 变化路径 ∩（被审产物集 ∪ 状态文件 ∪ 委派 brief 的现实锚点路径）≠ ∅ → **tamper，本轮 findings 整体作废**（审的与手里的已非同一份），换 agent 重跑或升级给人
  - 其余路径（构建产物、IDE 自动保存、后台进程写入等）→ 留痕路径清单 + 人裁量，findings 可继续有效——**豁免必须留记录**，不得无痕放过
- 非 git 工作区 / 首提交前 → **显式清单 sha256 模式**（被审产物 + 状态文件 + 现实锚点；忽略区与仓库外由清单补位），判定输出 `verified(list-only)` / `uncovered`
- 审计记录必须携带覆盖方式（verified(full-tree) / verified(list-only) / uncovered）——绝不把弱保证伪装成强保证

**tamper 处置三步**（不提供半成品"一键恢复"）：

1. **取证**：`git archive tree1` 导出，或整体复制工作区到工作区外
2. **复位**：`git read-tree --reset -u tree0`（删新增、复原修改——明确它会重置真实索引）；窗口内有 commit 时另加 `git reset --hard HEAD0`
3. **留痕**：审计记 tree0/tree1/HEAD0/HEAD1 四值 + 取证物路径 + 分诊结论

**工具形态**（上线时）：技能目录 `scripts/` 下独立 Python 脚本（capture / verify 两子命令；Python 内部解析路径规避 Windows 引号/尾随空格问题；无 git 自动退 sha256 清单模式而非报错退出）。不动引擎契约（stamp 先例）。

## 4. 审查处置表（2026-10-20，reviewer 独立审查，5 第一层 + 4 改进全采纳）

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| 1 | bug | GIT_INDEX_FILE 两种读法必有一种改写真实索引：逐条 shell 调用 = 环境变量丢失 → read-tree/add -A 打在真实索引上（丢弃用户暂存态、撞 B&T :370/:363 红线）；同会话多行则违反单行纪律且泄漏变量 | capture 定义为单进程原子脚本（setlocal + mkdir + 逐步失败中止）；"禁止拆条执行"写入配方 |
| 2 | gap | 覆盖边界与"verified"记录强度不匹配：非 git 项目机制整体不可用、忽略区语料（reviewer 会读的只读参考）、`.git` 内部全部静默缺席，审计却只有二元 verified | 三态判定输出 + 证据集分级 + sha256 清单回退；忽略区清单 hash 告警；合成公式 = tree 主检（有 git）/ sha256 回退（非 git、忽略区、仓库外）/ HEAD 辅检（提交逃逸） |
| 3 | gap | "用 tree0 恢复/隔离"不可执行：checkout 不删新增文件、不撤 commit、自身重写真实索引、且"恢复"销毁了重审与人复核需要的证物 | 改三步：取证 → 复位（read-tree --reset -u + reset --hard HEAD0）→ 留痕四值 |
| 4 | gap | 触发条件本机结构性不可达：本机 reviewer deny 写/执行、窗口内主会话阻塞 →"等一次越界"永远等不到，观察期全绿反而被误读为"没问题" | 触发条件改两条任一（§6）；本机实践期产出重定义为"配方可用性 + 误报率"，不是必要性证据 |
| 5 | ambiguity | "任何 diff 即 tamper"与同文档"按路径解释"自相矛盾，实操必然产生无记录豁免 | 分级锚在证据集（被审产物 ∪ 状态文件 ∪ 现实锚点 → 作废；其余 → 留痕 + 人裁量）；明确不按文件类别分级 |
| A | 改进 | `--stat` 文本判定脆弱（命令出错时 stdout 也为空，会把"没跑成"读成"一致"） | tree 字符串比较为主判定 + `diff --quiet` 三态（≥2 = 检测失败，报错不降级） |
| B | 改进 | `ls-files -m -o` 与 tree diff 信息冗余，且引入顺序陷阱与 CWD 截断 | 降级为可选诊断（pre-window dirty inventory），不参与判定 |
| C | 改进 | "40 位指纹 / 整棵工作区 / 零副作用"三处措辞超能力（sha256 仓库为 64 位；忽略区与子模块不在内；write-tree 写不可达对象） | 哈希长度不硬编码；口径改"工作区快照（tracked + 非忽略 untracked）"；副作用口径改"零工作区副作用 + 少量不可达对象（gc 可回收）" |
| D | 改进 | POSIX 下 `set VAR=` 是设位置参数非导出变量，静默失效后同样落入 #1 | 最终工具必须 Python（跨平台）；cmd 配方仅本机实践期备注 |

## 5. 已验证事实（本机 PoC，2026-10-20）

机制（临时仓库实跑）：

1. 同窗口三场景全中：已脏文件再改（porcelain 前后完全一致的盲区）/ 干净文件改后 commit（commit 逃逸：HEAD 变化 + tree diff 双杀）/ 新增未跟踪文件
2. 删除与重命名：树对比正确报出（`c.txt -1`、`a.txt => d.txt`）
3. 缺父目录 → `read-tree` fatal + errorlevel 1（失败可见）
4. 空索引 `add -A` → 有效树
5. 环境变量不跨 shell 调用（每次调用新进程，实测确认）
6. cmd `set VAR=value & ...` 尾随空格事故复现（索引路径带空格 → 假 status 输出）
7. 临时索引放仓库内被自身快照捕获 + 锁文件假差异

本仓库配置事实：

- `core.autocrlf = true`（仓库级实测）→ 纯换行改写不可见（现实盲区，非理论）
- `filemode = false` → mode 变更不可见
- `ignorecase = true` → 仅大小写改名不可见
- `.gitignore` 忽略三块语料（见 §3 判定值 4）

## 6. 触发条件（修正版，2026-10-20 用户裁决）

**两条任一 → L3 立即上线**：

1. 在 L2 不覆盖的 harness 上做一次真实审查；
2. 外部写入导致一次无法解释的变更。

**本机实践期的产出定义**：配方可用性 + 误报率——跑 N 次全绿 ≠ 机制必要，不构成必要性证据。复评时机：实践期收尾（维持 2026-10-19 裁决）。

实践期轻量替代（维持）：委派前后各记一次快照、肉眼比对——可直接用 §3 配方（单进程脚本形态）。

## 7. 边界（承袭并明确）

- ignored 路径 / 仓库外 / `.git` 内部（真实索引由可选 hash 项覆盖）/ CRLF 与 filemode 归一化——均已声明盲区
- 面向失范与失误，非对抗性取证（reflog 级规避不在威胁模型内）
- 与引擎零耦合：不进 D14 传感器（fire 点是引擎动词，委派边界不在引擎视野）；与 State Digest 无冲突（快照只读；窗口内状态文件变动被判 tamper 是正确行为）
- 与 B&T commit 红线：capture 绝不触碰真实 index（单进程原子 + 临时索引 + 失败即中止）

## 8. 落点与免费副产品（承袭）

- 上线时为 `references/common/review-delegation.md` 强制步骤（RV-xx 条款形态，由委派方执行；受"强制步骤须在当阶段实际加载文件里有锚点"透镜约束）
- 快照兼任审查收据：下轮复审对比即知"上回审过后改了什么"（增量复审基线）；findings 的 file:line 在分诊核对时锚定同一棵已知未动的树——审读与核对之间无漂移
- 变体（审副本沙目录 / 审查前先 commit）维持否决，理由见 plan brief §5c 变体节（历史记录）
