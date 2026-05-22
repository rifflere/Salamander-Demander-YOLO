import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from threading import Thread

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from collections import defaultdict

VIDEOS_DIR = Path(__file__).parent / "videos"
VIDEOS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Salamander Tracker POC")

model = YOLO("best.pt")
print(model.names)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")

job = {"status": "idle"}

# One distinct BGR color per track ID (cycles if there are more tracks than colors)
TRAIL_COLORS = [
    (255, 80, 80), (80, 255, 80), (80, 80, 255),
    (255, 255, 80), (255, 80, 255), (80, 255, 255),
    (255, 165, 80), (165, 80, 255),
]

@app.get("/")
def root():
    return {"ok": True}

# Draws each track's accumulated centroid path as a polyline on the frame (in-place)
def draw_paths(frame, track_history):
    for tid, points in track_history.items():
        if len(points) < 2:
            continue
        color = TRAIL_COLORS[tid % len(TRAIL_COLORS)]
        pts = np.array(points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=4)

# Normalizes the detection accumulator, applies a color map, blends with a reference frame,
# and saves the result as heatmap.png in the videos directory.
def generate_heatmap(accumulator, reference_frame):
    normalized = cv2.normalize(accumulator, None, 0, 255, cv2.NORM_MINMAX)
    colormap = cv2.applyColorMap(np.uint8(normalized), cv2.COLORMAP_JET)
    if reference_frame is not None:
        blended = cv2.addWeighted(reference_frame, 0.35, colormap, 0.65, 0)
    else:
        blended = colormap
    cv2.imwrite(str(VIDEOS_DIR / "heatmap.png"), blended)

# Processes the uploaded video frame-by-frame, runs YOLO tracking, and writes output.mp4.
# If show_path is True, a cumulative movement trail is drawn for each tracked salamander.
# If show_heatmap is True, a position heatmap PNG is generated after processing.
def run_track_job(show_path: bool = False, show_heatmap: bool = False):
    try:
        input_path = VIDEOS_DIR / "input.mp4"
        cap = cv2.VideoCapture(str(input_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"fps={fps} dims={width}x{height} frames={total}")

        output_path = VIDEOS_DIR / "output.mp4"
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"avc1"),
            fps,
            (width, height),
        )

        frames_seen = defaultdict(int)
        label_for = {}
        track_history = defaultdict(list)  # tid -> [(cx, cy), ...]
        accumulator = np.zeros((height, width), dtype=np.float32) if show_heatmap else None
        heatmap_radius = max(width, height) // 25
        reference_frame = None

        for frame_idx in range(total):
            ok, frame = cap.read()
            if not ok:
                break

            if show_heatmap and reference_frame is None:
                reference_frame = frame.copy()

            result = model.track(frame, persist=True, verbose=False)[0]
            annotated = result.plot()

            boxes = result.boxes
            if boxes is not None and boxes.id is not None:
                for tid, cls_id, xyxy in zip(
                    boxes.id.tolist(), boxes.cls.tolist(), boxes.xyxy.tolist()
                ):
                    tid = int(tid)
                    frames_seen[tid] += 1
                    label_for[tid] = model.names[int(cls_id)]

                    if show_path or show_heatmap:
                        cx = int((xyxy[0] + xyxy[2]) / 2)
                        cy = int((xyxy[1] + xyxy[3]) / 2)

                        if show_path:
                            track_history[tid].append((cx, cy))

                        if show_heatmap:
                            temp = np.zeros_like(accumulator)
                            cv2.circle(temp, (cx, cy), heatmap_radius, 1.0, -1)
                            accumulator += temp

            if show_path:
                draw_paths(annotated, track_history)

            writer.write(annotated)

            if frame_idx % 30 == 0:
                print(f"frame {frame_idx}/{total}")

            job["percent"] = int((frame_idx + 1) / total * 100)

        cap.release()
        writer.release()

        if show_heatmap:
            generate_heatmap(accumulator, reference_frame)

        tracks = [
            {
                "track_id": tid,
                "time_on_screen_s": round(count / fps, 2),
                "label": label_for[tid],
            }
            for tid, count in frames_seen.items()
        ]

        job.clear()
        job["status"] = "done"
        job["percent"] = 100
        result = {
            "video_url": f"http://localhost:8000/videos/output.mp4?t={int(time.time())}",
            "tracks": tracks,
        }
        if show_heatmap:
            result["heatmap_url"] = f"http://localhost:8000/videos/heatmap.png?t={int(time.time())}"
        job["result"] = result
    except Exception as e:
        print(f"error: {e}", flush=True)
        job.clear()
        job["status"] = "error"
        job["message"] = str(e)

# Accepts the video file and optional show_path/show_heatmap flags, then kicks off background processing.
@app.post("/track")
def start_track(
    video: UploadFile = File(...),
    show_path: bool = Form(False),
    show_heatmap: bool = Form(False),
):
    (VIDEOS_DIR / "input.mp4").write_bytes(video.file.read())
    job.clear()
    job["status"] = "processing"
    job["percent"] = 0
    Thread(target=run_track_job, args=(show_path, show_heatmap), daemon=True).start()
    return {"status": "processing"}
    
@app.get("/track")
def get_track():
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)