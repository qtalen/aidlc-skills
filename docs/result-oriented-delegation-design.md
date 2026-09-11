# 结果导向委派设计：去 Persona / 去 Role / 去自有子智能体

**日期**：2026-09-10
**状态**：讨论记录（供后续新会话继续讨论）
**不包含**：夜跑模式、可选钩子插件（这两条线的上下文本次刻意排除，后续单独讨论）。

---

## 1. 背景与动机

讨论起点：对 v2.0 的"14 个 agent / persona"设置不满意。核心论点——**用 prompt 给模型戴 persona（"你是资深架构师"）的做法，对客观正确性任务已被证明效果弱且不稳定**；AIDLC 的价值是流程正确性，persona 恰好用在最不产生收益的地方。因此结论：

> **去 persona、去 role、去 AIDLC 自带的子智能体。**

但要区分：v2.0 的 agent 抽象**捆绑了**几件真正有用的机制（知识检索范围、模型分层、权限隔离、上下文隔离、完成证据、独立评审）和一件基本没用的东西（人格自述）。删除时必须保留有用机制，用**行为/任务类型**而非身份表达。

---

## 2. 确立的核心原则

> **AIDLC 只关心结果，不关心过程。AIDLC 发出 review 任务，harness 自己想办法去做。**

推论：
- AIDLC **不**规定用什么 agent、什么模型、是否并行、如何做到只读。
- AIDLC **不**发货任何 persona、任何子智能体定义、任何命名 agent。
- AIDLC **只**声明"要什么结果、什么时候要、怎么验收"。

---

## 3. 三方分工（原则的准确落点）

| 角色 | 决定 |
|---|---|
| **AIDLC 引擎（确定性）** | **WHAT + WHEN**：任务类型、输入清单、期望结果 schema、验收判据、失败后的策略 |
| **Harness（自由）** | **HOW**：子代理还是内联、挑哪个 agent、用什么模型、是否并行、怎么做到只读 |
| **AIDLC 脚本（确定性）** | **验收结果**：结果文件是否存在、schema 是否合法、哈希绑定是否完好、verdict 是什么；据此路由 |

关键点：**"独立评审"是一个任务类型，不是一个角色。** AIDLC 里不再有 `reviewer` 这个 agent，只有 `task: review`。

---

## 4. AIDLC 发出的最小任务信封（Task Envelope）

AIDLC 的 directive / 阶段文件只发这样一个信封：

```yaml
task: review
inputs: [{ path, sha256 }]        # 要评审什么，绑定字节
expected:
  artifact: <结果落盘路径>          # 结果必须是工作区里的文件
  schema: verdict{ verdict: READY|NOT-READY, findings[] }
integrity:
  bound_to: <inputs 哈希 + nonce>  # 防陈旧/防掉包
```

- **没有** agent 名、**没有**人设、**没有**"用什么工具"。
- 模型在某个 harness 里读到这个信封，就用手边最合适的方式去做。
- 明确**收回**早期提出的"role / requirements / 解析优先级阶梯"设计——那是 harness 侧的事，不属于 AIDLC。

---

## 5. 唯一不能外包的：结果验收 + 失败策略

**AIDLC 的脚本必须自己、只读地去验证结果文件**（存在 / schema / 哈希 / verdict），绝不接受"模型口头说做完了"。否则"harness 自己想办法"会退化成"harness 自己给自己打分"。

- 结果不合格时 AIDLC 按**结果**决策：重试、降级、halt-and-ask——不关心 harness 内部为什么失败。
- 落地机制：**把委托当成"待验收的产物"，而不是"一次调用"**。每个委托任务必须有持久化、schema 化的结果工件。

---

## 6. 必须正视的边界：独立性是过程属性

**问题**：独立性（fresh eyes）是**过程属性**，却表现为**结果质量**。结果文件本身无法证明它是独立上下文跑出来的——同一个上下文自评也会产出格式合法的 verdict。

处理路线：
- **(a) Best-effort + 溯源声明（推荐为默认）**：要求结果里带 provenance 字段（"独立上下文 / 内联自评 / 未知"），AIDLC 记录并据此调整门的措辞。对所有 harness 通用。
- **(b) 能力依赖（可选增强）**：只在 harness 能提供独立/只读保证时要求，否则把该次评审标记为低置信，并在门处显式提示人类。

倾向：**(a) 为默认、(b) 为可选增强**——默认不因 harness 能力不同而改变流程形状，只改变"置信标注"。

---

## 7. 兼容性证据（各 harness 子代理能力，已核实）

| Harness | 子代理机制 | 命名选择 | 对 AIDLC 的含义 |
|---|---|---|---|
| **opencode** | `task`(v1) / `subagent`(v2) + `subagent_type`；内建 `general`/`explore`/`scout`；`.opencode/agent(s)/` | ✅ 可按名 | 内建只读 `explore` 天然适合 review |
| **Claude Code** | `Task` + `subagent_type`；内建 `general-purpose`/`Explore`/`Plan` | ✅ 可按名 | 同上 |
| **Trae** | `.trae/agents/*.md`；内建 "Agent" **按 description 自动路由**；内建只读 "Search" | ⚠️ 主推**自动路由** | 正好就是"由 harness 自己判断" |
| **Codex** | `spawn_agent`/`multi_agent`；内建 `default`/`worker`/`explorer` | ❌ **工具会话中常不暴露 `agent_type`**（0.137.0 起有回归，子代理变通用且继承父模型） | **绝不能依赖命名选择**，只能通用 spawn + prompt 带角色 |
| **pi** | 未核实 | ? | 按最坏情况设计（通用/无子代理 → 回退到内联隔离评审） |

关键结论：存在"命名选择不可用"的现实（Codex），所以正确抽象**不是**"挑一个 agent 名"，而是"发一个任务信封 + 通用回退"。

补充佐证：Trae 官方博客明确写 *"Subagents are specialized workers, but Skills are portable... If multiple subagents need the same expertise, don't duplicate—create a Skill."* ——与"技能承载流程、子代理只做执行"的方向一致。

---

## 8. 由本原则衍生的架构结论（待并入正式整合计划）

1. `aidlc-workflows` 保持**独立可移植技能包**；核心与 harness 解耦。
2. **去 persona、去 role**：角色只作为任务类型（review / author / research / synthesize）存在。
3. **AIDLC 不发货任何子智能体**；委派采用"能力声明式 / 结果导向"的任务信封。
4. **验证在输出侧**：不管最终是谁执行的，AIDLC 校验产物（字节哈希绑定、schema、非空 findings）。即使某 harness 挑了个可写代理，冻结收据仍能**检测**出篡改——把保证从"选对人"换成"验对结果"，使跨 harness 兼容真正可行。
5. 失败策略（重试/降级/halt-and-ask）按**结果**定义，不按过程。

---

## 9. 下次会话待决问题

1. **独立性处理**：确认采用 (a) best-effort + provenance 溯源声明为默认，(b) 能力依赖为可选增强？
2. **结果工件的 schema 规范**：`verdict` 之外，review / author / research / synthesize 各自的结果 schema 如何定义？finding 的严重度分级与关闭状态如何表达？
3. **失败策略细节**：结果缺失/不合法/schema 不符时，分别重试几次、何时降级、何时 halt-and-ask？
4. **冻结与防篡改**：无硬强制手段时，哈希绑定收据由哪一步写、哪一步校验、如何避免"自己写收据自己校验"的闭环失效？
5. **知识检索替代 persona**：原 persona 携带的知识目录，改为按 `task`/阶段声明需要加载的知识引用（`knowledge_refs`），具体清单如何组织？
6. **模型分层的归宿**：v2.0 的 `aidlc-tiers.ts` 模型分层若要保留，应作为"任务信封的可选建议字段"由 harness 采纳，还是也完全交给 harness 自决？
