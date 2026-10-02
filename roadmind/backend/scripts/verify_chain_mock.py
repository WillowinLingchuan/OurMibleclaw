"""D6 闭环核心逻辑验证：直接调用 mock 判定+应急服务，检查输出结构。"""
import json
import sys
import os

# 使 app 可导入（backend 目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import llm_service
from app.services.rag import rag_service


def run_case(text: str):
    print("=" * 50)
    print(f"输入文字: {text}")
    # M2 检索
    retrieved = rag_service.retrieve(text)
    print(f"RAG 检索到 {len(retrieved)} 条")
    # M3 判定
    judgement = llm_service.judge(text, retrieved)
    print(f"责任判定: {judgement['responsibility']}")
    print(f"  依据: {judgement['basis']}")
    print(f"  理由: {judgement['reasoning']}")
    print(f"  置信度: {judgement['confidence']}")
    # M4 应急（由事故类型推导）
    accident_type = "vehicle_pedestrian" if "行人" in text or "撞人" in text \
        else ("rear_end" if "追尾" in text else "general")
    resp = llm_service.draft_response(accident_type)
    print(f"事故类型: {accident_type}")
    print(f"应急步骤({len(resp['steps'])}):")
    for s in resp["steps"]:
        print(f"  {s['order']}. {s['action']}{' [紧急]' if s['urgent'] else ''}")
    print(f"  保险: {resp['insurance']}")


if __name__ == "__main__":
    print("D6 闭环逻辑验证 (mock)\n")
    run_case("路口我车直行，对方左转弯未让行，两车发生碰撞")
    run_case("后车追尾前车，前车正常行驶，前车司机下车后被撞")
