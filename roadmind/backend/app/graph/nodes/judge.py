"""M3 判定节点：scene + 检索 → judgment。"""
from __future__ import annotations

from app.core.config import settings
from app.graph.state import State
from app.schemas.models import Judgment, Responsibility
from app.services.llm import llm_service
from app.services.scene_summary import build_scene_summary


async def judge_node(state: State) -> State:
    state["step"] = "judging"
    text = state.get("input_text", "")
    scene = state.get("scene")
    # 用场景摘要（基于检测数据）生成判责输入，回退到用户文字
    scene_summary = build_scene_summary(scene.model_dump() if scene else None, text)
    scene_dict = scene.model_dump() if scene else None

    raw = await llm_service.judge(scene_summary, state.get("retrieved"), scene_dict)
    state["judgment"] = Judgment(
        scene_id=state.get("case_id", "case"),
        responsibility=Responsibility(**raw["responsibility"]),
        basis=raw["basis"],
        reasoning=raw["reasoning"],
        confidence=raw["confidence"],
    )
    return state
