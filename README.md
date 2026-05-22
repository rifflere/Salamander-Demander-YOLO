# Salamander-Demander-YOLO
*Created by [Augy](https://www.linkedin.com/in/augy-markham/) + [Rebecca](https://www.linkedin.com/in/rebecca-riffle/)*

A YOLO-based app that analyzes salamander videos to track individual salamanders and extract metrics including time on screen, movement path trails, and position heatmaps.

This is a reimagination of the 2025 Centroid Finder App ([backend](https://github.com/rifflere/Centroid-Finder-App), [frontend](https://github.com/rifflere/centroid-finder-frontend)) — built by Rebecca, Augy, and [Tyler](https://www.linkedin.com/in/dev-tylergilmore/) in collaboration with researchers at OSU — which used color masking algorithms to locate salamanders frame-by-frame and export CSV location data. This version replaces that approach with YOLO object detection for more robust tracking.

**Table of Contents**
1. [Run Instructions](#run-instructions)
1. [User Instruction](#user-instructions)
1. [Model Training Instructions](#model-training-instructions)
1. [Reflection](#reflection)


## Run Instructions
You will need to have two terminals open, one to run the backend and one to run the frontend.

### Set up backend
#### Set up venv
on *Windows*:
```bash
cd backend
python3 -m venv venv
source venv\\Scripts\\activate
```

on *Mac or Linux*:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```
#### Run Backend
```bash
cd backend/
pip install -r requirements.txt # This will take a moment
python main.py
```
### Set up Frontend
In a different terminal, run:
```bash
cd frontend/
npm i
npm run dev
```
## User Instructions
1. Open the app in your browser (default: `http://localhost:5173`).
2. Click **Choose File** and select a salamander video from your computer (any common video format works).
3. (Optional) Check **Show path** to draw a colored movement trail on the video for each tracked salamander.
4. (Optional) Check **Show heatmap** to generate a position heatmap image showing where salamanders spent the most time.
5. Click **Upload** — the button will change to **Processing...** while the video is being analyzed.
6. Watch the progress bar to track how far along the analysis is.
7. Once processing finishes, the app displays:
   - **Annotated video** — the original footage with bounding boxes drawn around each detected salamander, with native playback controls (play, pause, seek). If **Show path** was checked, a colored trail shows each salamander's movement history up to that point in the video.
   - **Position heatmap** — (if **Show heatmap** was checked) a single image overlaid on a reference frame, using a blue-to-red color scale to show where salamanders spent the most time.
   - **Metrics table** — one row per tracked salamander showing its Track ID, label, and total time on screen (in seconds).

> If an error occurs, an error message will appear inside the upload card with details.

## Model Training Instructions
### Train Model
1. Upload a training video to the `model` directory
2. `cd model`
2. Process the video
    First batch — clear old frames and start fresh
    ```bash
    python scripts/extract_frames.py --video clip1.mp4 clip2.mp4 --clear # replace "clip1.mp4" and "clip2.mp4" with your video name
    ```
    Add more later without wiping what's already there
    ```
    python scripts/extract_frames.py --interval 30 --video clip3.mp4
    ```

### Label Data in data directory
Open Docker on your computer.  
Open Label Studio:
```bash
docker run -it -p 8080:8080 -v ${PWD}/data/labelstudio:/label-studio/data heartexlabs/label-studio:latest
```
Label the data then extract the zip file created into the data folder of this project.
### Create the Model
#### Prepare Dataset
```
python scripts/prepare_dataset.py --export-dir data
```

#### Visualize Augmentation
```
python scripts/visualize_augmentations.py
```

#### Train The Model
```
python scripts/train.py
```
#### Update the app model
Delete `backend/best.pt`.
Copy `best.pt` from `model/runs/detect/train/weights/`, and paste it into `backend/`. Restart app.

## Reflection
### Color Masking vs. YOLO comparison