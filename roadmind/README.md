# RoadMind · 代码骨架

多智能体交通事故辅助研判系统的基础代码（MVP 阶段可运行）。

## 目录结构
```
roadmind/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── core/config.py          # 配置（use_mock 开关）
│   │   ├── schemas/models.py       # Pydantic 数据模型（scene/judgment/response）
│   │   ├── graph/
│   │   │   ├── state.py            # LangGraph 状态
│   │   │   ├── builder.py          # 构图：perceive→retrieve→judge→respond→aggregate
│   │   │   └── nodes/              # 各智能体节点
│   │   ├── services/               # M1感知 / M2 RAG / LLM 服务（mock）
│   │   └── api/                    # REST 路由 + 任务管理
│   └── requirements.txt
└── frontend/
    └── index.html                  # 双视角（车主/交警）页面
```

## 快速启动（MVP，默认 mock，无需任何凭据）

```bash
cd roadmind/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000 即可使用双视角界面。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/health` | 健康检查 |
| POST | `/api/cases` | 创建案件（json: `{"text_description": "..."}`），启动多智能体分析 |
| GET  | `/api/tasks/{id}/status` | 查询任务状态与进度 |
| GET  | `/api/tasks/{id}/result` | 查询最终结果（scene/judgment/response） |

## 设计说明

- **功能不砍，精度递进**：MVP 阶段所有服务走 mock（`app/core/config.py` 中 `use_mock=True`），
  保证全链路可跑、可演示；真实视频感知（YOLO）、LLM（MoMA 网关）、向量检索（chromadb）
  在迭代阶段替换（代码中已标注 `TODO(迭代)`）。
- **多智能体交互**：LangGraph 状态图编排感知 → 检索 → 判定 → 应急 → 汇聚。
- **判定定位为辅助建议**：`judgment.note` 明确"非最终裁定"。
