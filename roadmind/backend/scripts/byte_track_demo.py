"""
ByteTrack 追踪起步脚本（D1 · 检测→追踪 demo）。

用 supervision 库的 ByteTrack 包装器，配合 ultralytics YOLO：
帧 → 检测框 → ByteTrack 追踪 → 输出 scene.json（轨迹点）+ 可视化结果视频/图。

依赖：pip install ultralytics supervision

用法：
    python byte_track_demo.py --video 路径/视频.mp4 --model yolov8n.pt
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from app.schemas.models import Scene, SceneEvent, TrajectoryPoint, Vehicle


def main(video_path: str, model_name: str, out_dir: str) -> None:
    from supervision import ByteTrack, Detections

    model = YOLO(model_name)
    tracker = ByteTrack(track_activation_threshold=0.25, lost_track_buffer=30)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_idx = 0

    # 轨迹缓存：track_id -> {t: x, y}
    tracks: dict[int, dict] = {}
    vehicles: dict[int, Vehicle] = {}
    events: list[SceneEvent] = []

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_dir / "tracked.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"), fps,
        (int(cap.get(3)), int(cap.get(4))),
    )

    # 类别名：YOLOv8 COCO 中 person=0, car=2, bicycle=1, motorcycle=3, truck=7, bus=5
    cls_to_type = {0: "pedestrian", 1: "bicycle", 2: "car", 3: "motorcycle",
                   5: "bus", 7: "truck"}

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        results = model(frame, verbose=False)[0]
        det = results.boxes

        boxes = det.xyxy.numpy() if det is not None else np.empty((0, 4))
        confs = det.conf.numpy() if det is not None else np.empty(0)
        clss = det.cls.numpy() if det is not None else np.empty(0)

        detections = Detections(
            xyxy=boxes,
            confidence=confs,
            class_id=clss.astype(int),
        )
        detections = tracker.update_with_detections(detections)

        h, w = frame.shape[:2]
        t = frame_idx / fps

        for det in detections:
            track_id = int(det.tracker_id)
            x1, y1, x2, y2 = det.xyxy
            cls = int(det.class_id)
            conf = float(det.confidence)

            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h

            if track_id not in tracks:
                tracks[track_id] = {"points": [], "type": cls_to_type.get(cls, "other")}
            tracks[track_id]["points"].append(TrajectoryPoint(t=t, x=cx, y=cy,
                                                              w=(x2 - x1) / w,
                                                              h=(y2 - y1) / h))

            # 画框
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"#{track_id} {cls_to_type.get(cls,'?')} {conf:.2f}",
                        (int(x1), int(y1) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 1)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()

    # 组装 scene（MVP：只有轨迹，事件/路况留待后续）
    for tid, info in tracks.items():
        pts = info["points"]
        max_speed = 0.0
        if len(pts) >= 2:
            # 粗略速度估算（像素/秒 → 简化 kmh，MVP 参考值）
            dx = pts[-1].x - pts[0].x
            dt = pts[-1].t - pts[0].t
            if dt > 0:
                max_speed = abs(dx) / dt * 100.0
        vehicles[tid] = Vehicle(id=tid, type=info["type"],
                                trajectory=pts, max_speed_kmh=round(max_speed, 1))

    scene = Scene(
        scene_id=Path(video_path).stem,
        source="video",
        vehicles=list(vehicles.values()),
        events=events,
        confidence=0.5,  # 低精度 MVP
    )

    out_json = out_dir / "scene.json"
    out_json.write_text(scene.model_dump_json(indent=2), encoding="utf-8")
    print(f"scene.json -> {out_json}")
    print(f"tracked.mp4  -> {out_dir / 'tracked.mp4'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="行车记录仪视频路径")
    ap.add_argument("--model", default="yolov8n.pt", help="YOLO 权重")
    ap.add_argument("--out", default="./data/outputs", help="输出目录")
    args = ap.parse_args()
    main(args.video, args.model, args.out)
