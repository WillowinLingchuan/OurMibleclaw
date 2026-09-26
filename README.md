# OurMobileClaw · 第五届「移动云杯」参赛方案

> 第五届「移动云杯」智算应用创新大赛 · **模型应用赛**（面向外部开发者）
> 基于移动云 **MoMA**（Mobile Model Marketplace）平台构建 ｜ 团队 4 人

---

## 项目简介

本仓库是参赛项目的**方案库**。目前有**三个候选方向并列评估中，尚未冻结**：

| 方向 | 一句话 | 状态 |
|---|---|---|
| **短剧投流素材智能体 BoostForge** | 从一集成片批量产出投流素材，**并随投放回流越做越准** | ✅ 已确定方向（⏳ 待验证） |
| **学业综测规划智能体 PathPilot** | 把培养方案 + 综测细则变成每个学生的**跨学期最优路径** | ⏳ 候选 · 评估中 |
| **交通事故辅助研判智能体 RoadMind** | 把散落的案卷材料，排成交警判责时要翻的那份清单，**并随办结文书回流越排越准** | ⏳ 候选 · 评估中 |

### 贯穿三个方向的决策标准

> ### 硬核部分必须是「可选的」，不能是「承重的」。
> 项目最难的那部分如果失败，作品**仍然成立、仍然可交付**。

> ### 完成度高的中等作品，永远赢过完成度低的高远作品。

### ⚠️ 当前最大的问题

**三个方向，验证清单完成度为零。**
真正的分歧只有一个：**「高校服务 / 交通治理」能否挂靠「智能协同办公」赛道？**

> 详见 [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) **附录 A「三方向可行性评估」** —— 含可行性评分、「死法」分析与一周决策路径。

---

## 文档

> **目录结构：每个候选方向一个独立目录**，各自存放该方向的方案 / 架构 / 演示脚本。
> ⚠️ 现有**三个候选方向并列评估中**，除 BoostForge 外均**未冻结**。

| 方向 | 目录 | 状态 |
|---|---|---|
| **短剧投流素材智能体 BoostForge** | [`docs/boostforge/`](docs/boostforge/) | ✅ 已确定方向（⏳ 待验证） |
| **学业综测规划智能体 PathPilot** | [`docs/pathpilot/`](docs/pathpilot/) | ⏳ 候选 · 评估中 |
| **交通事故辅助研判智能体 RoadMind** | [`docs/roadmind/`](docs/roadmind/) | ⏳ 候选 · 评估中 |
| **方向决策记录** | [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) | 评估矩阵 · 选型理由 · **验证清单** · **附录 A：三方向可行性评估** |

### 各方向目录内容

| 目录 | 文件 |
|---|---|
| [`docs/boostforge/`](docs/boostforge/) | `EXECUTION-PLAN.md` — 短剧投流素材工厂 |
| [`docs/pathpilot/`](docs/pathpilot/) | `EXECUTION-PLAN.md` — 高校学业-综测路径规划 |
| [`docs/roadmind/`](docs/roadmind/) | `EXECUTION-PLAN.md`（方案 · 做什么）· [`TEAM-ROLES.md`](docs/roadmind/TEAM-ROLES.md)（**分工与排期 · 谁做**）· [`ARCHITECTURE.md`](docs/roadmind/ARCHITECTURE.md)（智能体角色架构）· [`JUDGMENT-DATA.md`](docs/roadmind/JUDGMENT-DATA.md)（**公开裁判文书接入 · 闭环落地**）· [`DEMO-SCRIPT.md`](docs/roadmind/DEMO-SCRIPT.md)（演示脚本） |

### 建议阅读顺序

1. 先看 [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) 第二节「决策标准」和第六节「验证清单」——理解**决策标准是什么**，以及**当前卡在哪**
2. 再看 [`docs/boostforge/EXECUTION-PLAN.md`](docs/boostforge/EXECUTION-PLAN.md) 第一、二、四节——理解**已确定方向是什么**，以及**为什么它是智能体而不是工作流**
3. 若在考虑换方向：看 [`docs/roadmind/EXECUTION-PLAN.md`](docs/roadmind/EXECUTION-PLAN.md) **第十三节「三方向对比矩阵」** —— 三个方向的逐项对比与建议

---

## ★ 下一步：两封邮件定方向

| # | 动作 | 决定什么 |
|---|---|---|
| **1** | 问组委会：**高校服务 / 交通治理能否挂靠「智能协同办公」赛道** | **PathPilot 与 RoadMind 的生死** |
| **2** | 问组委会：**Token 配额是否覆盖视频模型** | BoostForge 是否要砍模块 |

**各一天。** 完整决策路径见 [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) 附录 A「A.6」。

### 三个方向各自的致命问题（都还没验证）

| 方向 | 致命问题 | 若失败的后果 |
|---|---|---|
| **BoostForge** | 拿不到投放数据 ／ Token 配额不覆盖视频模型 | ❌ 不致命（砍模块，作品仍成立） |
| **PathPilot** | 赛道挂靠被拒 | **★ 一票否决（跑题）** |
| **RoadMind** | 撞题（**"事故责任认定"比"交通疏通"更常见于论文与比赛**）／**闭环是唯一一条腿** | ❌ 不致命，但**闭环失败则"能交付、不能赢"** |

---

## 团队分工（4 人）

三个方向的角色结构一致，**具体职责见各方向的 `EXECUTION-PLAN.md`**：

| 角色 | 通用定位 |
|---|---|
| **P1 · 队长 / 产品 + 业务** | 领域业务理解、方案设计报告、答辩主讲、组委会沟通 |
| **P2 · 后端 / 架构** | MoMA 网关、流水线编排、数据管道 |
| **P3 · 算法 / 核心智能** | 技术命门（各方向不同）、评测体系 |
| **P4 · 前端 / 全栈** | 可视化、产品界面、上架材料 |

> ⚠️ **各方向 P1 的技能要求差别很大** —— BoostForge 需要外部补课「投流业务」；PathPilot 的领域知识更接近团队自身经验；RoadMind 需补**交规与司法文书体例**，且 P1 的第一件事是**定「什么算一条要件」的切分标准**。

---

## 当前状态

| 阶段 | 状态 |
|---|---|
| 方向选型 | ⏳ **三选一，未冻结** |
| 可行性验证 | ⏳ **待执行**（三个方向都未开始） |
| 方案冻结 | ⏳ 待验证通过 |

> ⚠️ **冻结新增方向** —— 详见 [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) 附录 A 的结论。
