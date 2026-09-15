# Domain Entities — course-schedule

## Entity: Course（课程）
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | string (uuid) | 是 | 创建时生成 |
| name | string | 是 | 课程名，1-50 字符 |
| teacher | string | 否 | 教师姓名 |
| location | string | 否 | 上课地点 |
| dayOfWeek | number (1-7) | 是 | 星期几，1=周一 … 7=周日 |
| startSection | number | 是 | 开始节次（1 起） |
| endSection | number | 是 | 结束节次（≥ startSection） |
| weekStart | number | 是 | 起始周（1 起） |
| weekEnd | number | 是 | 结束周（≥ weekStart，≤ totalWeeks） |
| weekType | enum: all / odd / even | 是 | 每周 / 单周 / 双周 |
| color | string (hex) | 是 | 颜色标记，创建时自动分配 |
| createdAt | string (ISO) | 是 | 创建时间 |

## Entity: SectionTime（节次时间）
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| index | number | 是 | 节次序号（1 起） |
| startTime | string (HH:mm) | 是 | 本节开始时间 |
| endTime | string (HH:mm) | 是 | 本节结束时间（> startTime） |

默认模板：12 节，常见高校作息（08:00 起，每节 45 分钟 + 课间 10 分钟，午间/晚间休息）。用户可增删节、修改时间。

## Entity: SemesterSettings（学期设置）
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| semesterStartDate | string (YYYY-MM-DD) | 是 | 第一周的日期；自动对齐到该周周一 |
| totalWeeks | number | 是 | 学期总周数，默认 20 |

## Entity: AppSettings（应用设置）
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reminderMinutes | number | 是 | 课前提醒提前量（分钟），默认 15，全局统一 |
| notificationEnabled | boolean | 是 | 是否启用浏览器通知（需用户授权） |
| sectionTimes | SectionTime[] | 是 | 节次时间表（默认 12 节模板） |

## 关系
- SemesterSettings 1 ─── n Course（一门课程归属一个学期设置下的周次体系）
- AppSettings.sectionTimes 1 ─── n SectionTime
- Course.startSection/endSection 引用 SectionTime.index（用于渲染与提醒触发计算）

## 持久化
全部实体存于 localStorage 单一键 `course-schedule-data`，结构：
```json
{ "version": 1, "courses": [], "semester": {}, "settings": {} }
```
