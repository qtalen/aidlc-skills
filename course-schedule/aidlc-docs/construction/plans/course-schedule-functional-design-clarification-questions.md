# Functional Design Clarification Questions — course-schedule

我在你的回答中检测到 1 处需要澄清的歧义：

## Ambiguity 1: 冲突处理策略不完整
你在 Q5 选择了 Other 并回答"要考虑单双周的情况"——这明确了**冲突判定**要考虑周次范围和单双周（只有周次区间实际相交的同时间段课程才算冲突），但没有说明判定为冲突后**是否允许保存**。

### Clarification Question 1
当检测到课程时间冲突（已考虑周次范围与单双周，仅在周次区间实际相交时判定冲突）时，系统应如何处理？

A) 弹出警告说明冲突详情，但允许用户确认后保存（适应调课等现实情况）

B) 弹出错误提示并禁止保存，必须修改到不冲突为止

C) Other (please describe after [Answer]: tag below)

[Answer]: A
