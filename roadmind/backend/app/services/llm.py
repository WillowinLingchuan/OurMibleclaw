"""
LLM 网关服务。

MVP 阶段 use_mock=True 时返回确定性模板结果（保证全链路可跑）；
接入真实 MoMA/OpenAI 兼容网关后，use_mock=False 走真实调用。
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.rule_judge import judge as rule_judge_combined


class LLMService:
    async def judge(self, scene_text: str, evidence: Any, scene: dict | None = None) -> dict:
        """责任判定。MVP 阶段用规则判定（场景优先/文字兜底），迭代阶段替换为 LLM。"""
        if settings.use_mock:
            return rule_judge_combined(scene_text, evidence, scene)
        # TODO(迭代): 调用真实 LLM（MoMA 网关）
        raise NotImplementedError("真实 LLM 接入待实现")

    async def draft_response(self, accident_type: str) -> dict:
        """应急方案。MVP 阶段按事故类型返回模板。"""
        templates = {
            "vehicle_pedestrian": {
                "priority": 1,
                "steps": [
                    {"order": 1, "action": "立即开启双闪，停车熄火", "urgent": True},
                    {"order": 2, "action": "拨打 120 急救，说明伤员情况", "urgent": True},
                    {"order": 3, "action": "拨打 122/110 报警", "urgent": True},
                    {"order": 4, "action": "放置三角警示牌（来车方向 50 米）", "urgent": True},
                    {"order": 5, "action": "保护现场，勿移动伤员，等待救援", "urgent": True},
                ],
                "insurance": "同步拨打保险公司报案，拍摄现场照片与全景视频，保留证据。",
            },
            "rear_end": {
                "priority": 2,
                "steps": [
                    {"order": 1, "action": "开启双闪，停车熄火", "urgent": True},
                    {"order": 2, "action": "放置三角警示牌（来车方向 50 米）", "urgent": True},
                    {"order": 3, "action": "人员撤至安全地带，勿留在车道", "urgent": True},
                    {"order": 4, "action": "无伤亡可先拍照固定证据后撤离至安全处协商", "urgent": False},
                ],
                "insurance": "拨打保险报案，保留现场照片与行车记录仪。",
            },
        }
        return templates.get(
            accident_type,
            {
                "priority": 2,
                "steps": [
                    {"order": 1, "action": "开启双闪，停车熄火", "urgent": True},
                    {"order": 2, "action": "放置三角警示牌", "urgent": True},
                    {"order": 3, "action": "人员撤至安全地带", "urgent": True},
                    {"order": 4, "action": "有伤亡拨打 120，报警 122/110", "urgent": True},
                ],
                "insurance": "保留现场证据，及时报保险。",
            },
        )


llm_service = LLMService()
