# AI-DLC v2.0 opencode 插件 — 完整技术文档

> 本文档基于对 `opencode/` 目录**全部源码**（约 300 个文件：50+ 个 TypeScript 工具、17 个钩子、41 个技能、33 个阶段定义、8 个协议模块、14 个智能体、11 个 scope、6 个传感器、全部数据文件）的逐一遍历撰写。
>
> - **框架版本**：`2.7.1`（唯一真源：`.aidlc/tools/aidlc-version.ts` 的 `AIDLC_VERSION` 常量）
> - **Harness 标识**：`.aidlc/tools/data/harness.json` → `{ "name": "opencode", "harnessDir": ".aidlc", "rulesSubdir": "rules" }`
> - **运行时要求**：opencode ≥ 1.17 + bun（全部工具/钩子经 bun 执行）

---

## 目录

- 第一部分：总览 — §1 是什么 / §2 目的与理念 / §3 总体架构 / §4 目录结构
- 第二部分：opencode 原生层 — §5 opencode.json / §6 命令入口 / §7 适配器插件详解
- 第三部分：工作流引擎 — §8 转发循环 / §9 Directive 契约 / §10 语音契约 / §11 新工作与 Composer
- 第四部分：生命周期 — §12 33 阶段总览 / §13 逐阶段详解 / §14 Stage 契约 / §15 Scope / §16 ARS
- 第五部分：协议 — §17 conductor.md / §18 主协议 / §19 七个协议模块 / §20 问题渲染
- 第六部分：多智能体 — §21 十四 agent / §22 四种拓扑
- 第七部分：治理 — §23 审批门 / §24 传感器 / §25 评审者 / §26 学习仪式 / §27 Construction 机制
- 第八部分：持久化 — §28 数据树 / §29 状态与审计 / §30 五层规则 / §31 知识资产 / §32 恢复
- 第九部分：实现清单 — §33 Hooks / §34 Tools / §35 Skills / §36 data 文件 / §37 规则种子
- 第十部分：安全与扩展 — §38 权限模型 / §39 opencode 差异 / §40 插件工具链 / §41 Git 集成
- 附录 A：使用速查 / 附录 B：一句话理解

---

# 第一部分：总览

## 1. 这个插件是什么

这是 **AI-DLC（AI-Driven Development Life Cycle，AI 驱动开发生命周期）v2.0** 方法论的 **opencode harness 发行版**——一套把 opencode CLI 包装成"结构化软件工厂"的完整插件包。

它**不是**传统意义上"编译后安装"的插件：没有 `package.json`、没有构建产物、没有 npm 依赖。整个目录就是一个**可直接放进项目根目录的工作区外壳（workspace shell）**，由三类内容组成：

| 组成 | 位置 | 性质 |
|------|------|------|
| opencode 原生消费面 | `.opencode/`、`opencode.json` | opencode 自动发现加载的命令、子代理、插件 |
| 框架运行时（引擎） | `.aidlc/` | 跨 harness **字节共享**的 TypeScript 工具、钩子、技能、协议、知识库 |
| 工作区数据树 | `aidlc/` | 运行时产生的规则、记忆、intent 记录、审计日志（纳入 git 版本控制） |

用户只需在项目里输入 `/aidlc <想构建的东西>`，插件就会接管：判断这件事需要多少流程（scope）、逐步执行从需求到部署的完整生命周期、每一步都停下来请求人类批准，并把"决定了什么、为什么"完整落盘。

**前置条件**（来自 `AGENTS.md`）：
- **opencode ≥ 1.17**：依赖其插件钩子面（`tool.execute.before/after`、`chat.message`、`session.idle` 事件总线、`experimental.session.compacting`）与项目级 `.aidlc/skills/`、`.opencode/agents/` 发现能力。
- **bun**：全部 50+ 个 CLI 工具和 17 个钩子脚本都是 TypeScript，经 `bun` 以子进程方式执行；适配器还会直接探测 `~/.bun/bin/bun`。
- **模型/Provider**：项目 `opencode.json` 不锁定模型，由全局 `~/.config/opencode/opencode.json` 提供默认；5 个分层 persona 固定使用 `amazon-bedrock/global.anthropic.claude-sonnet-4-6`（可在项目配置中按 agent 覆盖）。
- **锁**：审计日志用 mkdir 锁（系统临时目录，跨平台无外部依赖）。
- **钩子权限**：17 个钩子全是 `.ts`，经 bun 运行，不需要可执行位——macOS/Linux/原生 Windows 行为一致。

## 2. 设计目的与核心理念

### 2.1 要解决的问题

裸用 AI 编码助手做真实项目时的典型失控点：AI 自由发挥跳过需求与设计、决策没有记录无法追溯、上下文丢失后无法恢复、并行/委派工作没有边界、质量没有强制检查点。AI-DLC 的回答是：**把"必须由机器精确执行的部分"从"必须由模型判断的部分"中剥离**。

### 2.2 核心架构哲学：判断归 LLM，精确归工具

- **LLM（conductor）负责判断**：扮演领域专家角色、提出好问题、做设计权衡、在审批门向人类呈现决策。
- **TypeScript 工具负责精确**：工作流走到哪一步（状态机）、下一步该做什么（编排引擎）、决策日志怎么写（审计）、阶段能否通过（传感器）、并行工作如何收敛（swarm 裁判）。这些**绝不由模型在散文中即兴推导**。

`AGENTS.md` 原话：*"small command-line programs (TypeScript, run via bun) that do the parts which must be exact rather than judged"*。

### 2.3 七条贯穿性原则

1. **人在每个决策点上**：除 3 个引导初始化阶段外，每个 stage 都有强制审批门，不可推断、不可自动批准、不可跳过；沉默不等于批准；自治权永不推断（"这个阶段你看着办"只对该阶段一次有效）。
2. **自适应流程（Adaptive scope）**：11 个内置 scope 决定 33 个 stage 中哪些 EXECUTE、哪些 SKIP、提问深度多少；自适应 composer 可按任务熵值定制网格。
3. **一切可追溯**：审计日志是 append-only 决策账本，91 个事件类型、22 个类别的冻结词表，由工具原子写入；模型被**禁止**从散文发审计事件。
4. **状态可恢复**：产物树、per-stage 日记、审计日志、状态文件、runtime-graph 五重数据源支撑会话恢复、压缩后恢复、崩溃恢复。
5. **无涌现行为**：完成消息固定 2 选项（Construction/Operation），只有 Ideation/Inception 可条件性加第 3 选项；选项严格来自 spec + Other，禁止即兴发明。
6. **harness 中立**：核心（`.aidlc/`）与具体 AI CLI 解耦，同一核心渲染到 7 个 harness（claude/codex/copilot/cursor/kiro/kiro-ide/opencode）；`aidlc/` 工作区树可在不同 harness 安装间迁移。
7. **自学习护栏**：人类的纠正经 §13 学习仪式沉淀为 `team.md`/`project.md` 中的持久实践，冲突检查保证窄层规则不推翻宽层策略。

## 3. 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│ 用户: /aidlc "帮我做一个 XXX 系统"                            │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ opencode 原生层 (.opencode/)                                 │
│  · command/aidlc.md      — /aidlc 命令入口，转交 skill       │
│  · agents/*.md (×14)     — 原生 subagent 人格投影            │
│  · plugin/aidlc-opencode-adapter.ts — 钩子适配器（唯一        │
│    为 opencode authored 的文件，其余全是 packaged 核心）      │
└──────────────────────────┬──────────────────────────────────┘
                           ▼ 适配器把 opencode 钩子时刻映射为核心钩子子进程
┌─────────────────────────────────────────────────────────────┐
│ AI-DLC 核心 (.aidlc/) —— 与 Claude Code 版字节共享            │
│  · skills/aidlc/SKILL.md — 编排器（conductor）提示词          │
│  · tools/aidlc-orchestrate.ts — 确定性编排引擎（"下一步做什么"）│
│  · tools/*.ts (×50+)     — 状态/审计/图/传感器/学习/蜂群…     │
│  · hooks/*.ts (×17)      — 核心钩子体                         │
│  · aidlc-common/         — 阶段文件(33)+协议模块(8)+指挥家人格 │
│  · scopes/(11) sensors/(6) knowledge/ agents/(14)            │
│  · tools/data/stage-graph.json — 编译后的阶段 DAG（结构真理）  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼ 读写
┌─────────────────────────────────────────────────────────────┐
│ 工作区数据树 (aidlc/) —— harness 中立，纳入 git               │
│  spaces/<space>/memory/     五层规则（org→team→project→phase→stage）│
│  spaces/<space>/intents/<YYMMDD>-<label>/  每个工作意图的记录  │
│    ├─ aidlc-state.md        状态文件（工作流位置）             │
│    ├─ audit/                append-only 审计分片（按 clone）   │
│    ├─ <phase>/<stage>/      各阶段产物 + memory.md 日记        │
│    └─ runtime-graph.json    编译的运行时图                    │
│  spaces/<space>/knowledge/  团队知识 + DocumentKB 文档目录     │
│  spaces/<space>/codekb/     代码知识库（brownfield 扫描产物）  │
└─────────────────────────────────────────────────────────────┘
```

关键设计：**`.aidlc/` 里的工具/钩子/技能与 Claude Code harness 版字节共享**（packaged core），opencode 独有的只有 `.opencode/plugin/aidlc-opencode-adapter.ts` 这一个 "authored shell 文件"——因为 opencode 没有 settings.json/hooks.json 钩子注册表，它的扩展缝是插件 API，所以需要一个适配器把 opencode 的钩子时刻翻译成核心钩子能懂的输入。

## 4. 目录结构全景

```
opencode/
├── opencode.json                  # opencode 项目配置（skills 路径、instructions、权限）
├── AGENTS.md                      # 给 AI 的项目说明（AI-DLC 结构导览，opencode 自动注入）
├── .gitignore                     # 通用忽略 + AI-DLC per-user/机器本地文件排除
│
├── .opencode/                     # 【opencode 原生发现层】
│   ├── command/aidlc.md           # /aidlc 斜杠命令入口
│   ├── agents/aidlc-*-agent.md    # 14 个原生 subagent（mode: subagent）
│   └── plugin/aidlc-opencode-adapter.ts  # 钩子适配器插件（774 行）
│
├── .aidlc/                        # 【AI-DLC 框架运行时，跨 harness 共享核心】
│   ├── skills/                    # 41 个技能目录
│   │   ├── aidlc/                 # 主编排器（SKILL.md + question-rendering.md）
│   │   ├── aidlc-<stage>/         # 30 个单阶段隔离运行器（自动生成）
│   │   ├── aidlc-init/            # 初始化阶段打包入口
│   │   ├── aidlc-compose/         # 自适应工作流组合入口
│   │   ├── aidlc-session-cost/ aidlc-replay/ aidlc-outcomes-pack/  # 只读会话技能
│   │   ├── aidlc-knowledge/       # DocumentKB 文档目录技能（read-write）
│   │   └── aidlc-mvp/ aidlc-feature/ aidlc-express/ aidlc-bugfix/ aidlc-security-patch/
│   ├── agents/aidlc-*-agent.md    # 14 个 harness 中立的权威人格（inline 使用）
│   ├── knowledge/                 # 按 agent 划分的方法学知识库（14 目录）+ aidlc-shared/
│   ├── scopes/aidlc-*.md          # 11 个 scope 定义
│   ├── sensors/aidlc-*.md         # 6 个传感器清单
│   ├── aidlc-common/
│   │   ├── conductor.md           # 指挥家执行人格手册（引擎注入首个 run-stage）
│   │   ├── protocols/             # 8 个协议模块
│   │   └── stages/<phase>/*.md    # 33 个阶段文件（5 个 phase 子目录）
│   ├── hooks/                     # 17 个核心钩子体 + review-freeze-command.ts 共享库
│   └── tools/                     # 50+ 个 bun CLI 工具（引擎本体）
│       ├── aidlc-orchestrate.ts   # 编排引擎（恰好 5 个子命令）
│       ├── aidlc-state.ts / aidlc-audit.ts / aidlc-log.ts
│       ├── aidlc-graph.ts / aidlc-sensor*.ts / aidlc-plugin-*.ts / ...
│       └── data/                  # 编译产物与静态数据
│
└── aidlc/                         # 【工作区数据树，运行时产物，纳入 git】
    ├── active-space               # 当前空间游标（per-user，gitignore）
    └── spaces/default/memory/     # 分层规则：org.md / team.md / project.md / phases/*.md
        #（intents/、knowledge/、codekb/ 在首次运行时由引擎创建）
```

---

# 第二部分：opencode 原生层

## 5. `opencode.json` 配置详解

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": { "paths": [".aidlc/skills"] },                 // ① 让 opencode 发现 .aidlc 下的 41 个技能
  "instructions": ["aidlc/spaces/default/memory/**/*.md"],  // ② 把五层方法规则注入每次会话上下文
  "permission": {
    "edit":  { "*": "allow", ".aidlc/tools/**": "ask", ".aidlc/hooks/**": "ask" },
    "bash":  { "*": "ask", "bun .aidlc/tools/*": "allow", "bun .aidlc/hooks/*": "allow" }
  }
}
```

三个要点：

1. **skills 发现**：`skills.paths` 把框架的全部技能注册为 opencode 可调用的技能。
2. **方法注入**：`instructions` glob 是 AI-DLC 方法（五层规则文件）到达模型环境上下文的**原生通道**——对比其它 harness：Claude 用 `@`-import 存根、Kiro CLI 用 resources 或 IDE steering、Codex 用 `AIDLC_RULES_DIR`、Copilot 用 `AGENTS.md` `@`-imports。`/aidlc space <name>` 切换空间时会**原位改写**这个指针（surgical，保留 JSONC 注释，由 `aidlc-includes.ts` 实现）。
3. **最小权限配置**：仅预批准"单次直接调用打包时嵌入的工具/钩子入口"；其它一切 bash 都要询问；对 `.aidlc/tools/`、`.aidlc/hooks/` 的编辑也要询问（防止篡改引擎）。**注意配置层的 `bun .aidlc/tools/*` 是宽门**——真正的窄门 enforcement 在适配器插件里（见 §7.4）。

## 6. `/aidlc` 命令入口

`.opencode/command/aidlc.md` 是一个极薄的入口（14 行）：声明 `/aidlc` 命令的描述（出现在命令补全里），正文指示模型**立即调用 `aidlc` skill 并严格遵循**（"它定义转发循环：你跑 `bun .aidlc/tools/aidlc-orchestrate.ts next` 并把下面的参数原样透传，按返回的唯一 directive 行动，报告结果，重复直到引擎说 done"），末尾 `$ARGUMENTS` 占位透传用户参数。真正的逻辑全在 `.aidlc/skills/aidlc/SKILL.md`（268 行编排器提示词）。

## 7. 适配器插件 `aidlc-opencode-adapter.ts` 逐模块详解

这是本目录**唯一为 opencode 专门编写**的运行时文件（774 行，头部注释明确标注："AUTHORED shell file；`.aidlc/hooks/` 里的 hook 体是 PACKAGED core，与 Claude Code harness 字节共享"）。

### 7.1 存在的理由

opencode 没有 Claude Code 那样的 `settings.json` 钩子注册表；它的扩展缝是**进程内加载的插件 API**（自动发现 `.opencode/plugin/*.ts`，由 opencode 运行时加载）。适配器的职责：

1. 把 opencode 的钩子时刻映射成核心钩子体的 **bun 子进程调用**；
2. 为每个核心钩子构造它在 Claude Code 上习惯解析的 **`ClaudeCodeHookInput` JSON**（经 stdin 喂入）；
3. 在 opencode 本体实现三个核心钩子无法完成的 enforcement（bash 窄门、nudge 注入、主/子会话甄别）。

### 7.2 bun 解析与 fail-open

`bunBin()`：优先探测 `~/.bun/bin/bun`（存在则直接用绝对路径），否则退回 PATH 上的 `bun`。`runCore()` 用 `spawn` 起子进程（cwd=项目目录，环境注入 `AIDLC_PROJECT_DIR` 与 `CLAUDE_PROJECT_DIR`），stdin 写 JSON、收集 stdout/stderr。**bun 缺失、spawn 失败、任何异常 → 静默返回 code 0（fail-open）**——建议型钩子宁可失效也不阻塞用户，这与插件 compose 钩子的行为镜像。

### 7.3 钩子时刻映射表（文件头注释中的权威表，live-verified on opencode 1.17.18）

| opencode 时刻 | 核心钩子（对应的 Claude 事件） | 性质 |
|---|---|---|
| `chat.message`（每会话首次） | `aidlc-session-start.ts`（SessionStart） | 建议型 |
| `chat.message`（每个人类回合） | `aidlc-record-human-turn.ts`（UserPromptSubmit） | 建议型 |
| `tool.execute.before` + task | `aidlc-deliver-stage-rules.ts` 改写输入 + plan-approval 守卫（PreToolUse） | 可阻断 |
| `tool.execute.before` + bash | 适配器自带 bash 入口边界 + `aidlc-state-transition-guard.ts` + `aidlc-review-freeze.ts` + `aidlc-plan-approval-guard.ts`（PreToolUse） | 可阻断 |
| `tool.execute.before` + write/edit/apply_patch | `aidlc-review-freeze.ts` + `aidlc-plan-approval-guard.ts`（PreToolUse） | 可阻断 |
| `tool.execute.before` + 读类工具 | `aidlc-reviewer-scope.ts`（PreToolUse） | 可阻断 |
| `tool.execute.after` + write/edit/apply_patch | `aidlc-write-audit-log.ts` → `aidlc-run-sensors.ts`（PostToolUse） | 建议型 |
| `tool.execute.after` + bash | `aidlc-rebuild-stage-graph.ts`（PostToolUse Bash） | 建议型 |
| `tool.execute.after` + todowrite | `aidlc-sync-workflow-state.ts`（PostToolUse TaskUpdate） | 建议型 |
| `tool.execute.after` + task | `aidlc-log-subagent.ts`（SubagentStop） | 建议型 |
| 事件总线 `session.idle` | `aidlc-continue-workflow.ts`（Stop） | 建议型（nudge） |
| `experimental.session.compacting` | `aidlc-validate-state.ts`（PreCompact） | 建议型 |

**阻断的实现方式**：核心钩子以 exit code 2 + stderr 原因表达拒绝，适配器把它翻译成 `throw new Error(...)`——opencode 的 `tool.execute.before` 抛错即阻止工具执行。

**工具名翻译层**：`reviewerCalls()` 把 opencode 的 `read/write/edit/glob/grep/list/bash/apply_patch` 映射为 Claude 形状的 `Read/Write/Edit/Glob/Grep/LS/Bash` 调用；`apply_patch` 还会用正则从 patch 文本中解析全部 `*** Add/Update/Delete File:` 与 `*** Move to:` 目标路径，**逐路径**过钩子（保证补丁里的每个文件都被审计/传感器/冻结检查覆盖）。

### 7.4 适配器本体实现的三个 enforcement

**① bash 入口窄门（`aidlcBashBoundaryViolation` + `directShellWords`）**

`opencode.json` 的 `bun .aidlc/tools/*` 是粗粒度 glob，单靠它无法阻止"新写一个 `.aidlc/tools/payload.ts` 然后借白名单执行"。适配器内置**打包时嵌入的已发货入口白名单** `shippedAidlcEntrypoints`（62 个 `hooks/*.ts` + `tools/*.ts` 路径，由 `aidlc-plugin-emit.ts` 在打包时替换 `@aidlc-shipped-entrypoints@` 标记注入），并用手写的 shell 词法分析器 `directShellWords()` 逐字符解析命令：拒绝一切链式符（`; | &`）、重定向（`< >`）、命令替换（`` ` ``、`$`）、换行、括号、未闭合引号、反斜杠续行——只有"`bun` + 一个未改动的已发货入口"这一种形态放行。**配置层是宽门，适配器是窄门**，双层的理由是：宽门让正常调用免询问，窄门让注入新 payload 的攻击面归零。

**② Nudge 哨兵与转发循环再接入**

opencode 的 `session.idle` 是**反应式**事件（没有 blocking 的 continue-workflow 通道）。当核心 Stop 钩子回答 `{"decision":"block","reason":…}` 时，适配器通过 opencode SDK 的 `client.session.prompt()` 把 reason 包装成带 `[aidlc-forwarding-nudge]` 哨兵的新提示**注入会话**，重新接入转发循环。两个关键不变量：
- 哨兵保证 `chat.message` 臂**不会**把这个合成提示误记为人类回合（HUMAN presence 是门禁事实，不能伪造）；
- 循环防失控计数**留在核心钩子**（run-mode 感知无进展上限：autonomous=8 / interactive=2），适配器自己从不计数。
注入前先释放 `idleInFlight` 串行锁——opencode 可能同步投递下一次 idle。

**③ 主/子会话甄别（`isMainSession`）**

经 `client.session.get` 查 `parentID`：只有无主会话才 mint 人类存在、才受 Stop enforcement；task 子会话是 worker 不是人。查询失败时 **fail closed**（不确定的子会话永远不能往共享账本写 HUMAN_TURN），且**不缓存失败**以便后续事件重试。

### 7.5 会话状态簿记（进程内 5 个集合/映射）

| 结构 | 作用 |
|---|---|
| `started: Set` | session-start 已触达活跃工作流的会话（新项目无状态时核心钩子不产 context，会在后续人类回合重试直到工作流出现） |
| `sawHumanTurn: Set` | 见过真实人类回合的主会话——Stop enforcement 以此为准（工作流可能在第一回合内才创建） |
| `mainSession: Map` | 主会话判定缓存 |
| `sessionAgent: Map` | 从 `chat.message.agent` 关联 reviewer 身份——补偿 opencode 的 `tool.execute.before` **不带 active-agent 字段**；字段缺失时，子会话在有派发记录的窗口内按 `scoped_registration` 处理（窄窗口内可能误 scope 别的子 worker，但**永不误 scope 主会话**） |
| `idleInFlight: Set` | session.idle 重入防护 |

### 7.6 `tool.execute.before` 的完整处理顺序

对每次工具调用，适配器按固定顺序执行（任一环节 exit 2 即抛错阻断）：

1. **task 工具**：先跑 `aidlc-deliver-stage-rules.ts`——把当前激活阶段的规则包（带 sha256 的 `resolvedRuleBundle`）经 `hookSpecificOutput.updatedInput` **改写进**子代理 prompt；规则包缺失/超限则阻断派发。
2. **bash 工具**：先过适配器自带的 bash 窄门 → 再跑 `aidlc-state-transition-guard.ts`（拒绝手调 `aidlc-state.ts` 生命周期动词，要求走 `aidlc-orchestrate report`；若已知当前是委派 agent 则附带 `agent_type`）。
3. **bash/write/edit/apply_patch**：对每个归一化写目标跑 `aidlc-review-freeze.ts`（§12a 收据冻结：任何会使新鲜 READY 终审收据失效的 `produces[]` 写入被拒，**不分身份**）→ 再跑 `aidlc-plan-approval-guard.ts`（code-generation 的"先批准计划后生成"）。
4. **task 且目标是 `aidlc-developer-agent`**：单独再跑一次 plan-approval-guard（Task 形态，校验计划证据：plan、测试指令、Testing Contract 指纹、"Approve Plan"答案）。
5. **读类工具（含 bash/grep/glob 变体）**：跑 `aidlc-reviewer-scope.ts`（评审代理按 Unit 的读取范围强制）——身份从 `sessionAgent` 映射取；无身份且是主会话则跳过。

---

# 第三部分：工作流引擎

## 8. 转发循环（Forwarding Loop）

这是整个插件的**心跳**。`SKILL.md` 把 conductor（即 `/aidlc` 会话中的模型）约束为一个确定性循环：

```
Loop:
  1. directive = bun .aidlc/tools/aidlc-orchestrate.ts next $ARGUMENTS
  2. 按 directive.kind 执行这一个动作
  3. bun .aidlc/tools/aidlc-orchestrate.ts report --stage <directive.stage> \
       --result <outcome> [--user-input "<text>"]
  4. 重复，直到 directive.kind == done
```

### 8.1 职责分割（引擎 vs Conductor）

- **引擎（next/report）独占全部跨 stage 路由**：scope 解析、旗标优先级、跳转方向、resume/init 守卫、阶段排序、门状态、工作流完成判定。`next` 每次输出**恰好一个**经 `validateDirective` schema 校验的 directive JSON，且 `next` 本身**不变异任何状态**——变异全在 `report`（以及 directive 点名的工具）里。
- **Conductor 独占 stage 内的执行质量**：进入对的人称、问好问题、记阶段日记、化解矛盾、在门处向人类呈现判断。**永不**在散文中重新推导路由，也永不向用户叙述路由机制。
- **`$ARGUMENTS` 原样透传给第一个 `next`**——引擎自己解析 `--status`、`--stage`、`--scope`、`--depth`、自由文本等旗标，conductor 不预解析、不剥离。

### 8.2 裸会话重入探针（opencode 补偿）

opencode 的 session-start 钩子**没有 `additionalContext` 注入通道**，所以 conductor 不知道是否有活跃工作流。补偿机制：用户裸调 `/aidlc`（`$ARGUMENTS` 为空）的第一次调用，先跑只读 `bun .aidlc/tools/aidlc-utility.ts status` 探测：
- 无活跃工作流 → 裸 `next` 进循环；
- 有活跃工作流 → 呈现 Resume / Redo / Jump / Start Fresh 编号菜单并 **STOP** 等人选，然后 `report --result resumed --user-input "<answer>"`，按返回的 `print` 继续。
`--resume` 显式传入时跳过探测直接续传。

### 8.3 状态转移纪律（report 的唯一通道地位）

- 一个 gate 阶段的生命周期固定为：`report awaiting-approval` →（人类 Request Changes 时 `rejected` → 修订循环 → `revised`）→ `approved`。**每次转移都由引擎派发**。
- conductor 直接调 `aidlc-state.ts` 生命周期动词会被**双保险**拦截：工具层的 `AIDLC_STATE_TRANSITION_OWNER` 所有权守卫是硬地板，钩子层的 `aidlc-state-transition-guard.ts` 提前阻断并给出重定向信息。
- **条件性不适用**：阶段自身条件证明它不能跑时，不许伪造产物，而是 `report --result skipped --reason "<具体原因>"`（skip 是主工作流路由，`--single` 不可用）。
- **拒绝纪律**：动作按"操作+目标"定身份，同一身份被拒两次即停止；失败消息是诊断输出而非叙事，**绝不把内部词汇转述给用户**——用用户项目语言说一句"什么被拒、为什么"，再说一句"下一步可以做什么"。

## 9. Directive 契约（11 种 kind）

`aidlc-directive.ts` 是引擎↔conductor 的**冻结接口契约**（判别联合 + 运行时校验器，纯契约无 I/O）。11 种 kind 中引擎当前实际发出 8 种：

| kind | conductor 的动作 |
|---|---|
| `load-steering` | 按数组序应用 `rules_content` 并保留为活跃阶段规则包；**立即** `continue "<continue_token>"` 续传（纯传输：不 report、不打印进度、不向用户提分块）；重复直到 `run-stage` |
| `run-stage` | 核心动作。先**阻塞式**读完 `inline_context_paths` 全部文件（不许与后续读批在一起）→ 显示 `context_warnings` → 读 `stage_file` 与 `consumes` → 初始化 `memory_path` 日记 → **按 `swarm_settled` → `single` → `wave` → `gate` 的顺序分支**运行阶段体 |
| `invoke-swarm` | 自治授权下的 Construction 批次并行构建（加载 `protocol_modules` 点名的全部协议模块） |
| `ask` | 引擎把人类回合委托给 conductor：按 `question-rendering.md` 渲染结构化问题，按类型化响应契约路由（`new-work-routing` 时不 report 而按三条路由重跑 `next`；resume 菜单回答用 `report --result resumed`；其余经 `--user-input` 回喂） |
| `print` | 原样执行 `directive.message`（三形：terminal / run-then-continue / run-then-stop；变异在点名工具里，不在 `next`） |
| `error` | **原样打印** `directive.message` 并立即停止——不恢复、不重试、不粉饰 |
| `done` | 工作流（或单阶段运行）完成：呈现完成摘要并停止循环 |
| `parked` | 工作流已在干净阶段边界暂停：告知用户如何 `/aidlc --resume`，停止循环 |

`dispatch-subagent`、`present-gate`（及 `notice`）是文档化的占位形态，引擎当前不发出，conductor 不得投机实现。

### 9.1 `run-stage` 的 `gate` 分支

`gate` 字段折叠了审批门决策：
- **`gate: false`**——初始化引导阶段直通完成（无 Q&A、无工作流门、无学习仪式）。per-unit 指令不同：仍要走 PRE-GENERATION SUMMARY STOP（带 `--unit` 记录收据）再写该 unit 的产物，然后重跑 `next`。
- **`gate: "unresolved"`**——哨兵值：首个 Construction Bolt 的行走骨架（walking-skeleton）立场无法从自由文本 practices 确定性解析，引擎把裁决推给 conductor（加载 construction 协议，按 §17.4 流程分类后 `report --skeleton-stance <on|off|scope-dependent>`）。
- **`gate: true`**——完整门仪式（见 §23）。

### 9.2 `single`（隔离单阶段运行）分支

`directive.single === true` 时在普通门处理之前分支：跑阶段体 →（有文件 Q&A 则过 PRE-GENERATION SUMMARY STOP，`--single` 身份）→ 写产物与日记 → 跑配置的评审者与完成验证 → `report --single --stage <slug> --result completed` **恰好一次**。**不做**：学习仪式、`awaiting-approval`、工作流门、主工作流 `next`、park。返回的 `done` 是终态。隔离运行的评审收据也加 `--single`，使其**永远无法满足主工作流**。引擎确定性拒绝缺失/过期/自写/生成后的确认收据。

### 9.3 `wave`（per-unit 批处理波）分支

默认 stage-major 走法下，`directive.wave` 是引擎拥有的并行面，仅覆盖 functional-design / nfr-requirements / nfr-design / infrastructure-design 四个 per-unit 设计阶段。builder 得到父 `stage_file`、全部 `inline_context_paths`、`context_warnings`、完整 steering 包、各自的条目路径；尽量并发、串行为回退。build 后按 `review_state` 分支：`outstanding`（跑命名迭代）/ `retry-required`（`--retry-pending` 重发）/ `repair-required`（lead 修复后下一迭代）/ `recovery-required`（跑一次陈旧收据恢复）/ `escalation-required`（恢复已用尽，**停机**等人类 Request Changes）。全部 settle 且 `completion_required` 时跑 `aidlc-state.ts unit complete --wave`（重验条目、日记确定性去重并入父日记、发 `UNIT_COMPLETED`），然后不重批直接重跑 `next`。

### 9.4 Parking（暂停纪律）

`bun .aidlc/tools/aidlc-orchestrate.ts park` 在干净的阶段边界暂停工作流（发 `parked` directive）。**明确的反模式**：不许因"上下文感觉重"而 park——模型无法测量自己的上下文窗口（实测：感觉沉重的 32 阶段运行只用了 37%）；只有 harness 实际报告 ≥80% 用量才可因上下文 park。绝不为了够到 `done` 而批准没真正跑过的阶段——park 代替。

## 10. Conductor 的语音契约与叙事纪律

框架对"何时说话、说什么"有罕见严格的规定（`stage-protocol.md` "Talking to the user" + SKILL.md 的叙事段落）：

**内部词汇表（永不出现在用户面前）**：engine、directive、dispatch、conductor、harness、verb、scope grid、steering、forwarding loop、mint、swarm、entropy、ARS 组件名（IAE/CSU/VE/R/UA）。替换示例：engine→"workflow"或"我"；dispatch agent→"交给 X / 请 X 介入"；mint an intent→"create a workflow"。

**什么能到达用户**（仅四类载体）：
1. directive 的 `narration` 字段值（引擎已为用户措辞好，重现它，只允许调整时态/名字/明显错误的细节）；
2. `stage_validity.warning`（有效性咨询，原样显示后继续正常动作——检测性字段，永不变成错误/停止/跳转）；
3. **SAY:** 行双引号内的文本（填好槽位即是全部可说的话）；
4. 门/问题/计划/完成摘要/工具点名打印的自有表面。

**沉默规则**：工具调用之间无散文——不报下一步、不复述工具结果、不把字段读回给用户。判定测试："如果一句话的唯一内容是下一步是什么，它不属于任何地方——去做工具调用而不是写它。"首个回合例外（还没有 directive）：一句 `SAY: "Let me get started on [用户的原话]"`。

**Construction 的额外沉默**：迭代次数、continuation token、门解析状态、produces 清单等账本细节一律不叙述；重入时 `narration` 是全部可说的话，没有时至多说一句正在构建的工件名，普通情况是什么都不说。

## 11. 新工作识别、计划重塑与 Composer

### 11.1 新工作路由（recognise-vs-route）

已有活跃 intent 时，对每段 `$ARGUMENTS` 的第一个判断属于 conductor 而非引擎：**这是继续活跃 intent、描述真正无关的新工作、还是要重塑运行中工作流的计划？**

- **默认继续（CONTINUATION）**——误报新工作是主要风险，拿不准就继续（用 `aidlc-utility.ts intent --json` 对比活跃 intent 的 slug/status）。
- **真新工作 → 只 OFFER 不自动创建**：渲染 Yes/No 确认问题（肯定项以 "Yes" 开头，如 "Yes - start a second intent"），展示活跃 intent 与建议的新 intent（含推断的 scope）。**启动工作流是"判断→人类"门控的变更，无明确确认绝不创建**。CONFIRM：`next --new-intent --scope <确认scope> "<描述>"`，执行返回的 `intent-create`（替换 `--label` 占位），然后 **STOP 交接给全新会话**（intent 已落盘）。DECLINE：继续活跃 intent。引擎还做了后备：活跃工作流中收到自由文本时返回 `ask_type: "new-work-routing"` 的类型化 ask（含 `response_route: "next"`、活跃工作、`new_work_description`、`proposed_scope` 与三条路由）。
- **计划重塑（PLAN-RESHAPE）**：人类点名跳过/删除/新增 stage 或要求精简剩余计划时，路由到 `next compose "<原话>"`（绝不原文转发给普通 `next`——那会被当成推进当前阶段）。**快速路径**：请求命令式点名具体 stage（"drop market-research and team-formation"）时可跳过 composer 派发，直接写 pending 标记 → 呈现 approve/edit/reject 门 → 批准后跑 `aidlc-utility.ts recompose --skip <slugs> --add <slugs>` → 删标记。两条路径都**绝不跳过人类门**，都禁止在自治 Construction 下进行。
- 两条不可破坏的规则：绝不为了退出一个没执行的 directive 而 `report`（那会记录人类从未做过的门拒绝——放弃 directive 即可，下一个 `next` 会重推状态）；offer 路径本身**零变异**（不 park、不 report、不动活跃 intent）。

### 11.2 Composer 门流程

`/aidlc compose "<任务>"`（或 `--new-scope`、`--report <path>`、冷启动 compose offer 回答 "compose"）时引擎发 `print` 点名 composer 派发：经 `task` 工具委派 `aidlc-composer-agent`。Composer 跑只读 `detect` 扫描、估 5 个熵分量、返回结构化提案 `{mode: matched|custom, scopeName, ars{...}, arsRationale, grid, rationale[], summary}` + 两张预渲染表（ARS 评分带；逐 stage 决策理由）。

Conductor 以**三块**呈现，然后 approve/edit/reject **硬门**：
- **Block 1**：两三句平实语言推荐（这是什么类型的变更→建议多少流程→阶段列表的平实说法）+ 提案的 `summary` 行（N stages EXECUTE / M SKIP, G approval gates，取校验器数字绝不手数）+ scopeName + mode；
- **Block 2**：composer 的逐 stage 决策表原样 + fold 咨询；
- **Block 3 "Scoring detail (advisory)"**：ARS 评分表原样 + `method` 行 + arsRationale（可跳过区）。

批准后（front/report 场景）：matched 股票 scope **不写任何文件**；custom 必须**同回合**写两个文件——`.aidlc/scopes/aidlc-<name>.md`（frontmatter `name/depth/keywords: []`——组合 scope 默认不可推断）+ `scope-grid.json` 的 `"<name>": {"stages": {...}}` 条目（缺一解析为全 SKIP），然后以批准的 `creationDescription`（经字面 `--` 分隔符作为单个 argv、POSIX 单引号转义）跑 `next --scope <name> -- <desc>` 继续 intent 创建。

**In-flight recompose**（工作流运行中）：dispatch 返回 `{mode: in-flight, grid: <保留的全量有效网格>, changes: {skip, add}}`；批准前写 `aidlc/.aidlc-compose-pending` 标记（让回合能在门处结束、session.idle 尊重它），门解析后**立即删除**（残留标记会屏蔽转发循环 enforcement）；批准后跑 `recompose --skip/--add`——它确定性校验（饥饿输入/冻结动作/光标后阶段/骨架门翻转都会被拒）、只翻转光标之后的 PENDING 阶段、重建派生状态字段、审计 `RECOMPOSED`。**绝不手改状态文件**。

一句话原则：**composer 提议，人类决定，确定性校验器守门**。

---

# 第四部分：生命周期与阶段体系

## 12. 五阶段 33 个 Stage 总览

结构真理是编译产物 `.aidlc/tools/data/stage-graph.json`（33 个阶段对象的数组），由 `aidlc-graph.ts compile` 从各阶段 YAML 源 + scope 网格 + 规则链 + 传感器清单编译生成；CI 漂移检查 `compile --check` 在 JSON 与 YAML 分歧时令构建失败。

| # | Slug | Phase | 执行 | Lead（Support） | Mode | 评审者 |
|---|------|-------|------|----------------|------|--------|
| 0.1 | workspace-scaffold | initialization | ALWAYS | orchestrator | inline | — |
| 0.2 | workspace-detection | initialization | ALWAYS | orchestrator | inline | — |
| 0.3 | state-init | initialization | ALWAYS | orchestrator | inline | — |
| 1.1 | intent-capture | ideation | ALWAYS | product（architect） | inline | product-lead (advisory) |
| 1.2 | market-research | ideation | CONDITIONAL | product | inline | — |
| 1.3 | feasibility | ideation | CONDITIONAL | architect（aws-platform, compliance） | inline | — |
| 1.4 | scope-definition | ideation | ALWAYS | product（delivery） | inline | — |
| 1.5 | team-formation | ideation | CONDITIONAL | delivery | inline | — |
| 1.6 | rough-mockups | ideation | CONDITIONAL | design（product） | inline | product-lead (advisory) |
| 1.7 | approval-handoff | ideation | ALWAYS | delivery（product） | inline | — |
| 2.1 | reverse-engineering | inception | CONDITIONAL | developer（architect） | **pipeline** | — |
| 2.2 | practices-discovery | inception | CONDITIONAL | pipeline-deploy（quality, developer, devsecops） | **subagent** | — |
| 2.3 | requirements-analysis | inception | ALWAYS | product | inline | product-lead (advisory) |
| 2.4 | user-stories | inception | CONDITIONAL | product（design, developer, quality） | **mob** | product-lead (advisory) |
| 2.5 | refined-mockups | inception | CONDITIONAL | design（product） | inline | product-lead (advisory) |
| 2.6 | domain-design | inception | CONDITIONAL | architect（aws-platform, design） | inline | architecture-reviewer (advisory) |
| 2.7 | units-generation | inception | ALWAYS | architect（delivery） | inline | architecture-reviewer (advisory) |
| 2.8 | contract-design | inception | CONDITIONAL | architect（aws-platform） | inline | architecture-reviewer (advisory) |
| 2.9 | delivery-planning | inception | ALWAYS | delivery（architect） | inline | — |
| 3.1 | functional-design | construction | CONDITIONAL | architect（developer） | inline | architecture-reviewer |
| 3.2 | nfr-requirements | construction | CONDITIONAL | architect（devsecops, compliance, quality） | inline | architecture-reviewer |
| 3.3 | nfr-design | construction | CONDITIONAL | architect（aws-platform） | inline | architecture-reviewer |
| 3.4 | infrastructure-design | construction | CONDITIONAL | aws-platform（devsecops, compliance） | inline | architecture-reviewer |
| 3.5 | code-generation | construction | ALWAYS | developer | **subagent** | architecture-reviewer |
| 3.6 | build-and-test | construction | ALWAYS | quality（devsecops） | inline | — |
| 3.7 | ci-pipeline | construction | CONDITIONAL | pipeline-deploy | inline | — |
| 4.1 | deployment-pipeline | operation | CONDITIONAL | pipeline-deploy | inline | — |
| 4.2 | environment-provisioning | operation | CONDITIONAL | aws-platform（devsecops, compliance） | inline | — |
| 4.3 | deployment-execution | operation | CONDITIONAL | pipeline-deploy（developer） | inline | — |
| 4.4 | observability-setup | operation | CONDITIONAL | operations | inline | — |
| 4.5 | incident-response | operation | CONDITIONAL | operations | inline | — |
| 4.6 | performance-validation | operation | CONDITIONAL | quality | inline | — |
| 4.7 | feedback-optimization | operation | CONDITIONAL | operations（aws-platform） | inline | — |

拓扑分布：**29 inline / 2 subagent / 1 pipeline / 1 mob**。ALWAYS 15 个，CONDITIONAL 18 个。`for_each: unit-of-work` 的 5 个 per-unit 阶段：3.1–3.5。`workspace_requires: true` 仅 3.5。`summary_confirmation: required` 26 个阶段。声明评审者的 13 个阶段：intent-capture、rough-mockups、requirements-analysis、user-stories、refined-mockups、domain-design、units-generation、contract-design、functional-design、nfr-requirements、nfr-design、infrastructure-design、code-generation。

## 13. 33 个 Stage 逐个详解

### Phase 0 — Initialization（3 个，全部无门直通，`sensors: []`）

**0.1 workspace-scaffold**（produces: 无）
确保 space 级共享目录（`codekb/`、`knowledge/`）与 scope 内的 phase 目录（含 `verification/`）存在；幂等（按需创建、跳过已存在）；scope 完全排除的 phase 不建目录；per-stage 目录在首次写产物时才出现。审计 `WORKSPACE_SCAFFOLDED`。确定性逻辑在 `aidlc-utility intent-create` 中。零门意味着学习仪式从第一个 post-initialization 阶段才开始。

**0.2 workspace-detection**（produces: 无）
扫描工作区（顶层文件 + 已知源码目录，排除 harness/`aidlc/`/node_modules 等），支持"嵌套项目回退"（顶层无信号时递归容器目录至三层）；按信号分类 **greenfield / brownfield**（brownfield 任一指标存在即成立，greenfield 需全部条件成立）；识别技术栈（语言/框架/构建/测试设施）；未初始化 submodule 警告原样转达（仅建议不代跑）。审计 `WORKSPACE_SCANNED`。分类直接决定后续路由，正常操作无覆盖路径。

**0.3 state-init**（produces: 无）
从 `state-template.md` 读状态契约，用编译后的 stage graph 和 scope grid 写入完整 `aidlc-state.md`（项目描述、类型、workspace 状态、scope 配置、全部阶段复选框、Total Stages=EXECUTE 计数等）；按项目类型定路由（brownfield→reverse-engineering；greenfield→requirements-analysis）。审计 `WORKSPACE_INITIALISED`。确定性运行于 `aidlc-utility init`。

### Phase 1 — Ideation（7 个）

**1.1 intent-capture**（ALWAYS；produces: intent-statement, stakeholder-map, intent-capture-questions；sensors: claim-sources, required-sections, upstream-coverage；评审: product-lead advisory on intent-statement；scopes: enterprise/feature/mvp/poc）
以权威项目描述（`project-description` 工具）为起点；粘贴文档走 **UNTRUSTED DATA 契约**（`<document>...</document>` 内视为不可信数据）；创建问题文件并以 `## Sources` 注册表声明允许来源全集（`[desc]`/`[scope]`/`[memory:M<n>]`）；**grounding 契约**：每项实质声明必须带内联来源标签（claim-sources 传感器在门处校验）；假设进入 `## Assumption Confirmation` 双选项结构化问题（接受/转为追问），未解决前禁止调评审或完成。

**1.2 market-research**（CONDITIONAL：有外部市场定位或 build-vs-buy 考量时；produces: competitive-analysis, market-trends, build-vs-buy, questions；consumes: intent-statement(required)；scopes: enterprise/feature）
竞争分析、行业趋势、build-vs-buy 计算、市场规模问题；产出竞争分析/趋势报告/评估简报。无评审者。

**1.3 feasibility**（CONDITIONAL：有集成约束、监管要求或显著技术不确定性时；produces: feasibility-assessment, constraint-register, raid-log, questions；scopes: enterprise/feature/mvp）
加载五层 guardrails；提出集成、合规（PCI/HIPAA/SOC2）、技术栈、预算、组织阻塞、AWS 使用等问题；产物交 aws-platform（AWS landscape 评估）与 compliance（监管扫描）两个 support 评估后由 lead 综合。

**1.4 scope-definition**（ALWAYS；produces: scope-document, intent-backlog, questions；consumes: intent-statement(required), feasibility 两工件(optional)；scopes: enterprise/feature/mvp）
MVP 范围、must-have vs nice-to-have、能力依赖、排序偏好（风险/价值/依赖优先）、硬期限；产出 in/out 边界文档 + 用 MoSCoW/WSJF/RICE 排序的 proto-Unit backlog + 价值流图。

**1.5 team-formation**（CONDITIONAL：团队构成/容量/mob 规划相关时；produces: team-assessment, skill-matrix, mob-composition, questions；scopes: enterprise/feature）
技能缺口分析、团队可用性评估、技能矩阵、mob 构成计划、RACI、容量分配、入职检查单。

**1.6 rough-mockups**（CONDITIONAL：含 UI 时，API/后端则产系统交互图；produces: wireframes, user-flow, questions；评审: product-lead advisory on wireframes；scopes: enterprise/feature/mvp）
低保真 wireframe（ASCII 或结构化描述）+ 用户流图 + IA 大纲；**每屏强制一行无障碍注释**（标题层级/landmark/键盘入口）。

**1.7 approval-handoff**（ALWAYS；produces: initiative-brief, decision-log, questions；consumes 4 required + 5 optional；scopes: enterprise/feature）
**Ideation capstone**：编译全部 Ideation 产物为一页式 initiative-brief（意图/市场验证/可行性风险/scope/概念视觉/团队计划/go-no-go 建议）+ decision-log；跑 **Ideation→Inception 阶段边界验证**（写 `phase-check-ideation.md`）；三选项门：Approve（进 Inception）/ Request Changes / **Reject Initiative（结束整个工作流）**。

### Phase 2 — Inception（9 个）

**2.1 reverse-engineering**（CONDITIONAL：brownfield；mode: **pipeline** 两环链 developer→architect；produces: 9 个——business-overview, architecture, code-structure, api-documentation, component-inventory, technology-stack, dependencies, code-quality-assessment, reverse-engineering-timestamp；**写入 space 级 `codekb/<repo>/` 而非 intent record**；scopes: 10 个（仅 infra 跳过））
解析 intent 的 repo 集合（可 multi-repo，每 repo 独立收据链）；重跑守卫跑 `codekb-scope-diff` 判 NO_STORE/CURRENT/STALE/UNVERIFIED/UNKNOWN_SCOPE，向人类呈现复用/全量重扫/聚焦扫描三选；link 1 developer 扫描写 `developer-scan.md`；link 2 architect 综合为 9 工件，经 compare-and-swap `codekb-publish` **原子发布**（带 rollback/recovery）；每 link 铸 `PIPELINE_LINK_COMPLETED` 收据；对 NARROWER repo 必须在门前给出 repo 标签警告。代码知识库是 **space 级共享存储，跨 intent 累积**。

**2.2 practices-discovery**（CONDITIONAL：总是重跑保持新鲜；mode: **subagent** hub-and-spoke；lead: pipeline-deploy；support: quality/developer/devsecops；produces: team-practices, discovered-rules, evidence, practices-discovery-timestamp + 每 support 一个 contribution 文件；consumes: 6 个 RE 工件（optional + conditional_on brownfield）；scopes: enterprise/feature/mvp/infra/classic/workshop）
brownfield 从 git/CI/部署配置推断，greenfield 从 org.md 取建议默认；三 support **互盲并行**审阅各写 contribution 文件（首行 `**Collaborator:**` 身份标记 + `## Contribution` + `## Positions`）；lead 访谈 `memory/team.md` 五个区块（Way of Working / Walking Skeleton / Testing Posture / Deployment / Code Style，用用户语言并解释术语）；**promote 机制**：人类批准不提交，直到确定性工具 `practices-promote` 成功（先写 project.md 再写 team.md，成功发 `PRACTICES_AFFIRMED`，失败 `PRACTICES_OVERRIDE`）——引擎要求当前尝试的两项事实齐全才接受 `approved`；Testing Posture 必须含 `Methodology` 与 `Ordering` 两个结构化字段。

**2.3 requirements-analysis**（ALWAYS；produces: requirements, questions；评审: product-lead advisory on requirements；scopes: 全部 11 个）
六维完整性分析、强制歧义检测与矛盾分析 + 追问；**强制 PRE-GENERATION STOP**：追加 `## Consolidated Summary Confirmation`（Looks correct / Request changes）；产出 `requirements.md` 带 **FR{n} / NFR{n} 稳定 ID**（永久 traceability key）；若 User Stories 被 SKIP，门提供三选项含 "Add User Stories"（跑 `recompose --add user-stories`）。

**2.4 user-stories**（CONDITIONAL；mode: **mob** 网状；lead: product；support: design/developer/quality；produces: stories, personas, user-stories-assessment, traceability；评审: product-lead advisory on stories；sensors: +traceability；scopes: enterprise/feature/mvp/classic/workshop）
先做"是否需要 user stories"评估（不需要则 `report skipped`）；Round 0 lead 起草 personas.md 与 stories.md（`US{group}.{seq}`、`AC{story}.{seq}.{criterion}` 三段 ID）；Round 1 并行派发 mob（三 support 互盲各写 contribution）；lead 整合并**分诊异议**：判断性异议（scope/风险胃口/优先级）中途以结构化问题浮给**人类**，知识性争议进 Round 2 仅重派异议 agent（最多两轮）；写元素级 traceability.json（FR/NFR → USx.y，Deferred/N/A 需理由）。**三个 contribution 文件是 ensemble 证据，缺任一引擎拒绝批准**。

**2.5 refined-mockups**（CONDITIONAL：有 UI 且已有 rough mockups；produces: mockups, interaction-spec, design-system-mapping, accessibility-checklist, questions；评审: product-lead advisory on mockups；scopes: enterprise/feature/mvp/classic/workshop）
中高保真 mockups + 交互规格（用 `component-spec-template.md`）+ 设计系统映射 + 响应式规格 + 无障碍合规清单。classic scope 跳过 Ideation 时优雅降级（直接从故事+需求设计，**绝不发明缺失工件内容**）。

**2.6 domain-design**（CONDITIONAL：需要新组件或逻辑构建块时；produces: components, decisions, traceability；评审: architecture-reviewer advisory on components；sensors: +traceability；scopes: enterprise/feature/mvp/classic/workshop）
识别逻辑构建块（组件=你写的代码；数据库/缓存/队列/第三方是依赖而非组件；不决定部署拓扑/技术栈）；产出**机器可读 fenced yaml 组件目录**（source of truth，well-formedness 规则：唯一名、对称依赖、无环、实体唯一所有权）+ mermaid 人类视图 + ADR（`decisions.md`，ADR-NNN 结构）；组件边界多解时给 Option A/B + 推荐由团队在门选择（记录 Alternatives Rejected）；实体只捕获 ownership+shape（完整 schema 留给 Functional Design）。门可三选项 "Add Units Generation"。

**2.7 units-generation**（ALWAYS；produces: unit-of-work, unit-of-work-dependency, unit-of-work-story-map, traceability；评审: architecture-reviewer advisory on unit-of-work；sensors: +traceability；scopes: enterprise/feature/mvp/classic/workshop）
分解计划问题（边界策略/粒度/依赖排序/集成点，**不问实现顺序**——那是 2.9 的经济决策）；**计划批准门**（Approve Plan / Revise Plan）；产出 `unit-of-work.md`（`U{n}` ID、目录名、kind: service/spec/ui/packaging/library、复杂度 S/M/L/XL）、`unit-of-work-dependency.md`（依赖 DAG + **REQUIRED 机器可读 fenced yaml 边块**——下游 batch fan-out 由此计算，required-sections 传感器校验其 well-formed 且无环）、故事映射与 traceability。unit 名规则：小写路径段标识 ≤64 字符。与 2.9 在编译网格中同进退。

**2.8 contract-design**（CONDITIONAL：>1 个须集成的单元、或有暴露外部消费的公共 API；produces: contract-summary；评审: architecture-reviewer advisory；scopes: enterprise/feature/mvp/classic/workshop）
识别两类边界（单元间 / 公共外部 API）；契约被当作"两家公司间的 B2B 协议"；产出单工件 `contract-summary.md`：契约表（Provider/Consumer/Mechanism/Owner）+ 每契约 fenced spec 块（OpenAPI/AsyncAPI/shared-schema）+ 所有权规则 + 未决问题表。外部 API 单单元系统仍需此阶段固定——无其他阶段拥有外部 API 规范。

**2.9 delivery-planning**（ALWAYS；produces: bolt-plan, team-allocation, risk-and-sequencing-rationale, external-dependency-map, questions；consumes: requirements/components/unit-of-work/unit-of-work-dependency(required)；scopes: enterprise/feature/mvp/classic/workshop）
**Inception capstone**。战略问题（先建什么、WSJF 评分、Bolt 大小、并行/串行、外部依赖）+ per-Bolt 问题；产出有序 Bolt 序列（每 Bolt 含 Unit(s)、walking-skeleton 标记、DoD、confidence hypothesis、预期 demo）、Bolt→mob 分配、排序理由（**偏离拓扑序必须记录**——Bolt 排序是经济的而非拓扑的）、外部依赖图。跑 **Inception→Construction 完整性审计**。门后做三个 Construction 配置：iteration 分类（`unit-major` vs 默认 `stage-major`）、staffing（`set-unit-ownership team`/`solo`）、Team check-in rhythm（`per-stage`/`unit-end`）。

### Phase 3 — Construction（7 个）

**3.1 functional-design**（CONDITIONAL；for_each: unit-of-work；produces: entities, rules, functional-spec, traceability + optional: frontend-components(ui)；**produces_kinds** 按 Unit kind 裁剪；评审: architecture-reviewer on functional-spec；sensors: +linter/type-check/traceability；scopes: enterprise/feature/mvp/refactor/classic/workshop）
设计阶段（≤15 行伪代码，完整实现留给 code-generation）；产出 entities.md（fenced yaml source-of-truth）、rules.md（`BRx.y` 编号业务规则）、functional-spec.md（工作流与状态机的 source of truth）、条件 frontend-components.md；traceability.json（AC→BRx.y，`reverse` 数组解释无 AC 的规则）。三种执行模式：QUESTION-ONLY / ARTIFACT-ONLY / Full（由 orchestrator 在 Bolt 的问题相/设计相控制）。

**3.2 nfr-requirements**（CONDITIONAL；for_each；produces: 5 类 NFR requirements + tech-stack-decisions + traceability；produces_kinds；评审 on security-requirements；sensors: +linter/type-check/traceability；scopes: enterprise/feature/mvp/infra/security-patch/classic/workshop）
五类 NFR（性能/安全/可扩展/可靠/可观测）量化目标；**NFR ID 继承子号契约**（inception 的 NFR4 → 细化 NFR4.1）；traceability（NFR{n}→NFRx.y，N/A 需理由）。

**3.3 nfr-design**（CONDITIONAL：NFR Requirements 执行过才跑；for_each；produces: 5 类 NFR design + logical-components + traceability；评审 on security-design；consumes 7 required；scopes: enterprise/feature/mvp/infra/classic/workshop）
设计五类 NFR 具体方案（韧性/扩展/性能/安全/可观测模式）+ `logical-components.md`（服务边界/故障域/爆炸半径——桥接 NFR 设计与基础设施设计）。

**3.4 infrastructure-design**（CONDITIONAL；for_each；produces: infrastructure-specification, monitoring-design, cicd-pipeline, traceability；评审 on cicd-pipeline；consumes 9 required；scopes: enterprise/feature/mvp/infra/classic/workshop）
四大领域：部署架构、基础设施服务、监控可观测性、CI/CD 流水线；**表格优先**（prose 仅用于理由）：部署表/服务表/共享基础设施表、指标/告警/SLI-SLO/日志追踪表。

**3.5 code-generation**（ALWAYS；for_each: unit-of-work；mode: **subagent**；lead: developer；**workspace_requires: true（唯一声明者）**；produces: code-generation-plan, unit-test-instructions, code-summary, traceability + 源码写到工作区根；评审 on code-generation-plan；sensors: required-sections, linter, type-check, traceability（**有意不导入 upstream-coverage**）；scopes: 10 个（infra 跳过））
框架中最重装的阶段：
- **Part 1（计划）**：读该单元全部设计工件 → 生成带复选框的 `code-generation-plan.md`（story→code 步 traceability + 强制测试文件步）+ **确定性 Testing Contract**（`aidlc-testing-posture.ts render`，TDD/BDD/ATDD/custom/test-after 顺序）+ `unit-test-instructions.md`（命令限定本单元）；
- **Plan Approval 门**：Approve Plan / Request Changes，含目标绑定 `fingerprint` 与受保护 session 挑战/响应——**除 Build-and-Test loop-back 重放外无例外**；
- **Part 2（执行）**：派发 developer subagent 逐步执行（brief 以 `AIDLC-UNIT:` / `AIDLC-STAGE:` 标记 + `AIDLC-TESTING-CONTRACT` hash 开头）；
- **收尾**：code-summary.md、**`source-manifest.json`**（严格 schema，记录每个应用源路径——引擎校验，未认领的应用源变更 fail-closed）、traceability.json。
- 测试地板加性：mvp/enterprise/feature/infra +80% 行覆盖；bugfix/security-patch +目标回归。**Swarm 触发耦合**：`for_each` + `mode: subagent` 是 swarm 的字段匹配条件。

**3.6 build-and-test**（ALWAYS；在所有 per-unit 阶段结束后执行一次；lead: quality（devsecops）；produces: build-instructions, integration/performance/security-test-instructions, build-and-test-summary, build-test-results, cross-unit-traceability；sensors: required-sections, upstream-coverage, type-check（**有意不导入 linter**——规范 lint 在 CI 流水线里跑））
构建源码完整质量目标清单（每目标稳定 ID）；**Target Verification Matrix**（Target ID/Source/Expected/Actual/Evidence/Owning Stage/Verdict，无 Pending 残留）；实际执行构建与测试（命令去重、每命令跑一次）；写 `test-results.md`（含 **`## Loop-Back Log`** 附录）；跑跨单元最终覆盖门（每个 FR/NFR/AC 至少一个 OK）。**失败升级阶梯**：① 阶段内修复（最多 2 次）→ ② 分类并估算影响（绝不基于未估算影响声称无路可走）→ ③ **自治有界回跳 3.6→3.5**（仅 autonomous 模式；Loop-Back Log 上限 3 条；MODIFY 勿 REDO）→ ④ **halt-and-ask**（带影响估算的停机问题；放弃是人类的决定）。

**3.7 ci-pipeline**（CONDITIONAL：CI 需创建或显著修改时；lead: pipeline-deploy；produces: ci-config, quality-gates, questions；consumes: code-summary/build-and-test-summary/build-test-results(required)；sensors: +linter/type-check；scopes: enterprise/feature/mvp/infra/classic/workshop）
CI 配置（buildspec.yml/workflow YAML）、质量门定义、制品仓库配置；跑 **Construction→Operation 边界验证**（`phase-check-construction.md`：读 cross-unit-traceability 与各 code-generation traceability，确认全单元构建测试、跨 Unit FR/NFR/AC 门通过、CI 质量门执行记录的命令）。增量 infra scope 从 repo 本身检测现有 CI。

### Phase 4 — Operation（7 个）

**4.1 deployment-pipeline**（CONDITIONAL：CD 流水线需创建/显著修改时；lead: pipeline-deploy；produces: cd-config, deployment-strategy, rollback-runbook, questions；consumes: ci-config/quality-gates/infrastructure-specification/cicd-pipeline(required)；scopes: 9 个（mvp/poc 跳过））
部署策略（蓝绿/金丝雀/滚动）、环境晋升门（dev→staging→prod）、生产审批流、回滚程序、特性旗标策略。增量 scope（bugfix/refactor/security-patch/express）跳过 CI/Infrastructure 设计时，从工作区现有流水线与 codekb 取证，**绝不发明缺失工件**；Express greenfield 无可部署目标时 `report skipped`。

**4.2 environment-provisioning**（CONDITIONAL：AWS 环境需开通/验证时；lead: aws-platform（devsecops, compliance）；produces: environment-inventory, validation-report, questions；consumes: infrastructure-specification/cd-config(required)；scopes: enterprise/feature/infra/classic/workshop）
用 Construction 的 IaC 开通目标环境；VPC/子网/安全组/NACL、Secrets Manager/Parameter Store 注入、跨账户/跨 VPC 连通性验证；devsecops 做安全姿态验证；产出环境清单、验证报告、密钥审计、健康检查结果。

**4.3 deployment-execution**（CONDITIONAL：流水线与环境就绪后；lead: pipeline-deploy（developer）；produces: deployment-log, smoke-test-results, health-check-report, questions；consumes: cd-config/deployment-strategy/environment-inventory/build-test-results(required)；scopes: 9 个）
预部署检查（数据库迁移、依赖服务健康、部署窗口）→ 推送制品过流水线 → 冒烟测试 → 健康检查 → 数据库迁移（委派 developer subagent 执行）。增量 scope 的降级路径明确：跳过 Environment Provisioning 的 scope 从工作区真实配置盘点目标环境；现有流水线足够时 Deployment Pipeline 的缺失产物是**按设计的**（走文档化 fallback，不触发缺失恢复）。

**4.4 observability-setup**（CONDITIONAL：监控/仪表盘/告警/追踪需配置时；lead: operations；produces: dashboards, alarms, slo-config, log-queries, tracing-config, anomaly-config, questions；consumes: performance/security/reliability-design + monitoring-design + infrastructure-specification(required)；scopes: enterprise/feature/infra/classic/workshop/express）
黄金信号（延迟/流量/错误/饱和度）、SLO/SLI 定义、CloudWatch 仪表盘配置、告警定义（严重度/SNS 路由/升级）、Logs Insights 保存查询、X-Ray 追踪、异常检测。Express 缺 NFR/Infra 设计时从已批准需求 + 部署证据推导最小可观测面，观测不到的 SLO 决策向人提问。

**4.5 incident-response**（CONDITIONAL：需要运维 runbook 与事件响应程序时；lead: operations；produces: runbooks, incident-plan, escalation-matrix, questions；consumes: dashboards/alarms/reliability-design/security-design/infrastructure-specification(required)；scopes: enterprise/feature/classic/workshop）
故障模式分析、升级路径与值班轮换、自动化修复、事件通信程序、RTO/RPO 目标；产出 SSM Automation runbook 库、事件响应计划（集成 AWS Incident Manager）、升级矩阵、灾难恢复程序、AWS Backup 配置。ARS 中 `cost: null`（无法数值筛查的阶段之一）。

**4.6 performance-validation**（CONDITIONAL：NFR 性能目标需负载验证时；lead: quality；produces: load-test-plan, load-test-results, nfr-validation-matrix, questions；consumes: performance/scalability requirements+design + dashboards(required)；scopes: enterprise/feature/classic/workshop）
流量模式（稳态/峰值/突发）、目标延迟分位（p50/p95/p99）、吞吐量；设计负载测试计划、在类生产环境执行、用 CloudWatch/X-Ray 证据分析；产出瓶颈分析、自动扩展验证、容量规划建议、NFR 验证矩阵（目标 vs 实际）。

**4.7 feedback-optimization**（CONDITIONAL：持续运维监控与优化；lead: operations（aws-platform）；produces: slo-report, cost-analysis, drift-report, feedback-loop, questions；consumes: dashboards/alarms/slo-config/deployment-log(required) + load-test-results/incident-plan(optional)；scopes: enterprise/feature/classic/workshop）
**最终阶段**。SLO 合规与错误预算消耗率、成本优化机会（Cost Explorer）、配置/基础设施漂移（AWS Config）、Trusted Advisor 建议、运维自动化；产出 feedback-loop 文档（反馈进下一轮 Ideation）。三选项门：Approve（**工作流完成**）/ Request Changes / **Start New Ideation Cycle**。ARS 中另一个 `cost: null` 阶段。

## 14. Stage 文件契约（frontmatter 完整 schema）

`protocols/stage-definition.md` 是所有阶段文件的权威格式契约（`aidlc-stage-schema.ts` 实现之）。文件布局 = YAML frontmatter + 三个正文槽（`## Steps` 必需且总是填充；`## Sensors`、`## Learn` 为保留槽）。

**手工编写字段**：

| 字段 | 必需 | 约束 | 含义 |
|------|------|------|------|
| `slug` | 是 | kebab-case，**必须与文件名主干匹配** | 阶段唯一标识 |
| `phase` | 是 | 五相之一（小写） | 所属阶段 |
| `execution` | 是 | `ALWAYS` / `CONDITIONAL` | 是否无条件执行 |
| `condition` | 是 | 自由文本 | ALWAYS 时为始终开启的理由；CONDITIONAL 时为分支条件 |
| `lead_agent` | 是 | agent slug，动态对 `.aidlc/agents/*.md` 校验 | 主导 agent |
| `support_agents` | 是 | 可空数组；pipeline 模式时 lead+support 必须唯一 | 支持 agent |
| `mode` | 是 | `inline`/`subagent`/`pipeline`/`mob`/`agent-team` | 通信拓扑（`agent-team` 保留——读取时必须显式拒绝，不得落默认路径） |
| `reviewer` | 可选 | agent slug | 产物后、门前调用 |
| `review_artifact` | 有 reviewer 时必需 | 命名 `produces[]` 中一个 Markdown 条目 | 拥有 `## Review` 附录的精确工件 |
| `reviewer_max_iterations` | 可选 | 正整数，默认 2 | 评审最大迭代 |
| `review_class` | 可选 | `adversarial`（默认）/ `advisory` | 评审强度；scope `review_cap` 与 `--review` 只能降低不能升高 |
| `summary_confirmation` | 可选 | `required` / `if-present` | 合并摘要确认检查点 |
| `for_each` | 可选 | artifact slug | 对该工件每个实例运行一次（引擎校验其由上游产生） |
| `workspace_requires` | 可选 | 默认 false | 必须写源码到工作区根；仅 code-generation 声明 |
| `produces` | 是 | 可空，小写-kebab | 产出工件 |
| `consumes` | 是 | 可空，`{artifact, required, conditional_on?}` | 消费工件；`conditional_on: brownfield/greenfield`；`required: true` = "若生产阶段运行则必须被满足"（非全局断言） |
| `requires_stage` | 是 | 可空 | 双重角色：语义依赖 + 呈现序边（`display_order` 主要输入） |
| `scopes` | 可选 | scope 名 | **该 scope 下 EXECUTE** 的标记（per-stage 转置）；缺失=SKIP |
| `inputs` / `outputs` | 是 | 人类散文 | `outputs` 运行时不承重——引擎永不读它做路径解析 |

**计算字段**（编译产物中）：`display_order`（`<phase-prefix>.<sequence>`，按 `requires_stage` 拓扑排序 + slug 字母序平局）、`name`。

**产物路径引擎解析**：阶段只发相对工件**名**；引擎在 directive 发出时针对活跃 intent record 目录解析规范写路径；`consumes` 只列磁盘上存在的路径，缺失的必需输入移入 `consumes_absent`（`expected: true` = 按 scope 设计缺席；`expected: false` = 真实缺口，走恢复协议）。

**保留扩展命名空间**（schema 拒绝未知键）：`when`、`on_failure`、`blocks_on`、`timeout`/`retry`。

## 15. Scope 系统（11 个 scope 与 EXECUTE/SKIP 网格）

### 15.1 Scope 文件格式

`.aidlc/scopes/aidlc-<name>.md` 的 frontmatter：`name`、`depth`（Minimal/Standard/Comprehensive——决定提问与文档详尽度）、`keywords`（自动推断触发词，如 bugfix 的 fix/bug/broken）、`description`、`skeleton`（on/off——是否跑行走骨架仪式）、`review_cap`（评审上限）、`runner`（是否有独立 runner 技能）。正文说明阶段成员矩阵及理由。

### 15.2 网格总览（`scope-grid.json` 编译产物）

| Scope | 深度 | EXECUTE/33 | init / ideation / inception / construction / operation | 定位 |
|---|---|---|---|---|
| enterprise | Comprehensive | 33 | 3/3 · 7/7 · 9/9 · 7/7 · 7/7 | 全量全流程最深文档 |
| feature | Standard | 33 | 3/3 · 7/7 · 9/9 · 7/7 · 7/7 | 完整特性全 stage |
| classic | Standard | 26 | 3/3 · 0/7 · 9/9 · 7/7 · 7/7 | **隐含默认**（复现 v1：跳过全部 ideation） |
| workshop | Standard | 26 | 同 classic（测试量 Minimal） | 研讨/教学 |
| mvp | Standard | 23 | 3/3 · 4/7 · 9/9 · 7/7 · 0/7 | 免掉全部 operation |
| infra | Standard | 13 | 3/3 · 0/7 · 2/9 · 4/7 · 4/7 | 基础设施变更（跳过 RE 和 code-generation，但执行 infra-design + CI/CD） |
| express | Minimal | 10 | 3/3 · 0/7 · 2/9 · 2/7 · 3/7 | 最轻运行：需求到部署，无设计 pass、无评审者 |
| refactor | Minimal | 10 | 3/3 · 0/7 · 2/9 · 3/7 · 2/7 | 重构 |
| security-patch | Minimal | 10 | 3/3 · 0/7 · 2/9 · 3/7 · 2/7 | CVE 响应 |
| bugfix | Minimal | 9 | 3/3 · 0/7 · 2/9 · 2/7 · 2/7 | 修复增量路径 |
| poc | Minimal | 8 | 3/3 · 1/7 · 2/9 · 2/7 · 0/7 | 概念验证最短路径 |

要点：初始化三阶段全部 scope 必跑；最小主干 = reverse-engineering + requirements-analysis + code-generation + build-and-test + deployment-execution；2.7 与 2.9 同进退。

### 15.3 Scope 解析优先级

`--scope` 旗标 > compose 批准 > 关键词推断 > `AWS_AIDLC_DEFAULT_SCOPE` 环境变量 > `classic` 默认。`--depth`、`--test-strategy`、`--review` 三个独立覆盖点进一步调节。已存在工作流重跑时，**state 文件里记录的 scope 总是赢**（重跑即恢复）。

## 16. 自适应 Composer 与 ARS 评分

### 16.1 ARS（Autonomy Risk Score）确定性算术

数据源 `data/ars-priors.json`（`aidlc-graph.ts ars` 的唯一事实源）。**所有值是未校准先验；合成分数仅是门禁处给人看的咨询性指标，没有任何确定性逻辑据此路由。**

- **五分量权重**：IAE（意图歧义）0.2 / CSU（代码库结构不确定性）0.3 / VE（验证熵）0.25 / R（风险/爆炸半径）0.15 / UA（未决假设）0.1；
- **分量带**：low ≤0.3 < med ≤0.7 < high；
- **合成 5 档**：0-20 Near-direct / 21-40 Focused / 41-60 Standard / 61-80 Comprehensive / 81-100 Full ceremony；
- **EV 阈值**（阶段成本档→期望值阈值）：cost1→0、cost2→0.2、cost3→0.3、cost4→0.4、cost5→0.5；
- **每阶段先验**：`targets`（该阶段降低哪些分量）、`cost`（1-5）、`role`（initialization/core/phase-gate/structural）、`projectTypes`（如 reverse-engineering 仅 brownfield）。`cost: null` 的两个阶段（incident-response、feedback-optimization）报告为"无法数值筛查"而非编造成本；`role: structural` 的阶段（units-generation、contract-design、delivery-planning）机械式默认 SKIP。

### 16.2 Composer 工作方式

`aidlc-composer-agent`（810 行，最长 agent 文件）：跑只读 `detect` 扫描（CodeKB 优先的单一证据源策略，CodeKB 调用预算 ≤4 次写在正文程序里）→ 按打分锚点表估五分量 → 逐 stage 期望价值决策（EXECUTE/SKIP，每个 SKIP 附理由）→ `aidlc-graph.ts validate-grid` 校验 → 返回结构化提案。`mode` 由校验器的 `nearest_stock` 距离路由 matched/custom——matched 提案携带重验证的股票网格原样，**写无 scope 文件**；conductor 永不自行比较网格重推结论。

---

# 第五部分：协议与执行质量

## 17. Conductor 人格手册（conductor.md）

引擎把它烘焙进工作流**首个** `run-stage` directive 的 `conductor_persona` 字段（无任何 skill 通过路径引用它）。核心定位：SKILL.md 的转发循环是"机制"，conductor.md 是不可再简化的"知识工作"——如何把引擎点名的 stage 跑**好**。

### 17.1 人格框架（三种进入方式）

- **inline stage**：加载 lead agent 的扁平人格文件，以其领域专家口吻执行；知识加载按固定顺序（memory → shared → agent → team-shared → team-agent → 前序工件）。
- **subagent stage**：由 harness 原生分发边界加载人格并执行投影的模型/工具策略；上下文经 prompt 传入（subagent 看不到会话历史）；**绝不自己注入人格文本**。
- **多 agent stage**：加载 ensemble 协议；不可再简化的规则——**你是总线（bus），lead 拥有最终 `produces[]` 工件；禁止在 inline stage 派发 support agent；agent 之间永不互相调用，只有 conductor 委派**。

### 17.2 阶段日记（memory.md 四格）

- 位置：`directive.memory_path`（`<record>/<phase>/<stage>/memory.md`），引擎发 directive 时已从 `memory-template.md` 创建好——**绝不用 read 探测可能不存在的文件**；罕见缺失时用一条幂等命令引导创建，**永不覆盖**（重入/恢复要保留既有条目）。
- 四个规范 H2：**Interpretations / Deviations / Tradeoffs / Open questions**，追加带 ISO 时间戳的要点。
- 批准后 memory.md 留在原地作为永久记录；§13 门要读它。**日记是唯一手工维护的文件**——其余（状态字段、复选框、审计行）全是工具所有。

### 17.3 阶段内修订循环（Keep / Modify / Redo）

门处用户要求改动时共同决定：原样保留 / 就地修改 / 整段重做，然后重跑相关部分重新呈现门。每一轮都经引擎报告：`report --result rejected --user-input "Request Changes" --reason "<feedback>"`；修订后（若 `produces[]` 工件变了且 directive 带 reviewer，**先重跑 §12a 评审**——新派发记录、新 `## Review` verdict）再 `report --result revised` 重开门。绝不绕开这些调用。

### 17.4 walking-skeleton 立场分类（`gate: "unresolved"`）

1. 读团队 `## Walking Skeleton` 段（解析顺序 org → team → project，最具体的非空声明获胜）；
2. 分类：`always`/`every greenfield feature` → `on`；`never` → `off`；`scope-dependent`/未指明/team 层为空 → `scope-dependent`（引擎回退到活动 scope 文件的 `skeleton:` 字段）；
3. `report --skeleton-stance <on|off|scope-dependent>`，下一次 `next` 以已确定的布尔 gate 重发同一阶段。

**PRACTICES_OVERRIDE 判定归 conductor**：bolt-plan 标记与团队 practices 冲突时 **practices 获胜**（团队的常驻声音 > 某工作流的解释），报告立场前先 `aidlc-state.ts practices-event --type override` 发 `PRACTICES_OVERRIDE`。

### 17.5 任务侧栏可观测性

阶段级 todowrite 驱动侧栏 spinner：跑 stage 前把上一 stage 任务标 `completed`、当前标 `in_progress`，`activeForm` 必须含 `[slug]` 后缀（PostToolUse 钩子解析它同步状态）。压缩后任务 ID 丢失时用任务列表按主题找回。任务 ID 仅存于侧栏，**从不存入状态**。

## 18. 主协议 stage-protocol.md 详解

1242 行，引用最广的协议。除语音契约（§10）外：

### 18.1 Critical Compliance Checklist（最常漏的 6 步）

1. **所有生命周期转换走引擎**（`report awaiting-approval` → `approved`/`rejected` → 修订后 `revised`）；阻塞性传感器拒绝是单独记录的非门决策（Fix findings / Override blocking sensors 二选一，**autonomous 模式永不出 override**）；条件不适用报 `skipped --reason`。绝不直接调 `aidlc-state.ts` 动词或单独调 `aidlc-audit.ts append`。
2. 非门问题用 `aidlc-log.ts` 记 decision/answer 对。
3. **绝不总结用户输入**——用精确选项标签。
4. 任务转换 + 状态同步（`activeForm` 带 `[slug]`；approve 自动前进，不另调 advance）。
5. **Stage 仪式原子性**：question → artifact → reviewer → learnings → gate 全链必须执行；"跳到 stage X"只跳中间 stage 不省目标 stage 仪式。唯一例外：Build-and-Test 失败回跳。
6. **自主性绝不推断**。

### 18.2 §1 Approval Gates 细则

- **HARD STOP**：呈现批准门后立刻结束回合等用户新消息，期间不调任何工具。
- **NO EMERGENT BEHAVIOR**：Construction/Operation 只用标准 2 选项完成消息；只有 Ideation/Inception 可条件性加第 3 选项（补跑之前跳过的 stage）。两个特例：修订循环逃生舱 + Build-and-Test 失败回跳。
- `[next stage]` 占位符逐字取自 directive 的 `next_stage` 字段，为 null 时渲染 "Complete workflow"，**绝不猜测**。
- **修订循环逃生舱**：同一 stage 3 轮 Request Changes 后加第 3 选项 "Accept as-is"；第 2 轮后要预告"再修订一次将出现 Accept as-is"。
- **不匹配回复处理**：Other 逃生只是 UI 选项、不算持久答案——讨论后重发同一问题；不匹配则简短引用原话、说明不匹配、重发全部选项并结束回合。`--user-input` 必须转发精确选中的标签。

### 18.3 §3 问题格式（深度感知提问）

- 问题文件永远是真相源：A-E 选项 + 必以 `X. Other (please specify)` 结尾（Consolidated Summary 是唯一例外）；多选加 "(select all that apply)"。
- **深度感知**：stage 文件的示例问题是指引非脚本。提问量三因素：深度级别（Minimal ~2-4 / Standard ~5-8 / Comprehensive ~8-12+）、项目上下文、阶段推进（Ideation 最多问为何/为谁/市场，Inception 中等问需求/架构，Construction 最少——问题"例外而非例行"，Operation 偶发定点）。**是引导不是硬上限**。
- **绝不重问已答问题**：递归读所有 `*-questions.md`；审计只看 pairing（`DECISION_RECORDED` 必须配同 scope 的 `QUESTION_ANSWERED`）；不确定时发一个点名旧答案的窄追问。
- **问题必须自解释**：展开每个标识符（"导出须在 5 分钟内完成的需求（FR3）"而非 "FR3 还对吗？"）。
- **矛盾检测四类**（所有深度下强制）：scope 错配、风险错配、技术冲突、时间线 vs scope——逐条并陈、解释、定点追问，消解前不前进。
- **过度自信防范**：红旗清单（单字回答、"随你便"、放松已定质量目标）。
- **每回合结束前把所有待答问题写入问题文件留空标签**——Stop 钩子靠它区分"真等人"与"弃工"。

### 18.4 三种提问模式（Tri-mode）

1. **guided**：分批结构化问题呈现（每批 ≤4 个，5+ 选项时每题一条消息）、每批立即回写 `[Answer]:`、独立时间戳；最后过 Consolidated Summary 确认（打 `aidlc-review-brief.ts summary` 决策简报，工具拒绝自选答案/无匹配 prompt/文件不一致）。
2. **self-guided**：用户自己编辑文件，等 "done/ready"，读完仍要同一确认检查点。
3. **chat**：自然对话抽答案，写回文件带 `**Mode:** chat`，同样确认。
可中途换模式；最后校验所有标签已填。

### 18.5 其它章节速览

- **§4 状态跟踪/§2 审计**：`[ ] / [-] / [?] / [R] / [x] / [S]` 复选框记法；工具调用一律绝对路径避免 CWD 漂移；审计 `User Input` 字段必须是**完整未修改的原始输入**；`aidlc-audit.ts append` 是窄诊断逃生舱，**拒绝**权威收据类事件（HUMAN_TURN、GATE_*、QUESTION_ANSWERED、REVIEW_*、SWARM_*、UNIT_* 等由专属工具发射）。
- **§8 深度与测试策略**：scope→深度映射表；测试策略 Minimal=Nyquist 模型（每需求 1 个可验证测试 + 每组件 1 快乐路径，约 5-15 个）；Standard/Comprehensive 按组件 5-8 / 10-15 个，测试金字塔 75/20/5。
- **§9 术语表**：Phase/Stage/Scope/Bolt/Autonomy mode/Walking skeleton/Ladder prompt/Parallel batch/Walk order（stage-major vs unit-major）/Unit of Work/Worktree 等。
- **§10 内容校验**：Mermaid 语法 + 文字回退；模板覆盖顺序（team template → framework default → stage 散文，required-sections 传感器用同一顺序核对）；ASCII 图禁制表符（U+2500-257F）；字符转义。
- **Artifact Re-use**：Keep/Modify/Redo 三选项 + `reuse-artifact` 收据，全 stage 适用；回跳后前放重放的确定性覆盖（目标 unit=Modify、其余=Keep、build-and-test 重入=Modify，**Redo 被禁**以免抹掉 Loop-Back Log）。
- **§14 Sensor imports**：`sensors:` frontmatter 是完整导入集；`fire_on: write` 始终 advisory；`fire_on: gate` 阻塞性需验证通过；autonomous 不能 override 阻塞传感器。

## 19. 其余 7 个协议模块详解

### 19.1 stage-protocol-construction.md（Construction 专属）

会话首个 Construction directive 和每次 `invoke-swarm` 时加载。所有 Bolt/skeleton/ladder/per-Unit 仪式**仅在引擎解析出非空 Unit DAG 时适用**（零 Unit 指令当普通 stage 跑一次）。

- **walking-skeleton 门**：Unit DAG 非空且立场为 on 时，首个 in-scope Construction EXECUTE 阶段**无论自治模式与否都呈现阶段级批准门**（覆盖已 settle Units 的该阶段工件）。
- **Ladder prompt（一次性）**：skeleton 门批准后只发一次——"The walking skeleton shipped. How should the remaining Bolts run?" → **Continue autonomously** / **Gate every Bolt**，经 `aidlc-bolt.ts set-autonomy` 记录（发 `AUTONOMY_MODE_SET`）；**不走 decision/answer**（会消耗人类新鲜回合）。autonomous 跳过剩余 Construction 阶段门，但 halt-and-ask、回跳 rung 4、swarm settle 重入除外。会话恢复时若模式未设但 skeleton 已 `[x]`，先重发梯子。
- **halt-and-ask**：任何模式下 Code Generation 失败都停。Solo 失败立即 halt（发 `BOLT_FAILED`）给 Retry / Skip / Abort；并行批部分失败时等全部 Task 返回、保留成功 Unit 工件、给精确点名的三选。**两变体**：有候选修复（影响估算含 effort/financial/risk + `Loop-backs used [N]/3`）→ Retry with fix / Accept failure / Abort；无可识别修复（无可换维度：库/版本/镜像/实例类型/算法/flag）→ 只 Accept failure / Abort。**绝不渲染带编造修复的模板；无影响估算的放弃选项 = 违规**。
- **Build-and-Test 失败回跳（3.6→3.5）**：根因在生成代码或 code-gen 选型时可回跳修复；是 NO EMERGENT BEHAVIOR 与"先完成当前 stage"的**正式豁免**——失败运行故意保持 in-flight，其门不呈现、§13 推迟到最终通过运行。回跳计数器 = `test-results.md` 的 `## Loop-Back Log` 条目数（每 intent 上限 3，选它而非审计行因为它能越过回跳且与诊断同处；append-only；人类定向回跳不计）。**重放需重走 Plan Approval**：跳建新授权纪元——保留 Loop-Back Log 但清空 `[Answer]:`、重生成目标绑定指纹、重跑完整收据序列。自治回跳程序：记条目（诊断/根因阶段/计划修复/影响估计）→ 引擎验证后跑 `next --stage code-generation`（打印经验证的 `aidlc-jump.ts execute` 命令，逐字执行，发 `STAGE_JUMPED`）→ 新 Plan Approval 硬停 → 只修诊断点名的 unit（确定性 Artifact Re-use）→ 全部 unit 有 fresh 评审后以 `--user-input "Autonomous loop-back N per construction protocol module"` 自动批准（人类已批原运行，这是修复非新自主推断）。
- **引擎驱动的 per-Unit 迭代**：每次 `next` 发一个 unit 一个 `run-stage`（Bolt 构建序）；未 settle 的 unit 一律 `gate: false`；**最后一个 unit settle 后的重入才呈现一次真正的门**（单阶段级批准覆盖全部 unit）；还有 unit 未 settle 时 `report --result approved` 被拒。Unit 生命周期收据：`unit start` → 写工件 → `unit complete`（校验每个必需工件是磁盘常规文件）；暂停 `unit pause --reason --next-action`（暂停的 unit 路由优先并硬停循环，须显式 `unit resume`）；同时只开一个活动 Unit；**一旦出现任一收据，之后每次尝试都留在 receipt mode**。每生命周期行带精确 stage-attempt `Run floor`（`<boundary-event>:<timestamp>#<ordinal>`；因果无序时用确定性 `AMBIGUOUS:<ts>#<digest>`）。
- **Unit-major 迭代（opt-in）**：`Construction Iteration: unit-major` 时按"每个 Unit（外循环）× 每个 per-unit stage 图序（内循环）"走——**一个 Unit 的设计文件连续写完并被 BUILD，才开下一个 Unit**，首个可用代码在第一个 Unit 设计后落地。`directive.stage` 可能命名比 Current Stage 更晚的阶段——**总是按 directive 自己的 stage+unit 行动，绝不看 Current Stage**。autonomous swarm 在 unit-major 下永不触发。
- **Team-owned Unit Progress（opt-in，仅 unit-major）**：`Unit Ownership: team` 时引擎每次 `next` 重写 `## Unit Progress`（引擎所有的派生投影，手改会被覆盖）；`Unit Gate Rhythm: per-stage`（默认）/ `unit-end`；团队 unit 的所有非门调用都加 `--unit`；另有 team claim 与 scoped checkout（原子注册表 `claim/<intent-id8>/<unit>`、`participate`/`release`）、pinned Unit merge-back（`publish`/`pin`/`land` 事务）。
- **§12b 自治代码生成计划契约**：`invoke-swarm` 改变"在哪里生成"而非"是否规划与批准"——`prepare` 前在主工作区为每 unit 执行 Part 1 至 Plan Approval（含 Testing Contract、Approval Fingerprint、逐 unit 硬停）；**每个 worker brief 必须以两行开头**：`AIDLC-UNIT: <unit>` 和 `AIDLC-TESTING-CONTRACT: <contract_sha256>`；worker 必须产出 `source-manifest.json`；Testing Contract 权威（worker 不重解析 memory，重试复用同一已批字节）。

### 19.2 stage-protocol-ensemble.md（多智能体拓扑）

角色恒定：**lead 拥有 `produces[]`；support 是写自己工作的真实参与者；reviewer 事后从外部验证；orchestrator 在所有拓扑上都是总线——agent 之间每次交换都是它发起的 dispatch 与承载的 return，agent 互不调用**。

- **贡献文件（contribution file）**：每个被派发的 support 写 `<record>/<phase>/<stage>/contributions/<agent-slug>.md`；首行身份标记逐字 `**Collaborator:** <agent-slug>` + `## Contribution`（可整合实质内容）+ `## Positions`（`AGREE:`/`OBJECT:` 要点，`None`=完全同意）。单独成文件使并行派发不冲突；异议留在磁盘（永久记录）而非临时返回文本。
- **四种拓扑**：**inline**（support 只是 conductor 采纳的视角，先产 lead 输出再逐层加入 support 视角综合，无派发无 contribution）；**subagent（hub-and-spoke）**（dispatch lead 出草稿 → 对草稿派发每个 support——**互相致盲**：没有谁的 brief 含另一个的 contribution——各写 contribution → 最后再 dispatch lead 整合）；**pipeline（链式）**（`directive.pipeline.links` 声明顺序，`completed` 是恢复账本；每 link 看到全部上游并直接推进工作产品，返回后先 `aidlc-log.ts link` 铸收据再发下一个；最后的 link 让 `produces[]` 完整；多 repo 每 repo 一条链）；**mob（mesh，有界两轮）**（Round 1 并行互盲 → lead 整合 → 异议分诊：judgment calls 中途浮给人类[autonomous 下记录后最终批门浮出]、knowledge disputes Round 2 仅重派异议 agent；维持的异议在门完成摘要**逐字引用**）。
- **并发不是契约**：不能并行的 harness 上 subagent 辐条与 mob round-1 顺序跑、**brief 不变**——"谁看见什么"是不变量。
- **NOT-READY 修复**：任何拓扑只重召 **lead alone**（合奏只聚一次，修复环是 lead-reviewer 乒乓）。
- **完成证据（确定性）**：mob/subagent-with-supports 缺任一 contribution 文件或首行缺身份标记 → **拒绝进 gate/完成**；pipeline 缺 current-attempt `PIPELINE_LINK_COMPLETED` 收据 → 拒绝；`ARTIFACT_REUSED`（Decision: keep）豁免复用 repo；带 `single-stage:<slug>` 身份的孤立收据永不满足主工作流。逃生舱 `AIDLC_DISABLE_ENSEMBLE_EVIDENCE=1` 仅限合法的证据丢失场景。
- **Subagent 返回摘要固定格式**：`## Subagent Summary: [Stage]` → Produced / Key Decisions / Issues·Concerns / Next Steps 四节；orchestrator 前进前必读；Issues 非空必呈用户；Produced 少于预期必调查；**不重复已在磁盘的工件正文**。
- **失败恢复**：Task 失败 → ①缩上下文重试一次 → ②再失败给两选项结构化问题（"Run it here" / "Skip and revisit"）→ ③记审计。

### 19.3 stage-protocol-governance.md（阶段边界验证）

32 行的短文件。三个边界：Ideation→Inception（approval-handoff 后）、Inception→Construction（delivery-planning 后）、Construction→Operation（ci-pipeline 后）。**Initialization→Ideation 无治理边界检查**。
流程：读 `knowledge/aidlc-shared/verification.md` 方法论 → 跑该阶段特定的可追踪性检查 → 写 `<record>/verification/[boundary]-verification.md` → 失败则继续前向用户呈现问题（缺失追踪链接/孤儿工件/不一致）→ 审计 `PHASE_VERIFIED`。各边界检查内容：Ideation→Inception 查 intent 捕获/scope 定义/可行性确认/initiative 批准；Inception→Construction 查需求追踪到设计/units 定义/交付计划批准；Construction→Operation 查全 units 构建测试/CI 配置/基础设施设计。

### 19.4 stage-protocol-recovery.md（恢复与变更处理）

- **五数据源重建顺序**：① 产物树（"实际同意了什么"的持久记录）→ ② per-stage memory.md（决策过程观察）→ ③ 审计日志（**规范、append-only 的"发生了什么"真相源**；按 clone 分片 glob + 时间戳归并；有分歧时以它调和其余四个）→ ④ 状态文档 → ⑤ runtime-graph.json。类比"接别人做到一半的活"。**不能恢复上次会话的对话缓冲**。
- **回跳"已记未跳"检测**：`test-results.md` 有 Loop-Back Log 条目带计划修复、但审计无其后匹配的 `STAGE_JUMPED` → 会话死在记录与跳转之间，按 construction 模块**重执行跳转而非重新诊断**。
- **变更分级**：阶段中途新材料 = 当前阶段的**证据/输入，绝非路由指令**（留在当前 stage+unit，绝不跳设计直扑 Code Generation）；Minor（当前阶段内）直接改工件重呈现；Major（影响先前阶段）影响分析 → 批准后 jump 或 recompose；Scope changes 记审计 → 回 requirements-analysis 或 delivery-planning 重计划；**改前归档** `<record>/archive/[日期]-[stage]/`；Unit 增/删/拆各有程序（**绝不重跑已完成 unit**；架构变更保留未受影响 unit）。
- **损坏恢复**：状态文件损坏 → 备份 .bak → 扫产物定实际完成 → 按产物证据重建 → Current Status 设第一个缺产物证据的 stage；缺失产物先查 producer 是否在活动 scope 路径（**SKIP 从不产出——缺失是按设计，不是错误**）。
- **错误严重级别**：Critical/High 停+立刻问；Medium 先自解再问；Low 静默处理+审计。
- **压缩**：PreCompact 钩子校验状态结构（informational-only 不能阻止压缩）+ 写 `.aidlc-recovery.md` 面包屑，恢复时与 state 对比检测压缩损坏。

### 19.5 stage-protocol-reviewer.md（§12a 评审者协议）

- **两档**：**adversarial**（反驳-修复循环，至多 `reviewer_max_iterations` 轮，轮间 lead 修复；**反驳而非确认**——假设缺陷存在并猎取，READY 是尝试打破工件后未达成的结论；有机器可核验证据就落地，纯观点 finding 不足为 NOT-READY）与 **advisory**（单轮正常流评审作为人类门的决策支持；无论结论不重召 lead 不重跑 reviewer——记终态收据 → §13 → findings **逐字引用**在批准门给人类分诊）。Construction 默认 adversarial（finding 可机器核验），Ideation/Inception 散文阶段默认 advisory（就绪判断归门处人类）。
- **派发前必记请求**：`aidlc-log.ts review --stage --reviewer --iteration <n>`（per-unit 加 `--unit`、隔离加 `--single`）——请求先于派发，对 stale-source 恢复是强制的；请求绑定每个声明工件与既有终态附录之前的**精确字节**；成功请求返回 `reviewChallenge`，重试保留原 challenge。
- **既有 `## Review` 节处理**：再派发前先跑 `aidlc-review-brief.ts context`（保留完整 stdout 作为 Prior findings——持久人类处置 `Accepted risk`/`Rejected: <reason>` 不需编辑冻结工件而存活），然后**删除既有 `## Review` 节及随其引入的分隔字节**。
- **传什么/不传什么**：传 stage 定义路径、Q&A 文件、全部 produces 工件、Prior findings 原样（reviewer 保留 ID 更新状态，不重排不重编号）、consumes 解析路径（**仅路径**）、验证工具列表、source-manifest（**差分评审**，无关声明视为 finding）；**不传 memory.md 或任何 plan/推理文件**（独立判断）。
- **评审者读范围**：只当前 unit 工件 + 传入契约路径；**禁止**经任何工具读其他 unit 的 `construction/<other-unit>/`（含 grep/glob/shell 跨兄弟路径）；例外 = 当前 unit 设计显式点名的集成点、只该拥有文件、经共享契约解析。派发前写 `<record>/.aidlc-reviewer-dispatch.json`（`{reviewer, stage, unit, exempt}`）供 reviewer-scope 钩子强制。
- **失败/超时**：回到步骤 1 开头，删任何部分 `## Review` 附录，用 `--retry-pending` 重跑同请求（恰好接受一次，仅当请求 unmatched 且工件与源码精确匹配原请求；**有结论后绝不用**）。

### 19.6 stage-protocol-swarm.md（自治蜂群）

`invoke-swarm` 时加载。流程：`prepare`（`aidlc-swarm.ts prepare --batch/--units` 为每 unit 分叉隔离 git worktree）→ task 工具扇出并行 worker → `check <unit> --check-cmd`（跑项目 check 命令 + **反篡改比对**，绿=真收敛）→ `finalize --claimed`（权威门禁：重跑 check、要求 reviewer 收据、序列化 merge-back、发 `SWARM_*` 审计 + 失败信封）。`swarm_settled === true` 的重入只跑学习与单一批准门，不重跑阶段体。回跳交互：回跳建立新 stage-attempt `Run floor` 边界 token；先 check 所有 unit（已绿免 builder 回合但需 fresh reviewer 收据）；`prepare` 对陈旧 worktree/branch 冲突硬报错，`finalize` 拒绝无当前 prepare 戳的 unit。

## 20. 问题渲染机制（question-rendering.md）

stage-protocol 与各 stage 文件是 harness 中立的，只声明"呈现结构化问题"并携带 ` ```question ` 围栏规格块；本附录把契约绑定到 opencode 的具体机制（**无结构化问题控件，全部渲染为聊天中的编号散文选项**）。

- **绝不回显 spec（不可协商）**：围栏块是"渲染的输入，不是输出的粘贴物"——任何字段行（`prompt:`/`header:`/`options:`/`label:`/`description:`）禁止出现在对话中。回显即协议违规。
- **渲染形态**：
  ```
  **Approval** — [Stage Name] complete. How would you like to proceed?

  1. **Approve** — Continue to [next stage]
  2. **Request Changes** — Provide revision feedback
  3. **Other** — describe what you want instead

  Reply with a number (or just tell me).
  ```
- **细节规则**：header 加粗放前；推荐项排第一并加 "(Recommended)"；每个问题本地从 1 重新编号；**永远追加 Other 作为末项**；multiSelect 提示 "Reply with all numbers that apply (e.g. 1, 3)."；答案捕获把编号映射回确切 label **逐字**记录，自由文本明显匹配某选项算该选项，否则按 Other；批量化每条消息至多约 4 个问题；**禁止涌现式选项**（严格按 spec 的选项 + Other）。
- **Consolidated Summary 检查点**：渲染前先跑检查点专用 `aidlc-log.ts decision`（精确 `--questions-file` + `--unit`/`--single` 身份），END THE TURN 等人；回应映射回确切 label 写入 `[Answer]: Looks correct` / `[Answer]: Request changes` 并跑匹配的 `answer`——**必须剥掉源字母/编号/标点/描述**（`A. Looks correct`、`1. Looks correct` 都无效）。Request changes 时再问 "What should change?" 并再次 END THE TURN。

---

# 第六部分：多智能体系统

## 21. 14 个 Agent 详解

基础框架发货 14 个 agent（`.aidlc/agents/` 是 harness 中立的**权威人格集**，`.opencode/agents/` 是同批人格的 opencode 原生投影——正文逐字节一致，唯一差异是工具禁用写法：中立版 `disallowedTools: Task`，opencode 版 `mode: subagent` + `permission: { task: deny }`）。

| # | Agent | 角色 | 备注 |
|---|-------|------|------|
| 1 | product | 产品经理/业务分析师：需求、用户故事、市场调研、范围定义 | |
| 2 | design | UX/UI 设计师：线框、交互、可访问性、设计系统 | |
| 3 | delivery | 工程经理：团队组建、Bolt 排序、交付规划、阶段交接 | 锁定模型 |
| 4 | architect | 解决方案架构师：领域/契约/NFR 设计、组件分解 | |
| 5 | aws-platform | AWS 解决方案架构师：基础设施设计、环境开通、云原生 | |
| 6 | compliance | GRC 分析师：合规映射、数据分级、风险评估；纯支持角色 | |
| 7 | devsecops | 安全工程师：威胁建模（STRIDE）、安全需求、安全流水线 | |
| 8 | developer | 高级开发：代码生成、逆向工程扫描、数据建模、IaC | |
| 9 | quality | QA 负责人：测试策略、用例设计、质量门禁、性能验证 | |
| 10 | pipeline-deploy | CI/CD 工程师与发布经理：流水线、部署策略、发布执行 | 锁定模型 |
| 11 | operations | SRE/可靠性工程师：可观测性、事件响应、运维优化 | 锁定模型 |
| 12 | product-lead | 高级产品负责人：**只评审**需求/故事/UX 工件（完整性、商业对齐、可测性），代表客户声音 | 锁定模型 + steps:60 |
| 13 | architecture-reviewer | 高级架构评审人：**只评审**设计工件（健全性/可实现性/一致性） | 锁定模型 + steps:60 |
| 14 | composer | 自适应工作流编排者：ARS 熵值估算、EXECUTE/SKIP 网格组合（810 行，唯一"流程决策型"agent） | |

**Agent 正文统一骨架**（developer/product 结构同构）：
1. HTML 注释 + 强制**委派知识预检**：工作前按序加载 `.aidlc/knowledge/aidlc-shared/` → `.aidlc/knowledge/aidlc-<agent>/` → `aidlc/spaces/<space>/knowledge/aidlc-shared/` → 空间级 agent 知识；
2. `# <角色> Agent` persona 自述；
3. `## Core Responsibilities`（按阶段对齐）；
4. `## Collaboration` 三向矩阵（Receives from / Works with / Hands off to）+ 固定声明"跨 agent 委派只由 orchestrator 负责"；
5. `## Memory Focus`（指向五层规则）；
6. `## Key Principles` 编号原则。

**模型分层**：5 个 persona 固定 `amazon-bedrock/global.anthropic.claude-sonnet-4-6` + `variant: medium`（architecture-reviewer、delivery、operations、pipeline-deploy、product-lead），其余 9 个回退全局配置；`aidlc-tiers.ts` 提供 judgment/balanced/templated 三档投影（每个 agent 的 `tier_cap:` + `AIDLC_TIER_CAP` env → 各 harness 原生 model/effort 配置）。

**知识库**（`.aidlc/knowledge/`）：14 个 per-agent 目录共 40+ 篇方法学参考——architect（ADR 模板/架构指南/模式/DDD/NFR 设计与模式）、aws-platform（CDK 最佳实践/成本优化/基础设施指南/Well-Architected）、compliance（监管框架）、delivery（mob 编程/团队拓扑/工作流规划）、design（WCAG/组件规格模板/交互模式/UX/线框）、developer（API 设计/代码分析/代码生成指南与模式/数据建模/RE 产物）、devsecops（DevSecOps 流水线/NFR 需求/安全指南/STRIDE）、operations（事件响应/NFR 性能/可观测性模式/SLO-SLI）、pipeline-deploy（分支策略/CICD 模式/部署策略）、product（功能设计/市场调研方法/优先级框架/产品指南/需求引出/需求指南/用户故事模式）、quality（NFR 可靠性/NFR 验证方法/测试策略模式/测试指南）等。

**`aidlc-shared/` 九个共享文件**：`ai-dlc-principles.md`（方法论总纲："小 mob、广谱 agent"原则、7 条核心原则、五阶段表）、`audit-format.md`（**91 事件 22 类**权威注册表 + 三种条目格式 + validation-basis 收据）、`brownfield.md`（6 项棕地护栏矩阵：Blast Radius/Diff Preview/Test Baseline/Test Validation/Impact Analysis/Rollback Plan，锚定 2.1/3.5/3.6/4.3）、`knowledge-readme-template.md`、`memory-template.md`（四格日记模板，示例必须是单行 HTML 注释——全新模板解析为 total=0 触发 `MEMORY_EMPTY`）、`rules-reading.md`（五层规则读取协议：空模板检测/语义主题匹配/回退链落到第 4 层发 `PRACTICES_SECTION_EMPTY`）、`state-template.md`（state 字段契约，State Version 8，复选框六态）、`verification.md`（稳定 ID 体系 FR/NFR/US/AC/U/BR + traceability.json 形状与 OK/GAP/ORPHAN/Deferred/N/A 状态 + 6 步验证流程）、`worktree-info-schema.md`（worktree info 输出 schema 契约）。

## 22. 四种通信拓扑与委派纪律

- **拓扑分布**：29 inline / 2 subagent（practices-discovery、code-generation）/ 1 pipeline（reverse-engineering）/ 1 mob（user-stories）。`agent-team` 是保留 mode（未来原生总线传输），orchestrator 读取时必须显式拒绝。
- **委派纪律**：跨 agent 委派**只由 orchestrator 经 `task` 工具完成**；worker agent `permission.task: deny`——**无嵌套委派**，杜绝递归扇出。被委派的 lead/support/reviewer 都是**工件作用域**的：禁止调用 `next/report/park`、生命周期变更、路由、呈现门。
- **规则跨边界确定性**：`aidlc-deliver-stage-rules.ts` 钩子在每次 task 派发时把当前阶段规则包（带 sha256）缝入 prompt，保证规则跨 conductor→subagent 边界不漂移；规则包缺失或超 512KB 则阻断派发。
- **上下文预算**：subagent prompt 只传当前 unit 的设计工件；Construction subagent 对 inception 工件给 1-2 行摘要 + 路径；大知识集只点名路径让其自行读。
- **opencode 上的具体形态**：14 个 persona 以原生 subagent 注册（`.opencode/agents/`，`mode: subagent`），`task` 工具按名调用；`/aidlc` 会话在大多数阶段自己戴 persona 帽子（inline），仅 2.1 与 3.5 两个委派阶段经 `task` 工具出手。

---

# 第七部分：治理机制

## 23. 审批门仪式（完成消息五段式）

每个 gate 阶段到达门的完整序列（顺序不可换）：

1. **Reviewer 协议**（§12a，directive 声明 reviewer 时）；
2. **阶段完成验证**（产物存在、护栏遵守）；
3. **§13 学习仪式**（见 §26——**独立的人类回合**，其 `QUESTION_ANSWERED` 必须先于门的 `STAGE_AWAITING_APPROVAL`；门绝不在 learnings 问题同一消息里打开）；
4. **`report --result awaiting-approval`**（`[-]`→`[?]`，发 `STAGE_AWAITING_APPROVAL`；被阻塞性 gate 传感器拒绝时给 Fix findings / Override blocking sensors 两个独立选项，autonomous 下无 override）；
5. **呈现批准门 → 硬性 STOP**（不调任何工具直到人类明确选择）。

完成消息五段式：
- **Part 0**：先渲染 Part 1-2 → §13 学习仪式（独立回合）→ `report awaiting-approval` → Part 3；
- **Part 1 宣告**：`# [emoji] [Stage Name] Complete`（emoji 逐字取自 stage 文件）；
- **Part 2 摘要**：结构化要点 + 5-10 行行内摘要表（工件 vs 顶层内容）；会话首次完成消息须含 Project depth / Test strategy 说明；
- **Part 3 评审+批准**：有 reviewer 时先呈现 Review brief（`**Review:** <路径>`）再给批准问题；
- **Part 4 进度行**：approve 后显示——全 scope `Progress: [N]/33 overall | [phase-N]/[phase-total]`；缩减 scope `[X]/[S] in-scope stages complete ([N]/33 overall)`；总数从 `aidlc-utility.ts scope-table` 读，**禁止手工维护计数表**。

应答分支：Approve → `report --result approved --user-input "<精确选择>"`（自动发 `GATE_APPROVED` + `STAGE_COMPLETED` 并前进）；Request Changes → `report --result rejected --user-input "Request Changes" --reason "<feedback>"`（feedback 永不放 `--user-input`），`[?]`→`[R]` 修订后 `report --result revised`（`[R]`→`[?]` 重开门）；Accept as-is → 同 Approve。**批准是生命周期报告不是问题日志**：门不用 `aidlc-log.ts decision/answer`。

## 24. 传感器系统（6 个传感器详解）

传感器 = 自动质量检查，在匹配写入时（`fire_on: write`，本版本始终 advisory）或门处对已有交付物（`fire_on: gate`，可 blocking）触发。manifest 为 YAML frontmatter + 正文，字段：`id`、`kind: deterministic`、`command`、`default_severity`、`fire_on`、`description`、`category`、`matches`（glob）、`input_schema`/`output_schema`、`timeout_seconds`。stage 经 frontmatter `sensors: [<id>]` **拉入**（编译期解析进 `sensors_applicable`）。失败写详情到 `<record>/.aidlc-sensors/<stage-slug>/`。

| id | fire_on | category | timeout | 检查内容 |
|----|---------|----------|---------|---------|
| **claim-sources** | gate | document-provenance | 5s | Intent Capture 产物必须有 `## Assumptions & Open Questions`；每个实质段落/列表项/表格行带 `[desc]`/`[scope]`/`[Q<n>]`/`[memory:<id>]`/`[assumption]` 标签；标签解析到已确认来源（`[desc]` 精确匹配 project-description.json、`[Q<n>]` 解析到问题文件已填答案）；初始描述含 `<document>` 时禁用 `[desc]`；排除脚手架/围栏代码/HTML 注释/`## Review` |
| **required-sections** | gate | document-shape | 5s | 输出含所需 H2（默认 ≥2）；对 `unit-of-work-dependency.md` 额外校验 fenced `yaml` 的 `units:` 边块（ok/absent/malformed/cyclic，非 ok 即门失败）；标题集可被 `templates/<artifact>.md` 覆盖 |
| **upstream-coverage** | gate | document-shape | 5s | 交付物引用 frontmatter `consumes:` 声明的每个上游产物——独立 slug token（`requirements` 不算 `nfr-requirements` 内嵌）/ wikilink `[[slug]]` / 反引号文件名 / 生产阶段目录路径段；覆盖是"整个阶段输出"的属性；排除 `*-questions.md`/`*-timestamp.md`/`memory.md` |
| **traceability** | （write） | document-traceability | 5s | `traceability.json` 元素级验证：JSON 形状与闭合状态集；`GAP`/`ORPHAN`/缺行/未声明上游 ID 即失败；`OK`/`Deferred`/`N/A` 需非空 target；functional-design 的孤儿从 `rules.md` 推导而非只信自报 `reverse` 数组 |
| **linter** | （write） | code-quality | 30s | 包装项目配置的 linter（v0.5.0 默认 eslint，`bunx eslint --format json`；无配置→127→静默 PASS；多语言检测 ruff/golangci-lint/clippy 推迟 v0.6.0+） |
| **type-check** | （write） | code-quality | 60s | 包装 `bunx tsc --project --noEmit`（多语言 mypy/go vet/cargo-check 推迟 v0.6.0+） |

调度器 `aidlc-sensor.ts`（子命令 `list`/`describe`/`fire`）按锁定真值表裁决 PASSED/FAILED/BUDGET_OVERRIDE，输出单行 JSON 判定。阻塞性失败需显式审计的 override 才能开门（autonomous 模式无 override 路径）。框架发货的 6 个之外，fork 可加自定义 `aidlc-<id>.md` manifest（§13 学习仪式也能生成传感器提案）。

## 25. 评审者协议 §12a

见 §19.5。要点复述：**收据驱动**——`REVIEW_REQUESTED`/`REVIEW_COMPLETED` 收据绑定工件精确字节；`aidlc-review-freeze.ts` 钩子保证拿到新鲜 READY 收据后任何人再改产物都会被拒（收据作废保护）；`aidlc-reviewer-scope.ts` 钩子保证评审代理只能读自己 Unit 范围；`aidlc-review-brief.ts` 提供确定性评审上下文（`review --why first|revision|stale`、`context`、`summary --questions-file`），把人类 finding 处置折叠进 `GATE_APPROVED/REJECTED` 审计行（`Accepted risk`/`Rejected: <reason>` 处置持久存活，不需编辑冻结工件）。

## 26. 学习仪式 §13（自学习护栏）

**触发**：每个到达人类批准门的 stage，在完成消息与批准门之间；`gate: false` 迭代、隔离运行、bootstrap 初始化阶段绕过。**三方分工**：`aidlc-learnings.ts` 工具负责检测/浮出/路由/写入（tool-as-actor）；orchestrator-LLM 渲染结构化问题 + 做准入冲突检查；用户决定 keep/heading/scope。

**六步流程**：
1. 工作中维护 memory.md 四格日记；
2. `learnings surface --slug` 解析 memory.md 输出结构化 JSON：Interpretations/Deviations/Tradeoffs 逐字浮出为候选；**Open questions 是 parked 研究项，永不成候选**；输出还带此刻解析的 `space`/`intent`（必须逐字带入 selections 文件）；
3. 渲染结构化问题（每候选一选项，label 逐字=候选 summary）+ **强制** "Anything to add for next time?"（至少 Nothing to add / Add a note 两选项；**即使零候选也必问**，不能自选；**在该问题处结束回合**——门是之后的独立回合）；Add a note 打开自由文本，非空回答再让用户挑四日记标题之一（**唯一向用户要的分类**），由 orchestrator 按适配路由到 practice 标题（测试→Testing Posture、禁令→Forbidden、一般→Corrections 默认）；
4. **准入冲突检查**：拟议 practice 与 org.md 同 `##` 节对比；矛盾则 inline 浮出冲突句，用户**修订/跳过/升级**（无用户覆盖路径）；传感器 manifest 跳过此检查；
5. **persist**（`--selections-json`）：工具在一个 `withAuditLock` 事务里校验 slug/space/intent 存在，用 `<!-- cid:...sha256... -->` 标记去重（崩溃重放不重复追加）；Learning → 在路由标题下追加 `- <text> (learned YYYY-MM-DD) <!-- cid -->` 到 `memory/{project,team}.md`（默认 project，可一键升 team，**无 org 层**），发 `RULE_LEARNED`；Sensor → 搭 manifest scaffold + 把 id 追加进该 stage 的 `sensors:` frontmatter（双写安装，同一锁），发 `SENSOR_PROPOSED`。**orchestrator 永不直接 Edit 规则/传感器文件**；
6. 进批准门（仪式是建议性+附加性的，永不阻塞门）。

**stage 文件不可变，harness 可变**——学习只写入两面：规则文件或传感器 manifest。

## 27. Construction 专属机制：Unit/Bolt/Swarm/Worktree/回跳

（协议细节见 §19.1；此处是工具侧实现）

- **Unit**（`aidlc-unit.ts`）：原子 Unit 认领注册表与 checkout 本地 scope 绑定。子命令：`adopt`、`claim`（`--team/--rhythm`）、`release`、`participate`、`publish`、`pin`、`gate --decision approve|reject`、`land --step git|state|audit|all`、`merge-status`、`status`。
- **Bolt**（`aidlc-bolt.ts`）：构建期 Bolt 生命周期：`start --worktree`、`complete --merge`、`fail`、`abort --discard`、`set-autonomy --mode autonomous|gated`、`dispatch-event`、`hold-merge`、`release-merge`；发 BOLT_STARTED/COMPLETED/FAILED、AUTONOMY_MODE_SET 等审计，并联动 worktree 的 state/audit/runtime-graph 分段 fork/merge。
- **Worktree**（`aidlc-worktree.ts`）：`create`、`merge`、`discard`、`list`、`verify --event <WORKTREE_*>`、`info`；拒绝在非 main worktree 中调用。`info` 输出 schema 见 `worktree-info-schema.md`（`{slug, path, branch_name, audit_timestamp, merge_held}`，`.aidlc/worktree-meta.json` 存 `gitCommonDirHash` SHA-256 而非原始路径）。
- **Swarm**（`aidlc-swarm.ts`，仅人类授权的自治构建下触发）：3 个无状态子命令——`prepare --batch/--units`（每 unit fork 隔离 worktree）、`check <unit> --check-cmd`（项目 check 命令 + 反篡改比对）、`finalize --claimed`（权威门禁：重跑 check、要求 reviewer 收据、序列化 merge-back、SWARM_* 审计 + 失败信封）。**opencode 上 swarm 仅以 task 工具扇出实现**（`AIDLC_USE_SWARM=1` 是响亮 no-op）。
- **失败回跳**：见 §19.1；工具侧是 `aidlc-jump.ts`（`resolve` + `execute --target <slug> --direction forward|backward|redo`）——引擎验证后打印经验证的命令，conductor 逐字执行，发 `STAGE_JUMPED`。

---

# 第八部分：状态、审计与持久化

## 28. 工作区数据树（spaces / intents / record）

- **Space**（空间）：多团队隔离单位，单团队用户只见 `spaces/default/`。`/aidlc space <name>` 切换（`aidlc-includes.ts` 原位改写各 harness 的规则 include 指针）。
- **Intent**（意图）：一件工作的完整记录，目录 `spaces/<space>/intents/<YYMMDD>-<label>/`（`<record>/`）。`active-intent` 游标指向当前意图（per-user，不入 git）；`/aidlc intent <name>` 切换。intent 由 `aidlc-utility.ts intent-create --scope <scope> --arguments "<desc>" --label "<2-3词>"` 铸造（自由文本必须经 `--arguments` 传入，裸位置参数会静默丢失；label 成为可读的日期前缀目录名）。
- **record 目录内容**：`aidlc-state.md`（状态）、`audit/`（审计分片）、`<phase>/<stage>/`（产物 + memory.md 日记 + contributions/）、`runtime-graph.json`（不入 git）、`verification/`（边界验证报告）、`archive/`（改前归档）、`.aidlc-reviewer-dispatch.json`、`.aidlc-recovery.md` 等。

**应用代码写到工作区根**（或兄弟 repo），框架产物全在 `aidlc/` 中立的屋顶下。

## 29. 状态文件与审计系统

### 29.1 `aidlc-state.md`（state-template.md 契约，State Version 8）

字段区：Project Information（`Project` 字段只是 project-description.json 的安全单行预览）、Scope Configuration、Workspace State、Execution Plan Summary、Runtime State、三张进度表（Phase/Stage/Unit，复选框 `[ ]/[-]/[?]/[R]/[x]/[S]`）、Current Status（Lifecycle Phase、Construction Autonomy Mode、Walking Skeleton 立场等）、Session Resume Point。阶段集由编译图枚举。

**唯一权威写入者是 `aidlc-state.ts`**，且生命周期动词仅引擎可触发（`AIDLC_STATE_TRANSITION_OWNER` 守卫）。其子命令覆盖面：字段读写（`get`/`set`，支持 `NOW`/`+1`/`-1` 特殊值）、生命周期转移（`approve/reject/revise/skip/advance/finalize/complete-workflow/gate-start`）、`resume/acknowledge-compaction/reuse-artifact/lookup`、`practices-event/practices-promote`、Unit 系列（`set-skeleton-stance/set-construction-iteration/set-unit-ownership/set-unit-gate-rhythm/refresh-unit-progress/sync-unit-scope-stage/fold-unit-merge`、`unit start/pause/resume/complete`）、`checkbox/count`、`fork/merge`、`park/unpark`。

### 29.2 审计系统

- **事件词表**（`knowledge/aidlc-shared/audit-format.md`）：**91 个事件、22 个类别**的完整注册表（工作流/阶段/会话/初始化/导航/交互/Unit/产物/子代理/评审员强制/计划审批/DocumentKB/工具/错误恢复/Bolt/worktree/实践/merge 派发/传感器/学习循环/swarm…）；`SUBJECT_PAST_VERB` 命名；标准/错误/恢复三种条目格式；`STAGE_COMPLETED` 上的 schema-3 validation-basis 收据；ISO 8601 时间戳；append-only。
- **分片**：按 clone 分片 `audit/<host>-<clone>.md`（`.aidlc-clone-id` 令牌），glob + 时间戳归并；mkdir 锁（`withAuditLock`）保证原子性；**故意无 `.gitattributes merge=union`**——已被证明会损坏多行审计块。
- **写入纪律**：模型禁止从散文发审计事件；`aidlc-audit.ts append` 是窄诊断逃生舱，拒绝权威收据类事件（那些由专属工具在状态转移时原子发射）。`aidlc-audit.ts` 子命令：`append`/`append-batch`/`append-raw`/`audit-fork`/`audit-merge`。
- **交互审计**（`aidlc-log.ts`）：`decision`（提问前记 `DECISION_RECORDED`）、`answer`（`QUESTION_ANSWERED`）、`link`（`PIPELINE_LINK_COMPLETED`）、`review`（`REVIEW_REQUESTED/COMPLETED`）；`SUMMARY_CONFIRMATION_RECORDED` 收据带问题文件 digest。

### 29.3 runtime-graph

`aidlc-runtime.ts compile` 遍历审计 + memory 生成 per-workflow `runtime-graph.json`（时长、阶段结果、传感器触发、学习计数、token 成本），由 PostToolUse Bash 钩子在关键审计事件（GATE_APPROVED/STAGE_STARTED/STAGE_AWAITING_APPROVAL/AUDIT_MERGED/UNIT_MERGED/WORKFLOW_COMPLETED）后触发（带递归防护与 IDE 幂等 mtime 防护）。`summary --json` 供三个会话技能取数；`read <stage-slug>` 读单阶段视图。纯观察者，不改 state。

## 30. 五层规则系统

`aidlc/spaces/<space>/memory/` 下：`org.md`（框架默认 + 组织护栏）→ `team.md`（团队确认的实践）→ `project.md`（项目专门化）→ `phases/<phase>.md`（ideation/inception/construction/operation 四相护栏；initialization 无规则文件）→ stage 级。

- **严格叠加（strict-additive）**：每层只能增加约束，全部适用规则出现在运行时 `rules_in_context`（编译期烘焙进 stage-graph 每条记录）；冲突（窄层推翻宽层策略）在 §13 学习准入检查处拒绝落盘。
- **送达机制**：`load-steering` directive 以**内容**形式送达（`rules_content` 数组按序应用），不是路径提示；子代理派发时经钩子把累计规则包原样缝入 prompt。
- **读取协议**（`rules-reading.md`）：空模板检测（段落每个非空行都以 `<!--` 开头即空）；语义主题匹配（按主题而非精确标题）；回退链（project→team→org→硬编码默认，落到第 4 层时发 `PRACTICES_SECTION_EMPTY`）。

## 31. 知识资产：CodeKB / Team Knowledge / DocumentKB

- **CodeKB**：`spaces/<space>/codekb/<repo>/`——brownfield 逆向工程的 space 级共享存储，跨 intent 累积（9 个工件 + 聚焦合并/全量替换/复用三模式；compare-and-swap 发布带 rollback；`codekb-scope-diff` 新鲜度判定）。由 `aidlc-utility.ts codekb-path/snapshot/publish/scope-diff` 管理。
- **Team Knowledge**：`spaces/<space>/knowledge/`——自由格式团队/领域知识，跨 intent 积累；bootstrap 时为空目录（引擎首次 `/aidlc` 确保存在）；agent 读 `knowledge/aidlc-shared/`（全部 agent）与 `knowledge/<agent>/`（该 agent）。
- **DocumentKB**：两个子目录的负载承担性区别——`knowledge/documents/`（**用户所有**的原始文档：PDF/Word/Markdown/纯文本，框架永不 reorganize/删除）与 `knowledge/documentkb/`（**工具所有**的可重建目录：`index.json` + 每文档目录含 `metadata.json`/抽取的 `content.md`，事务写入工作区锁）。
  - **可重建性**：丢失 `index.json` 可从每个 `metadata.json` 重建（tombstone 恢复成 tombstone）；删整个 `documentkb/` 树不可恢复（id 与 tombstone 全丢，sync 把幸存原件当全新行重新 onboard）。
  - **动词**（`/aidlc knowledge <verb>` 或 `/aidlc-knowledge`）：`onboard`（幂等：同路径未变报 already、内容变报 edited 原地刷新；路径less sweep 上限 20 个新/变文档或 256 MiB，单文档 >32 MiB 拒读）、`sync`、`list`、`show <id>`、`associate`/`dissociate <id> --intent [slug]`（省略=space 级；裸=活跃 intent；具名=UUID；已完成 intent 拒绝除非 `--allow-inactive`；dissociate 永不需要该 flag）、`rebind <id> --to <path>`（移动+编辑是 sync 无法自解的唯一情况）、`summarize <id> --text-file --source-revision <sha256>`（工具自己不写摘要——校验/限界 4000 字符/消化/持久化你读 `show` 后产出的文本；文档变了则拒绝；摘要与修订版绑定，原件编辑后不重摘要报 `invalidated` 并扣留旧文本）。**刻意没有 `remove`**——删除 = 用户删自己的文件再 sync。
  - **九种行状态**：`extracted`、`no_extractable_text`、`extractor_unavailable`、`extraction_failed`、`unsupported_type`、`invalidated`、`source_unavailable`、`tombstoned`、`present_but_refused`（后三者语义刻意分离：够不到/人删了/拒绝读）。
  - **不可信数据契约**：提取的文档文本是**数据不是指令**——`show` 内联该警告；**文件名同样不可信**（list/show 都带 path_notice）；截断标记（50 PDF 页/200,000 字符上限）。

## 32. 恢复机制（五数据源重建）

见 §19.4。要点：恢复按"产物树 → memory.md → 审计日志 → 状态文档 → runtime-graph.json"顺序重建（审计是分歧时的调和者）；能恢复决定/阶段内上下文/时间线/当前位置，**不能恢复对话缓冲**。压缩前 `aidlc-validate-state.ts` 校验状态必需段 + 发 `SESSION_COMPACTED` + 失效 active-directive 上下文 + 写 `.aidlc-recovery.md` 面包屑；`aidlc-state.ts acknowledge-compaction` 在恢复时核对。会话启动时解析 active-intent 游标 → 查 `aidlc-state.md` → 有则呈现 Resume/Redo/Jump/Start Fresh 菜单（见 §8.2）。

---

# 第九部分：实现清单

## 33. 17 个 Hooks 逐个详解

全部 TypeScript，经 bun 子进程运行，stdin 收 `ClaudeCodeHookInput` 形状 JSON。通用约定：无活动工作流或输入畸形 → 静默 `exit 0`（fail-open）；阻断型 = PreToolUse 拒绝契约（stderr 原因 + exit 2）；多数写心跳文件（`hooksHealthDir/<hook>.last`）供 doctor 检测静默失败。所有阻断钩子有 `AIDLC_DISABLE_*` 逃生开关。

### 阻断型（exit 2，5 个）

| 钩子 | 事件 | 强制的不变量 |
|---|---|---|
| `aidlc-state-transition-guard.ts` | PreToolUse(Bash) | 生命周期转移只能走 `aidlc-orchestrate report`——拒绝手调 `aidlc-state.ts` 动词（set/checkbox/advance/approve/reject…）与派生子代理运行被委托的生命周期/路由命令；含复杂 shell 解析（引用/heredoc/函数/包装器/命令替换）。无文件副作用 |
| `aidlc-plan-approval-guard.ts` | PreToolUse | code-generation"先批准计划后生成"：计划证据（plan、测试指令、Testing Contract 指纹、"Approve Plan"答案）非当前时，拒绝 developer-agent 派发与 record 目录外的写/Bash 变更。审计 `PLAN_APPROVAL_BLOCKED`；批准时写保护收据 |
| `aidlc-review-freeze.ts` | PreToolUse | §12a 收据排序：目标文件匹配某 reviewer 阶段的 produces/optional_produces 且存在新鲜终审收据时，拒绝写入（Write/Edit/Bash/apply_patch，**不分身份**）。审计 `REVIEW_FREEZE_BLOCKED` |
| `aidlc-reviewer-scope.ts` | PreToolUse | 评审代理按 Unit 读范围：不得跨兄弟 unit 的 construction/ 路径读/搜（含 glob、grep、Bash 扫描），豁免列表外即拒绝。审计 `REVIEWER_SCOPE_BLOCKED`；清理过期 dispatch 记录；缺失记录告警（限频 10 分钟） |
| `aidlc-deliver-stage-rules.ts` | PreToolUse(task) | 子代理派发时把当前阶段规则包（带 sha256）确定性缝入 prompt；规则包缺失/超 512KB 阻断（或 preload 回退 exit 3）；返回 `updatedInput` 改写；记录后台子代理 in-flight ledger |

### 流改变型（特殊，1 个）

**`aidlc-continue-workflow.ts`**（Stop / session.idle）：回合结束时跑 `aidlc-orchestrate next`；仍有 PENDING 则以 `{"decision":"block","reason"}` 塞回待办（on-task 续接，非 override 指令）。**8 类豁免**：人工等待门（`[?]`/`[R]`）、待答问题文件、DECISION_RECORDED、compose 标记、后台子代理、会话式闲聊（`.aidlc-human-turn`/`.aidlc-engine-touch` mtime 比较）、resume 选择、Esc。无进展计数器 + run-mode 上限（autonomous=8 / interactive=2）防卡死；写 `block-count.json` 进度签名。Claude 上 blocking（stdout block 契约）；**opencode 上经 session.idle 注入 nudge，建议型**。

### 纯观测/建议型（恒 exit 0，11 个）

| 钩子 | 事件 | 作用 |
|---|---|---|
| `aidlc-session-start.ts` | SessionStart | 发 `SESSION_STARTED`/`SESSION_RESUMED`（compact 不发）；持久化 transcript/session 身份；resume 重绑定（INTENT REBIND OFFER）；注入工作流上下文 additionalContext（**opencode 无此通道**，但钩子仍为其副作用运行）；引导 cursors/includes |
| `aidlc-record-human-turn.ts` | UserPromptSubmit | 每次真实人类提示写 `HUMAN_TURN` 审计（human-presence 门禁事实；`AIDLC_UNATTENDED=1` 时跳过带授权事件但保留标记）；触碰 `.aidlc-human-turn` 标记；提取受保护的 Plan Approval 答复 |
| `aidlc-write-audit-log.ts` | PostToolUse(Write/Edit) | 落在活跃 intent record 或 space codekb 树内的写入发 `ARTIFACT_CREATED`/`ARTIFACT_UPDATED`（按 mtime≈birthtime 区分新建/覆写）；含审计分片递归防护 |
| `aidlc-run-sensors.ts` | PostToolUse(Write/Edit) | 读编译好的 `sensors_applicable`，对匹配 glob 的条目派发 `aidlc-sensor.ts fire` 子进程；结果经审计行（SENSOR_FIRED/PASSED/FAILED/BUDGET_OVERRIDE）与详情文件呈现；`.first-fired` 横幅标记 |
| `aidlc-rebuild-stage-graph.ts` | PostToolUse(Bash) | 命令/审计尾匹配到转换类事件（GATE_APPROVED / STAGE_STARTED / STAGE_AWAITING_APPROVAL / AUDIT_MERGED / UNIT_MERGED / WORKFLOW_COMPLETED）时派发 `aidlc-runtime.ts compile` 重建 runtime-graph；递归防护 + IDE 幂等 mtime 防护；绑定新建 intent 到调用会话 |
| `aidlc-sync-workflow-state.ts` | PostToolUse | 按 payload（TaskUpdate activeForm `[slug]` 或 Kiro IDE `ide-audit-sync`）把当前 stage 同步进状态文件（经 `aidlc-utility.ts set-status`）；IDE 路径为只进不回的镜像（有 Running 状态与 completed/skipped 防护） |
| `aidlc-log-subagent.ts` | SubagentStop | 子代理完成发 `SUBAGENT_COMPLETED` 审计；移除该会话的 in-flight ledger 条目 |
| `aidlc-validate-state.ts` | PreCompact | 压缩前验证状态文件必需段落；发 `SESSION_COMPACTED`；失效 active-directive 上下文；写 `.aidlc-recovery.md` 恢复面包屑 |
| `aidlc-session-end.ts` | SessionEnd | 发 `SESSION_ENDED`（纯可观测，不结束工作流）。**opencode 无此时刻，不装配** |
| `aidlc-statusline.ts` | StatusLine | 终端状态区显示工作流位置（phase、进度条、当前 stage、agent、空间/意图前缀）+ 模型缩写、上下文占用百分比（红/黄/绿）、成本段。**opencode 无状态栏，不装配** |
| `aidlc-fold-usage.ts` | PreToolUse+PostToolUse | 把 transcript 新增折叠进持久用量账本（offset 感知、每文件游标+holdback 模型，幂等）；引擎边界 flush-all。**仅 Claude 装配**（opencode 无生产者） |

**共享库**：`review-freeze-command.ts`——纯函数模块（无独立主流程），导出 `writeTargets`/`shellWriteTargets`/`shellCommandInvocations` 等，解析 Write/Edit 与各类 Bash 变异命令（cp/mv/rm/sed/perl/find/dd/重定向等）的写目标，被 review-freeze 与 plan-approval-guard 复用。

## 34. 50+ 个 Tools 分组详解

设计原则：**"必须精确而非判断"的部分全部落成小型命令行程序**，全部 `aidlc-*.ts` 前缀、经 bun 运行。

### 34.1 编排核心

- **`aidlc-orchestrate.ts`**：编排引擎，**恰好 5 个子命令**——`next`（读状态+编译图，输出恰好一个 directive JSON，自身零变异）、`continue`（内部 steering 传输通道）、`report`（conductor 执行完 directive 后提交状态转移；`--single` 隔离；`--stage` 固定动作）、`park`（干净边界暂停）、`team-board`（只读团队构建查询）。引擎不提问、不派生 agent、每个输出经 `validateDirective` 校验。
- **`aidlc-directive.ts`**：引擎↔conductor 冻结接口契约——11 种 directive kind 判别联合 + `validateDirective` 运行时校验器；纯契约无 I/O。
- **`aidlc.ts`**：CLI 总入口/路由分发器（`ROUTES` 表把顶层动词映射到工具文件、`SLASH_FLAG_ALIASES` 斜杠别名如 `--status`→status；分类 passthrough/translation/stub/routing-only/help）。

### 34.2 状态与账本

- **`aidlc-state.ts`**：state 唯一权威读写器（子命令清单见 §29.1）；引擎专属转移有 `AIDLC_STATE_TRANSITION_OWNER` 守卫。
- **`aidlc-audit.ts`**：审计日志（规范事件集；`append`/`append-batch`/`append-raw`/`audit-fork`/`audit-merge`；mkdir 锁跨平台）。
- **`aidlc-log.ts`**：交互审计（`decision`/`answer`/`link`/`review`）。
- **`aidlc-runtime.ts`**：runtime-graph 编译/读取（`compile`/`read <slug>`/`summary --json`）；纯观察者。

### 34.3 图与评分

- **`aidlc-graph.ts`**：阶段 DAG 库 + CLI——`artifacts`/`producers`/`consumers`/`topo`/`cycles`/`scope`/`validate-scope`/`validate-grid --proposal`/`ars --iae/--csu/--ve/--r/--ua`（确定性算术）/`compile`（YAML→JSON，`--check` CI 漂移守卫）/`resolve`/`export`。
- **`aidlc-validate.ts`**：阶段文件 Outputs 声明与正文引用一致性校验（`outputs <phase|all>`）。

### 34.4 工作流操作

`aidlc-jump.ts`（阶段跳转 resolve/execute）、`aidlc-unit.ts`（Unit 认领注册表）、`aidlc-bolt.ts`（Bolt 生命周期）、`aidlc-swarm.ts`（蜂群裁判）、`aidlc-worktree.ts`（worktree 原语）、`aidlc-testing-posture.ts`（测试姿态契约 + 计划/指令指纹；库模块带 main）——详见 §27。

### 34.5 学习与知识

- **`aidlc-learnings.ts`**：§13 学习门（`surface --slug` 只读 / `persist --selections-json` 确定性写入，内容哈希去重）。
- **`aidlc-knowledge.ts`**：DocumentKB 8 动词（见 §31）；事务写入 + 严格符号链接/包含守卫。
- **`aidlc-review-brief.ts`**：评审/摘要确定性决策上下文（`review --why first|revision|stale`、`context`、`summary --questions-file`）。

### 34.6 平台库（被导入为主）

- **`aidlc-lib.ts`**（2.3 万行，最大共享库）：参数解析、状态文件读写、audit 帮助、workspace 动词、checkbox 解析、路径解析。
- **`aidlc-utility.ts`**（独立 main 的管理 CLI）：`status`、`doctor`、`intent-create/init`、`intent`、`space/space-create`、`codekb-path/snapshot/publish/scope-diff`、`project-description`、`document-input`、`detect`、`select-plugins/plugin-list/plugin-sync/plugin-validate/plugin-build`、`recompose`、`scope-change`、`config-change/get/list`、`set-status`、`detect-scope`、`resolve-env-scope`、`scope-table`、`stage-table`、`upgrade`。
- **`aidlc-steering.ts`**（规则包解析）、`aidlc-metrics.ts`（opt-in StatsD，仅 `AIDLC_METRICS_ENDPOINT` 设置时生效）、`aidlc-usage.ts`（token 用量/成本：费率表 + transcript 读取器 + 纯成本计算 + per-file 游标账本）、`aidlc-tiers.ts`（三档模型分层投影）、`aidlc-validity.ts`（阶段有效性收据指纹：`STAGE_COMPLETED` 行写不可变 Validation Basis，结合当前产物树投影有效性）、`aidlc-runtime-paths.ts`（编译可执行 vs 源码运行时路径解析）、`aidlc-artifact-resolution.ts`（产物名→物理路径、per-unit 归属）、`aidlc-artifact-vocabulary.ts`（产物线名→文件名例外映射）。

### 34.7 Schema 纯函数校验器（零依赖）

`aidlc-stage-schema.ts`（阶段 frontmatter）、`aidlc-rule-schema.ts`（规则 frontmatter：`pairing/status/stale_after`）、`aidlc-sensor-schema.ts`（传感器 manifest）、`aidlc-documentkb-schema.ts`（index/metadata，schema_version 固定、六态 extraction 联合）。

### 34.8 传感器实现

`aidlc-sensor.ts`（调度器：`list`/`describe`/`fire`，锁定真值表裁决 PASSED/FAILED/BUDGET_OVERRIDE，单行 JSON 判定）+ `aidlc-sensor-claim-sources/linter/required-sections/traceability/type-check/upstream-coverage` 六个实现（检查内容见 §24）。

### 34.9 插件工具链

`aidlc-plugin-create.ts`（离线脚手架 `<name> [targetDir] [--json]`）、`aidlc-plugin-validate.ts`（清单/内容/symlink/贡献路径校验）、`aidlc-plugin-emit.ts`（共享投影引擎：插件 manifest → 各 harness 目标格式；也是适配器白名单的注入者）、`aidlc-plugin-build.ts`（`<plugin-root> <harness> [outDir]`）、`aidlc-plugin-test.ts`（compose 级安装测试）。

### 34.10 工作区与打包

`aidlc-workspace-manifest.ts`（`repos.json` 多仓 schema）、`aidlc-workspace-sync.ts`（按清单调和多仓工作区：克隆缺失 repo、维护 .gitignore 管理块、生成 VSCode multi-root 文件；事务化 + `--force` 孤儿清理前置安全校验）、`aidlc-workspace-doctor.ts`（doctor 的 workspace 健康行：W1 未提交记录 / W2 manifest-磁盘漂移 / W3 过期 gitignore 块，全 advisory）、`aidlc-doctor-bundle.ts`（`--doctor --export` 脱敏诊断包：report.md/json + manifest.json + evidence/，先脱敏再写，拒符号链接）、`aidlc-includes.ts`（各 harness 规则 include 指针原位改写器：Claude/Kiro/Codex/opencode/Cursor）、`aidlc-runner-gen.ts`（runner 技能生成器：`write`/`check` 漂移守卫/`list`/`scopes`）、`aidlc-version.ts`（`AIDLC_VERSION = "2.7.1"` 单一真源）。

## 35. 41 个 Skills 分组详解

`.aidlc/skills/` 下 41 个技能目录 + 1 个附属文档，分 6 组：

### 35.1 核心编排器：`aidlc/`

- `SKILL.md`（268 行）：conductor 提示词本体——转发循环、directive 动作表、门分支、语音契约、新工作路由、composer 流程、scope/stage 表格（编译生成、禁止手编）。最后 5 行 Key Principles 收尾：PRE-GENERATION SUMMARY STOP 完整命令契约（`aidlc-log.ts decision --checkpoint summary-confirmation --questions-file <path> --decision "..." --options "Looks correct,Request changes"` → 渲染 → END THE TURN → `answer --details "<exact choice>"`；文件中 `[Answer]: Looks correct` 精确且回执成功才能生成产物；Request changes 再问 "What should change?"）、Tri-mode 交互、工具拥有的审计线索、自学习护栏、禁止嵌套委派。
- `question-rendering.md`：问题渲染附录（见 §20）。

### 35.2 会话级只读技能（3 个，`classification: read-only`）

全部数字强制来自 `bun .aidlc/tools/aidlc-runtime.ts summary --json`（**禁止 LLM 侧计数**）；不推进阶段、不发审计事件；非零退出（尚无 runtime-graph）时打印引导语并 STOP。

- **`aidlc-session-cost`**：透明成本视图——时长、阶段结果、记忆条目、传感器触发、learnings 的固定格式报告；`duration_minutes` 为 null 显示 `in progress`；**刻意不打印 token 估算**（"文件大小换算 token"的启发式是披着数据外衣的猜测，已退役）。
- **`aidlc-replay`**：把审计线索与产物变成可读故事（面向未在场利益相关者）。固定骨架：`# Session Replay` → 元数据 → Executive Summary → Timeline（按 phase 展开，每 stage 三段：What happened / Key decisions / Artefacts produced）→ Decisions Register Summary 表 → Learnings Captured → What's Next。散文可综合，一切数字来自工具。
- **`aidlc-outcomes-pack`**：三者中唯一写文件的——在工作区根写 `OUTCOMES.md` 交接文档（8 个固定章节：What Was Built / Repository Structure / Setup Guide / Build and Deploy / Architecture Decisions / What to Commit vs Archive / Workflow Footprint / Known Limitations and What to Tackle Next）。

### 35.3 文档知识技能：`aidlc-knowledge`（唯一 read-write 独立技能）

包装 `aidlc-knowledge.ts` 的 8 动词（`argument-hint: "[onboard <path> | list | show <id> | sync]"`）；在工作流图之外——改文档目录、发文档审计事件，但**从不推进阶段、从不批准门**。机制细节见 §31。

### 35.4 特殊入口：`aidlc-init` 与 `aidlc-compose`

- **`aidlc-init`**：Initialization 是**阶段（phase）而非单个 stage**——一次性确定性铸造 intent + 检测工作区 + 构建 state。命令：`bun .aidlc/tools/aidlc-utility.ts intent-create --scope <scope> --arguments "<description>" --label "<2-3词 essence>"`。两个易错细节：自由文本必须经 `--arguments`（裸位置参数静默丢失）；`--label` 派生 2-3 词 kebab-case 成为日期前缀目录名。守卫：既无 scope 也无描述时先问用户；打印工具输出即停止，**不推进任何 stage**。
- **`aidlc-compose`**：`/aidlc compose` 的可输入快捷方式——"同一扇门，强制走完整 composer 即使 stock scope 会匹配"。命令仅 `bun .aidlc/tools/aidlc-orchestrate.ts next compose $ARGUMENTS`；之后完全并入主循环。

### 35.5 Scope 固定转发器（5 个）

`aidlc-bugfix`（"Fix a specific bug"，Minimal）、`aidlc-express`（"Lightest run: requirements to deploy, no design pass, no reviewers"，Minimal）、`aidlc-feature`（"Full lifecycle for new features"，Standard）、`aidlc-mvp`（"Skip operations, ship the core"，Standard）、`aidlc-security-patch`（"CVE response"，Minimal）。

与主 `/aidlc` 循环的**唯一机制差异**：首条命令烘焙 `--scope <name>`（`next --scope <name> $ARGUMENTS`），跳过 scope 自动检测；循环体/报告/门/学习仪式完全一致。各带独立的"Starting unrelated new work?"章节（默认建议 scope 取烘焙值；CONFIRM 后 STOP 交接新会话）。

### 35.6 单阶段运行器（30 个）

由 `bun .aidlc/tools/aidlc-runner-gen.ts write` 从编译 stage graph **自动生成**（frontmatter 带 `generated-by: aidlc-runner-gen`），`check` 子命令做漂移守卫——新增 stage 文件并重新生成即新增其 runner。三个引导初始化 stage 无 runner（无独立意义）。

统一三步骨架：① `next --stage <slug> --single` → ② 读 stage-protocol.md + `directive.protocol_modules` 点名的模块 → 按 directive 跑阶段 → ③ `report --single --stage <slug> --result completed`。`--single` 语义见 §9.2——**绝不写主工作流的 Current Stage**，工具按设计拒绝推进主工作流；是"opt-in 包装"：同一阶段不装技能也能用 `/aidlc --stage <slug> --single` 触达。

## 36. data/ 静态数据文件逐个详解

`.aidlc/tools/data/` 下：

| 文件 | 内容 |
|---|---|
| `stage-graph.json` | **结构真理**：33 阶段对象数组。每条含 slug/number/name/phase/execution/condition/lead_agent/support_agents/mode/produces/conuses/requires_stage/sensors/scopes/inputs/outputs + 编译期烘焙的 `rules_in_context`（五层规则链 `{path, scope}`）与 `sensors_applicable`（`{id, path, fire_on, default_severity, category, matches}`）+ 可选 reviewer 系列/summary_confirmation/for_each/produces_kinds/optional_produces/workspace_requires |
| `scope-grid.json` | 11 个 scope × 33 阶段的 `EXECUTE/SKIP` 网格（分布见 §15.2）；与 stage-graph 同为 `aidlc-graph.ts compile` 产物，compose 后重新生成 |
| `ars-priors.json` | ARS 确定性算术数据源（schemaVersion 1）：五分量权重（iae .2/csu .3/ve .25/r .15/ua .1）、分量带（low .3/med .7）、合成 5 档（Near-direct/Focused/Standard/Comprehensive/Full ceremony）、EV 阈值（cost1-5 → 0/.2/.3/.4/.5）、33 阶段的 targets/cost/role/projectTypes 先验（含两个 `cost: null` 阶段）。**未校准先验，仅咨询性** |
| `model-rates.json` | 框架默认模型费率表（USD/百万 token，Anthropic 公开价，截至 2026-07）：8 个模型按"代数离散"键控（opus-5、opus-4-8/4-7/4-6、sonnet-5、sonnet-4-6、haiku-4-5、fable-5），各含 input/output/cacheWrite5m(1.25x)/cacheWrite1h(2x)/cacheRead(0.1x)；未知模型记账 token 但成本记 null（绝不错价）；可被 `AIDLC_MODEL_RATES` env 覆盖 |
| `plugin-targets.json` | 7 个 harness 的安装目标表（`harnessName/manifestDir/harnessLeaf/kind/installRoots`）：claude(`.claude-plugin`/`.claude`，含 `.mcp.json`)、codex(`.codex-plugin`)、copilot(`.plugin`/`.aidlc`)、cursor(`.cursor-plugin`，含 `install.ts`)、kiro/kiro-ide(`.kiro-plugin`)、opencode(`.opencode-plugin`/`.aidlc`，installRoots = `.aidlc`+`.gitignore`+`.opencode`+`AGENTS.md`+`aidlc`+`opencode.json`) |
| `plugin-authoring-context.json` | 插件作者上下文：14 个合法 agent 名 + 33 个合法 stage slug 的权威清单 |
| `harness.json` | 本安装标识：`{"name":"opencode","harnessDir":".aidlc","rulesSubdir":"rules"}` |
| `memory-seed/` | 五层规则种子模板（见 §37） |
| `templates/` | 空目录（仅 `.gitkeep`，占位） |
| `plugin-hooks-template/` | 插件 compose 钩子模板：`compose.ts`（约 1257 行主脚本——SessionStart compose 钩子 + 可导入组合器：no-clobber 拷贝插件贡献、合并进 stage 源文件、重编译 graph；幂等、无变化短路；含 drops 文件/安装树审计/frontmatter 冲突预检/`agent-team` 保留 mode 拒绝/各 harness 原生 agent 投影校验）+ `aidlc-plugin-compose.ts`（92 行跨平台启动器，避免 `sh -c`，兼容原生 Windows） |

## 37. 方法规则种子（memory-seed 默认内容）

`data/memory-seed/` 与 `aidlc/spaces/default/memory/` **逐字节一致**（当前是未启动的全新工作区）。

### org.md（组织层默认，119 行）

- **Way of Working**：trunk-based 开发；短命分支合 `main`；Construction worktree 的 base/target 都是 `main`；多环境用 tag/部署配置门控而非长命发布分支；Bolt 分支 **squash-merge** 进 main（一个 Bolt 一个 commit，按 Bolt slug 命名）。
- **Walking Skeleton**：仅当 scope 文件声明 `skeleton: on` 才先跑骨架 Bolt（Bolt 1 单独、门控、用户显式批准）；Bolt 1 之后编排器发起 ladder prompt，选择持久化为 `Construction Autonomy Mode`。
- **Testing Posture**：测试是一等交付物；默认方法论 `test-after`；scope 附加底线（mvp/enterprise/feature/infra/classic +80% 行覆盖 + CI 执行；bugfix/security-patch +定向回归；express 用 Minimal；poc/refactor/workshop 无新增底线但现有套件保持绿色）；底线是**叠加的**，不削弱所选测试策略。
- **Deployment**：merge 即部署 staging；生产部署需独立人工审批（tech lead + product owner）。
- **Code Style**：委托项目级配置（Prettier/Black/gofmt、ESLint/Ruff/golangci-lint）。
- **Mandated — Conversation language 四条**：① resolution（制品语言由编排器从人类实质语句解析，每次委派 brief 必写 `Conversation language: <语言>` 行；解析顺序 brief 行 → project.md → project-description.json；**project.md 永远压过 team.md**）；② stability（会话内语言不因无信号回合改变；持久化只能走 §13 学习仪式，禁止直接编辑 memory 文件）；③ what to localize（需求/故事/计划/评审/问题/实践/证据/决策理由全本地化）；④ preserved tokens（反引号字面量 `[Answer]:`、`X. Other (please specify)`、`AGREE:`/`OBJECT:`、`**Collaborator:**`、`[desc]`/`[Q<n>]`、`## Sources`、`READY`/`NOT-READY`、YAML 键、稳定 ID 逐字保留英文）。
- **Forbidden / Corrections**：空模板，由学习循环填充。

### team.md / project.md

`team.md`（46 行）全是 HTML 注释占位（Way of Working/Walking Skeleton/Testing Posture/Deployment/Code Style/Forbidden/Mandated/Corrections），由 practices-discovery 的确认门填充——"在门禁处编辑，不直接改"。`project.md`（64 行）多三个区：**Tech Stack**（锁定技术选型）、**Decided**（`DECIDED: [decision] (Stage [slug], [date])`）、**Scope Overrides**；Forbidden 格式 `NEVER [行为] (affirmed [date])`、Mandated `ALWAYS ...`、Corrections `NEVER/ALWAYS [行为] (learned [date])`；文件头强调"大多数团队不需要 project 层，慎用"。

### phases/*.md（四相护栏）

- **ideation.md**：Focus（先问题后方案、无实现细节、先广后窄）；Evidence Standards（市场主张需引用、可行性保守、猜测标注 hypothesis）；Scope Discipline（不携带未批准的范围决定）；Output Quality（非技术干系人可读、指标可度量）。
- **inception.md**：Requirements Quality（可测、有 pass/fail 判据、无歧义词）；Architecture Standards（ADR 须含 Context/Decision/Consequences/Alternatives Rejected）；User Stories（BDD Given/When/Then、独立可测）；Traceability（每条需求回溯 ideation 制品）。
- **construction.md**：Code Completeness（完整可运行文件、无占位 stub）；Error Handling（集成边界必有错误处理、禁止静默失败）；Testing Standards（happy path + 至少 2 个错误/边界用例、测试不得恒真）；Security（禁止硬编码密钥、边界输入校验）。
- **operation.md**：Infrastructure Safety（IAM/网络/加密变更需风险评估）；Deployment Procedures（必含回滚步骤、生产 smoke test）；Observability（SLO 必须量化百分比+时间窗、告警阈值低于 SLO 违约线）；Incident Response（runbook 含升级路径、P1/P2 必须复盘）。

---

# 第十部分：安全、差异与扩展

## 38. 安全与权限模型（四层防御）

对"AI 能执行什么"有**四层叠加**的防御：

1. **opencode.json 权限层**：bash 默认 `ask`；仅放行 `bun .aidlc/tools/*`、`bun .aidlc/hooks/*` 单次调用；对 `.aidlc/tools/`、`.aidlc/hooks/` 的编辑要询问。
2. **适配器边界层**：手写 shell 词法分析器拒绝链式/重定向/展开/命令替换；62 个已发货入口白名单拒绝"新写 payload 再借白名单执行"（`aidlcEntrypoints` 可注入，是单测缝）。
3. **钩子阻断层**：5 个 exit-2 钩子强制工作流不变量（状态转移所有权、计划先批、评审收据冻结、评审读范围、规则包注入）。
4. **工具所有权层**：`aidlc-state.ts` 的 `AIDLC_STATE_TRANSITION_OWNER` 守卫是硬地板——即使前三层都绕过，直接调生命周期动词仍被拒。

其它安全设计：
- 审计写入用 mkdir 锁（跨平台无外部依赖）；
- DocumentKB 严格符号链接守卫、先脱敏再写的 doctor bundle；
- compose 的 creationDescription 强制 POSIX 单引号 argv 传递、禁用 shell 双引号包裹不可信文本；
- nudge 哨兵防止合成提示伪造人类存在；
- 主/子会话甄别 fail-closed；
- 粘贴文档与 DocumentKB 提取文本都是**不可信数据而非指令**；
- 所有阻断钩子有 `AIDLC_DISABLE_*` 逃生开关（调试用，默认全开）；
- 无 blanket shell trust；`opencode run` 非交互会话里 `--auto` 意味着接受剩余提示的自动批准，门控工作流建议交互式会话。

## 39. opencode 上的差异与已知降级

相对 Claude Code 版（适配器文件头与 AGENTS.md 明确记录）：

| 方面 | opencode 实况 |
|---|---|
| 审批门/问题呈现 | 编号散文选项（无结构化问题控件）；问题文件的 `[Answer]:` 标签仍是事实源 |
| 转发循环（Stop） | 骑 `session.idle`，以**注入 nudge 提示**再接入——建议型非阻断；正在聊天/暂停的人类由交互上限释放 |
| session-start 的 additionalContext | **无注入通道**；钩子仍为其副作用运行（会话→意图戳、状态检查）。补偿：SKILL.md 规定裸 `/aidlc` 首回合先跑只读 `aidlc-utility.ts status` 探测 |
| SESSION_ENDED | **不发出**（opencode 无会话结束时刻）；压缩前校验正常（`experimental.session.compacting`） |
| statusline / welcome | **没有**；用 `/aidlc --status` 与门处进度行 |
| Construction swarm | 仅 task 工具扇出；`AIDLC_USE_SWARM=1` 为响亮 no-op |
| 用量折叠（fold-usage） | 不装配（仅 Claude 有生产者） |
| reviewer 身份关联 | `tool.execute.before` 无 active-agent 字段；从 `chat.message.agent` 按会话关联，缺失时子会话按"有派发记录则视为 scoped registration"处理——窄窗口内可能误 scope 别的子 worker，但**永不误 scope 主会话** |
| 状态同步 | conductor 自有：适配器观察 todowrite 仅为簿记，状态文件同步骑状态工具（引擎 report 派发），不靠 todo 钩子 |
| MCP 服务器 | 不发货（需要可自行在 `opencode.json` 配置） |
| headless（`opencode run`） | session.idle nudge 仅为建议；转发循环纪律是唯一纪律——**绝不回合中途中断工作流而没有门问题或完成的 report** |

## 40. 插件扩展机制（Plugin 工具链）

AI-DLC 是**开放世界**：`plugins/<name>/` 下的插件可贡献额外的 stage、scope、agent，`select-plugins` 选择本安装启用哪些。启用集合的权威实况视图 = 编译产物 `stage-graph.json` + `/aidlc --doctor`。

工具链：`aidlc-plugin-create.ts`（脚手架）→ `aidlc-plugin-validate.ts`（校验）→ `aidlc-plugin-emit.ts`（投影引擎，把 manifest 渲染到各 harness 目标格式——本目录的 `.opencode/agents/` 投影与适配器白名单注入就是这种机制的体现）→ `aidlc-plugin-build.ts`（按 harness 构建）→ `aidlc-plugin-test.ts`（compose 级安装测试）。分发侧由 `plugin-hooks-template/compose.ts` 在 SessionStart 做增量合成（no-clobber 拷贝 + 贡献合并 + 重编译 graph，幂等短路）。

## 41. Git 集成与 .gitignore 详解

**原则**：per-user 会话游标与机器本地运行态/派生态**忽略**；共享工作（方法、注册表、状态、审计分片、产物）**一律提交**。

提交清单（注释块明确"勿加忽略规则"）：`aidlc/spaces/*/memory/**`、`codekb/**`、`intents/intents.json`、`intents/*/aidlc-state.md`、`intents/*/audit/*.md`（按 clone 分片；**故意无 `.gitattributes merge=union`**——已证明会损坏多行审计块）、`intents/*/<phase>/<stage>/*.md`。

忽略清单及理由：

| 条目 | 理由 |
|---|---|
| `aidlc/active-space`、`aidlc/spaces/*/intents/active-intent` | per-user 游标（两人可同时指向不同 space/intent） |
| `aidlc/.aidlc-clone-id` | 本克隆审计分片令牌——共享会导致每个克隆同分片、git 冲突 |
| `aidlc/.aidlc-unit-scope.json`、`.aidlc-unit-parked`、`.aidlc-claim-generations.json`、`.aidlc-unit-participant`、`.aidlc-claim-registry.json`、`.aidlc-unit-releases/`、`.aidlc-unit-merges/` | 团队 Unit 并行构建的本地运行态/声明/暂存 |
| `aidlc/.aidlc-active-space-*.tmp` | active-space 原子创建暂存 |
| `aidlc/.aidlc-sessions/` | 会话→intent 映射（按 session_id 键控的用户本地运行态） |
| `aidlc/spaces/*/intents/.aidlc-*`、`aidlc/spaces/*/intents/*/.aidlc-*` | 恢复/钩子健康/传感器暂存 |
| `**/aidlc/spaces/*/intents/**/.aidlc-sensors/` | 任意深度的引擎传感器缓存 |
| `aidlc/spaces/*/knowledge/documentkb/.journal/` | DocumentKB 事务暂存（崩溃残留安全移除，下次 sync 收集） |
| `aidlc/spaces/*/knowledge/.sources.local.json` | DocumentKB `linked` 源别名→**机器特定绝对路径**映射，提交会泄露开发者目录布局 |
| `aidlc/spaces/*/intents/*/runtime-graph.json` | 派生图（也覆盖 per-Bolt worktree 片段） |
| `aidlc/diagnostics/` | `--doctor --export` 脱敏诊断包（重新生成、共享后即删） |

另有通用段：日志、node_modules/dist、编辑器文件（保留 `.vscode/extensions.json`）。

---

# 附录 A：使用方式速查

| 命令 | 作用 |
|---|---|
| `/aidlc <描述>` | 开始/继续工作流；scope 自动检测 |
| `/aidlc --status` | 查看进度（opencode 无 statusline，这是位置查询入口） |
| `/aidlc --doctor` | 体检（钩子心跳、图漂移、workspace 健康；`--export` 脱敏诊断包） |
| `/aidlc --version` | 框架版本 |
| `/aidlc --stage <slug>` / `--phase <name>` | 跳转（跳过中间阶段，不跳过目标阶段仪式） |
| `/aidlc --depth` / `--test-strategy` / `--review <level>` | 覆盖深度 / 测试量 / 评审上限（adversarial/advisory/none） |
| `/aidlc compose "<task>"` | 自适应定制流程网格（`--report <path>` 从扫描报告、`--new-scope`）；每个提案停在 approve/edit/reject 门 |
| `/aidlc --resume` | 恢复暂停/上一会话的工作流 |
| `/aidlc intent [name]` / `space [name]` | 列出/切换意图 / 空间 |
| `/aidlc knowledge <verb>` | DocumentKB 文档目录（onboard/sync/list/show/associate/dissociate/rebind/summarize） |
| `/aidlc-init` | 一次性跑完初始化阶段（建首个工作流记录） |
| `/aidlc-<stage>` | 隔离运行单个 stage（不推进主工作流，30 个可用） |
| `/aidlc-bugfix` `/aidlc-express` `/aidlc-feature` `/aidlc-mvp` `/aidlc-security-patch` | scope 烘焙的快捷入口 |
| `/aidlc-session-cost` / `/aidlc-replay` / `/aidlc-outcomes-pack` | 会话成本 / 审计回放 / 成果交接文档（OUTCOMES.md） |
| `bun .aidlc/tools/aidlc-orchestrate.ts park` | 在干净边界暂停工作流 |

# 附录 B：一句话理解这个插件

> 它把 opencode 从"一个会写代码的聊天助手"改造成"一个有记忆、有流程、有门禁、有审计的软件生产线"：**模型负责在每个工位上把活干好，TypeScript 引擎负责决定工位顺序、记录每个决定、并在没有人类点头时拒绝让任何东西流向下一个工位**——而 opencode 适配层全部的技术含量，就在于用单个 774 行的进程内插件，把 opencode 的钩子时刻无损翻译给那套与 Claude Code 字节共享的核心引擎。
