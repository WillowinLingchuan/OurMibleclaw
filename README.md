# OurMibleclaw · 爆量工场 BoostForge

> 第五届「移动云杯」智算应用创新大赛 · **模型应用赛** 参赛项目
> 基于移动云 **MoMA**（Mobile Model Marketplace）平台构建

---

## 项目简介

**「爆量工场 BoostForge」** —— 面向短剧投流团队的 **AI 素材工厂与投放策略优化智能体**。

### 特定能力

> **从一集已有成片出发，批量产出可投放的投流素材，并依据投放数据回流，让每轮素材的转化率高于上一轮。**

### 为什么做这个

短剧行业最大的成本不是制作，是**投流**——买量成本占收入 **70-80%**。投流团队每日需产出几十到上百条素材做 A/B 测试，且素材 3-7 天就衰减疲劳，必须持续产出。**人工剪辑产能是硬瓶颈。**

我们不"再造一部短剧"，而是做**让已有短剧赚到更多钱的那一层**。

---

## 文档

> **目录结构：每个候选方向一个独立目录**，各自存放该方向的方案 / 架构 / 演示脚本。
> ⚠️ 现有**三个候选方向并列评估中**，除 BoostForge 外均**未冻结**。

| 方向 | 目录 | 状态 |
|---|---|---|
| **爆量工场 BoostForge** | [`docs/boostforge/`](docs/boostforge/) | ✅ 已确定方向（⏳ 待验证） |
| **明径 PathWise** | [`docs/pathwise/`](docs/pathwise/) | ⏳ 候选 · 评估中 |
| **通途 ClearWay** | [`docs/clearway/`](docs/clearway/) | ⏳ 候选 · 评估中 |
| **方向决策记录** | [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) | 评估矩阵 · 选型理由 · **验证清单** · **附录 A：三方向可行性评估** |

### 各方向目录内容

| 目录 | 文件 |
|---|---|
| [`docs/boostforge/`](docs/boostforge/) | `EXECUTION-PLAN.md` — 短剧投流素材工厂 |
| [`docs/pathwise/`](docs/pathwise/) | `EXECUTION-PLAN.md` — 高校学业-综测路径规划 |
| [`docs/clearway/`](docs/clearway/) | `EXECUTION-PLAN.md`（方案）· [`ARCHITECTURE.md`](docs/clearway/ARCHITECTURE.md)（智能体角色架构）· [`DEMO-SCRIPT.md`](docs/clearway/DEMO-SCRIPT.md)（演示脚本） |

### 建议阅读顺序

1. 先看 [`docs/DECISION-RECORD.md`](docs/DECISION-RECORD.md) 第二节「决策标准」和第六节「验证清单」——理解**决策标准是什么**，以及**当前卡在哪**
2. 再看 [`docs/boostforge/EXECUTION-PLAN.md`](docs/boostforge/EXECUTION-PLAN.md) 第一、二、四节——理解**已确定方向是什么**，以及**为什么它是智能体而不是工作流**
3. 若在考虑换方向：看 [`docs/clearway/EXECUTION-PLAN.md`](docs/clearway/EXECUTION-PLAN.md) **第十二节「三方向对比矩阵」** —— 三个方向的逐项对比与建议

---

## 团队分工（4 人）

| 角色 | 职责 |
|---|---|
| **P1 · 队长 / 产品 + 投流策略** | 投流业务理解、钩子类型库、投放策略、答辩主讲 |
| **P2 · 后端 / 架构** | MoMA 网关、七工位编排、路由决策器、数据回流管道 |
| **P3 · 算法 / 策略进化** | CTR 预测模型、策略进化器、高光识别、评测体系 |
| **P4 · 前端 / 全栈** | 素材墙、投放看板、效果曲线、素材管理 |

---

## 当前状态

| 阶段 | 状态 |
|---|---|
| 方向选型 | ✅ 已确定（BoostForge） |
| 可行性验证 | ⏳ **待执行** |
| 方案冻结 | ⏳ 待验证通过 |
| 新增候选方向 | ⏳ **评估中**（明径 PathWise，见决策记录第六节） |

### ★ 下一步：三项验证（本周可完成）

1. 拿到 **MoMA 账号**，查看可用模型列表
2. 跑通一次最小调用（视频理解：给一段视频问"里面发生了什么"）
3. 拿一集真实短剧素材，手工剪 3 条钩子素材

### 两条悬空的前置事实

- 🔴 **十亿 Token 配额是否覆盖视频模型** —— 不覆盖则需砍掉「AI 重生成钩子镜头」模块
- 🔴 **历史投放数据集能否拿到** —— 拿不到则「策略进化器」闭环需依赖模拟器

> 详见 `docs/DECISION-RECORD.md` 第六节。
