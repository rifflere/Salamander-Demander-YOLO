"""Extract frames from a video file for a YOLO training dataset.

Every Nth frame is saved to disk (default: every 30th frame).
A 5-second clip at 30 fps yields 150 frames; sampling every 30 gives ~5 images.

Frames are saved to data/captured/ as JPGs named <prefix>_<frame_number>.jpg.
Run from the project root:
    python scripts/extract_frames.py --video path/to/clip.mp4
"""
import argparse
from pathlib import Path

import cv2


def open_video(path: str):
    """Open a video file, raising a clear error if it can't be read."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video file: {path!r}\n"
            "Check that the file exists and is a format OpenCV supports "
            "(mp4, avi, mov, mkv, …)."
        )
    return cap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True,
                        help="Path to the input video file")
    parser.add_argument("--output-dir", default="data/captured",
                        help="Directory to save extracted frames (default: data/captured)")
    parser.add_argument("--interval", type=int, default=30,
                        help="Save every Nth frame (default: 30)")
    parser.add_argument("--prefix", default="frame",
                        help="Filename prefix for saved frames (default: frame)")
    args = parser.parse_args()

    if args.interval < 1:
        raise ValueError("--interval must be at least 1")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = open_video(args.video)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    duration = total_frames / fps if fps else 0

    print(f"Video : {args.video}")
    print(f"Frames: {total_frames} total  |  {fps:.2f} fps  |  {duration:.1f}s duration")
    print(f"Saving every {args.interval}th frame to {output_dir.resolve()}")
    print()

    frame_index = 0
    saved = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break  # End of video or read error

        if frame_index % args.interval == 0:
            # Zero-pad the frame number to match the total width (e.g. 00042).
            width = len(str(total_frames)) if total_frames > 0 else 6
            filename = f"{args.prefix}_{frame_index:0{width}d}.jpg"
            path = output_dir / filename
            cv2.imwrite(str(path), frame)
            saved += 1
            print(f"  [{saved}] {filename}  (frame {frame_index})")

        frame_index += 1

    cap.release()
    print()
    print(f"Done. Saved {saved} frames from {frame_index} total to {output_dir.resolve()}")


if __name__ == "__main__":
    main()