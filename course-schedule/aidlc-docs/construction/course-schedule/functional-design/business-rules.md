# Business Rules — course-schedule

## 周次与日历
- **BR-1 周起始日**：一周固定从周一开始（中国高校惯例），不提供配置项。
- **BR-2 学期起始对齐**：用户选择学期开始日期后，系统自动对齐到该日期所在周的周一作为 `semesterStartDate` 存储。
- **BR-3 当前周计算**：`currentWeek = floor((today - semesterStartDate) / 7 days) + 1`。结果 < 1 表示学期未开始；> totalWeeks 表示学期已结束（UI 给出相应提示）。

## 课程显示
- **BR-4 周次显示判定**：课程在第 w 周显示 ⟺ `weekStart ≤ w ≤ weekEnd` 且满足 weekType：
  - `all`：始终显示
  - `odd`：w 为奇数时显示
  - `even`：w 为偶数时显示

## 数据校验（添加/编辑课程表单）
- **BR-5 必填与范围**：
  - name 必填，1-50 字符
  - dayOfWeek ∈ [1,7]
  - 1 ≤ startSection ≤ endSection ≤ 当前节次时间表的节数
  - 1 ≤ weekStart ≤ weekEnd ≤ totalWeeks
  - teacher、location 可选
- **BR-6 校验失败处理**：表单内联提示错误字段，阻止提交。

## 冲突检测
- **BR-7 冲突判定**：两门课程冲突 ⟺ 三条件同时成立：
  1. dayOfWeek 相同
  2. 节次区间相交：`startSection ≤ other.endSection 且 other.startSection ≤ endSection`
  3. 周次区间实际相交（考虑单双周）：weekStart/weekEnd 区间相交，且 weekType 组合后存在共同周次（all 与 all/odd/even 均可能相交；odd 与 even 永不相交）
- **BR-8 冲突处理**（CQ1=A）：检测到冲突时弹出警告，列出冲突课程与重叠周次，**允许用户确认后保存**。

## 颜色分配
- **BR-9**：新增课程时自动从内置调色板（≥10 色）中选取当前使用次数最少的颜色；用户可在表单中修改。

## 上课提醒
- **BR-10 触发条件**：页面打开期间，每分钟检查当天课程；当 `当前时间 ≥ 课程开始时间（由 startSection 查 sectionTimes） − reminderMinutes` 且本节课今日未提醒过，则触发提醒。
- **BR-11 提醒方式**：优先浏览器 Notification API；用户未授权或 API 不可用时降级为页面内横幅提示。
- **BR-12 生效边界**：仅在页面打开时生效（纯前端架构固有限制），设置页明确说明。
- **BR-13 reminderMinutes**：全局统一配置，默认 15 分钟，可在设置页修改。

## 导入导出
- **BR-14 导出**：将 `{ version, courses, semester, settings }` 序列化为 JSON 文件下载。
- **BR-15 导入**：解析并校验 JSON——version 兼容、BR-5 全部字段规则、SectionTime 时间格式合法；任一校验失败则拒绝导入并提示具体原因；校验通过则全量替换现有数据（导入前提示用户确认）。

## 节次时间表维护
- **BR-16**：sectionTimes 至少保留 1 节；删除节次时若存在引用该节次的课程，警告并阻止删除；修改时间要求 endTime > startTime。
