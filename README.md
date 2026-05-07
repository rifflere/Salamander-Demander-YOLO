# Salamander-Demander-YOLO
1. Upload ensantina.mp4 or another salamander video to the root of the project
2. Run this in the root of the project to process the video
    ``` bash
    python scripts/extract_frames.py --video ensantina.mp4
    ```

## Label Data in data directory
To open Label Studio:
```bash
docker run -it -p 8080:8080 -v ${PWD}/data/labelstudio:/label-studio/data heartexlabs/label-studio:latest
```