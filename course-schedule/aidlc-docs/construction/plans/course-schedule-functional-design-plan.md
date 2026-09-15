# Functional Design Plan — course-schedule

单元：course-schedule（隐式单一单元） | 深度：minimal | 输入：inception/requirements/requirements.md

## 设计任务清单

- [x] 定义领域实体（课程、学期设置、节次时间表、提醒设置）
- [x] 定义业务规则（周次计算、单双周判定、冲突检测、校验规则）
- [x] 定义业务逻辑模型（课表渲染逻辑、提醒触发逻辑、导入导出逻辑）
- [x] 定义前端组件结构（视图层级、组件 props/state、交互流、表单校验）
- [x] 澄清问题全部作答且无歧义（Q1-Q5 + CQ1 冲突后允许保存）

## 澄清问题

## Question 1
节次时间表的默认策略？（中国高校常见一天 12 节：上午 4-5 节、下午 4-5 节、晚上 2-3 节，每节 45 分钟）

A) 提供 12 节默认模板（含常见作息时间），允许用户修改每节开始/结束时间和节数

B) 不提供默认模板，由用户从零自定义

C) 固定 12 节不可修改

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2
课程颜色如何分配？

A) 系统自动从调色板分配，用户可修改

B) 完全由用户手动选择

C) 系统自动分配，不可修改

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3
上课提醒的提前量如何配置？

A) 全局统一设置（默认课前 15 分钟，可改）

B) 每门课程单独配置

C) 固定 15 分钟不可改

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4
一周从哪天开始？

A) 周一（中国高校惯例）

B) 周日

C) 用户可配置

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5
同一时间段添加重叠课程时的处理策略？

A) 检测冲突并警告，但允许保存（现实中存在调课/冲突课的情况）

B) 检测冲突并禁止保存

C) 不做冲突检测

D) Other (please describe after [Answer]: tag below)

[Answer]: D — 要考虑单双周的情况
