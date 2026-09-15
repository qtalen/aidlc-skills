# 需求澄清问题（Requirement Verification Questions）

请回答以下问题以帮助澄清课程表 web 小程序的需求。每个问题选择最符合的选项字母；如都不符合，选 Other 并在 [Answer]: 后描述。

## Question 1
你说的"web 小程序"指哪种平台形态？

A) 微信小程序（在微信内运行）

B) 手机浏览器 H5 网页应用

C) 普通响应式网页应用（桌面 + 手机浏览器均可）

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2
核心功能范围包括哪些？（可多选，用逗号分隔字母，如 A,B）

A) 查看课表（周视图/日视图）

B) 手动添加/编辑/删除课程

C) 上课提醒（课前通知）

D) 考试安排 / 作业 DDL 管理

E) Other (please describe after [Answer]: tag below)

[Answer]: A,B,C

## Question 3
课程数据从哪里来？

A) 完全由用户手动录入

B) 从学校教务系统导入（需要对接或爬取）

C) 从 Excel/文件导入

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4
是否需要用户账号体系？

A) 无需登录，数据存本地（单机使用）

B) 需要账号登录，支持多端同步

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5
后端架构倾向？

A) 纯前端应用（数据用浏览器 localStorage 存储，零后端）

B) 前端 + 后端 API + 数据库

C) 由你根据需求推荐

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 6
技术栈偏好？

A) 无偏好，由你推荐

B) Vue

C) React

D) 微信小程序原生框架

E) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 7
目标使用范围？

A) 个人使用（自己用）

B) 小范围分享（同班/同宿舍同学）

C) 面向全校学生

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 8
Security Extensions：是否为本项目强制执行安全基线规则（SECURITY）？

A) 是 —— 将所有 SECURITY 规则作为阻塞性约束（推荐用于生产级应用）

B) 否 —— 跳过所有 SECURITY 规则（适合 PoC、原型和实验性项目）

C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 9
Resiliency Extensions：是否为本项目应用韧性基线（源自 AWS Well-Architected 可靠性支柱的设计期最佳实践，覆盖容错、高可用、可观测性、可恢复性等 15 个实践域；注意：这只是一份有依据的韧性姿态初稿，不代表生产就绪认证）？

A) 是 —— 应用韧性基线作为设计期指导（推荐用于业务关键型负载）

B) 否 —— 跳过韧性基线（适合快速迭代优先的 PoC/原型项目）

C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 10
Property-Based Testing Extension：是否为本项目强制执行基于属性的测试（PBT）规则？

A) 是 —— 将所有 PBT 规则作为阻塞性约束（推荐用于含业务逻辑、数据转换、序列化或有状态组件的项目）

B) 部分 —— 仅对纯函数和序列化往返强制 PBT 规则（适合算法复杂度有限的项目）

C) 否 —— 跳过所有 PBT 规则（适合简单 CRUD、纯 UI 项目）

D) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 11
Context Checkpointing Extension：是否启用上下文检查点（CTX）规则？启用后，每个阶段/单元结束时写出简短检查点文件（关键决策、核心约束、制品清单、待办项），新会话只重载检查点而非全部历史文档，使项目变大后仍保持高效。

A) 是 —— 在阶段/单元边界写检查点，会话恢复时只重载检查点（推荐用于长周期、多会话、多单元项目）

B) 否 —— 不写检查点，新会话按需重载所有历史文档（适合单会话可完成的小项目）

C) Other (please describe after [Answer]: tag below)

[Answer]: B
