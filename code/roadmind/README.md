# RoadMind · 原型代码

> 交通事故辅助研判智能体 —— 方案见 [`../../docs/roadmind/`](../../docs/roadmind/)
> 本目录只放**代码**，方案与论证在文档层，两者不混。

---

## 快速开始

```bash
cd D:\GIT\code\roadmind

uv sync --extra core      # 建 .venv 并装核心层（文书处理与检索栈）
uv run python check_env.py   # 自检，全绿才算配好
```

> 本机用 [uv](https://docs.astral.sh/uv/) 管理环境（已装在 `~/.local/bin`）。
> 若 `uv` 不在 PATH：`export PATH="$HOME/.local/bin:$PATH"`

---

## 分层依赖

按方案文档的优先级分层，**用到哪层装哪层**，不必一次配齐：

| 层 | 装什么 | 命令 | 体积 | 对应文档 |
|---|---|---|---|---|
| **① core** | numpy · pandas · jieba · pypdf · python-docx · openpyxl · rank-bm25 | `uv sync --extra core` | ~120 MB | [`JUDGMENT-DATA.md`](../../docs/roadmind/JUDGMENT-DATA.md) |
| **② agents** | LangGraph · LangChain · pydantic | `uv sync --extra core --extra agents` | +80 MB | [`ARCHITECTURE.md`](../../docs/roadmind/ARCHITECTURE.md) |
| **③ rag** | sentence-transformers · faiss-cpu | `uv sync --extra core --extra rag` | **+2.5 GB** | 条款 / 要件检索的向量化 |
| **④ vision** | ultralytics · torch · opencv | `uv sync --extra core --extra vision` | **+2.5 GB** | 仅当材料含影像时 |
| **⑤ ui** | streamlit · pyecharts | `uv sync --extra core --extra ui` | +120 MB | [`TEAM-ROLES.md`](../../docs/roadmind/TEAM-ROLES.md) P4 |
| ⑥ sumo | eclipse-sumo · traci · sumolib | `uv sync --extra sumo` | ~400 MB | **历史退路，当前方案不用** |

> **① 是命门**（方案验证清单第 1 条：判决书三段切分切得干净）。**先把它做掉，再考虑别的层。**
> ③ 只在词法检索（`rank-bm25`）不够用时才装 —— **先用最轻的跑通闭环，再上向量。**

---

## ⚠️ 路径规矩（本机必看）

本机 Windows 用户名是 `l'z'l`，**含单引号**。不少脚本与子进程调用不处理这种路径，会直接崩。

> **规矩：所有语料、场景与中间产物一律放 `D:\GIT\` 下，绝不放 `C:\Users\...`**

本目录已经在这个安全区内。**在别处新建文件前，先回想这一条。** 这条规矩在文书处理阶段同样适用。

---

## 目录约定

```
code/roadmind/
├── pyproject.toml    分层依赖定义
├── check_env.py      环境自检
├── .venv/            虚拟环境（已 gitignore）
└── corpus/           ← 语料与真值
    ├── raw/          原始文书（进版本控制）
    ├── split/        三段切分结果：① 输入段 / ②③ 真值段（进版本控制）
    ├── truth/        要件真值 R(c)（进版本控制）
    └── cache/        解析中间产物（已 gitignore）
```

`.venv/` 与 `corpus/cache/` 已在 `.gitignore` 里；
但**原始语料与真值文件**（`raw/` / `split/` / `truth/`）**必须进版本控制** —— 它们是可复现的基础与交付物。

---

## 下一步

按方案的优先级，本工程的第一件事**不是写 Agent**，而是：

> 跑通「文书 → 三段切分 → 泄漏扫描」的最小管线，**人工抽检 30–50 份确认切得干净**。

切不干净 = 标签泄漏 = 整套闭环指标虚高、论证作废 —— **这是本方案的头号工程风险，不过关不要往下做任何事。**

完整可执行步骤见 [`JUDGMENT-DATA.md`](../../docs/roadmind/JUDGMENT-DATA.md) 第二节起。
