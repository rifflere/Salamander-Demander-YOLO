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
pip install -r requirements.txt # This may take a few minutes
```

on *Mac or Linux*:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # This may take a few minutes
#### Run Backend
```bash
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
2. Click **Choose File** and select a [salamander video](#why-salamander-videos) from your computer (any common video format works).
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
This project is built on a model trained to detect [salamander movement](#why-salamander-videos) in videos. We have included the services we used to build our model, so you may *optionally* train a new model to track different targets. This section requires a little more technical experience, and for Docker to be running on your computer.

### Set up venv
on *Windows*:
```bash
cd model
python3 -m venv venv
source venv\\Scripts\\activate
pip install -r requirements.txt # This will take a few minutes
```

on *Mac or Linux*:
```bash
cd model
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # This will take a few minutes
```
### Upload Training Video(s)
1. Upload training video(s) to the `model` directory.
2. Process the video
    
    First batch — clear old frames and start fresh
    ```bash
    cd model
    python scripts/extract_frames.py --video clip1.mp4 clip2.mp4 --clear # replace "clip1.mp4" and "clip2.mp4" with your video name
    ```
    Add more later without wiping what's already there
    ```bash
    python scripts/extract_frames.py --interval 30 --video clip3.mp4 # replace "clip3.mp4" with your video name
    ```
### Label Data
Open Docker on your computer.  
Open Label Studio:
```bash
docker run -it -p 8080:8080 -v ${PWD}/data/labelstudio:/label-studio/data heartexlabs/label-studio:latest
```
Label the data then extract the zip file created into `model/data`.
### Create the Model
#### Prepare Dataset
Export dataset to the data directory:
```
python scripts/prepare_dataset.py --export-dir data
```

#### Visualize Augmentation
Generate visual augmentations:
```
python scripts/visualize_augmentations.py
```
#### Train The Model
Train the model:
```bash
python scripts/train.py # This will take a few minutes to run, longer for long videos
```
Open `runs/detect/run1/results.png` to see the loss and accuracy curves over training.
#### Update the app model
If you are satisfied with the results of the training, replace the model in the backend with the new model.
1. Delete `backend/best.pt`.
2. Copy `best.pt` from `model/runs/detect/train/weights/`, and paste it into `backend/`. Restart backend.

## Reflection
### Color Masking vs. YOLO comparison
A year ago we built an image detection app that had a similar interface, but was very different 'under the hood'. Our previous model relied on manual color tracking. We binarized the image based on a user-provided target color and threshhold, then used a graph search algorithm to locate the largest area that fit the target color, and tracked the centroid location over each frame, generating a CSV output that identified salamander location at each one second interval. This new app runs YOLO to detect salamanders based on a model that we trained. We were able to build the model and send meaningful metrics to the front end relatively quickly, but the model has some limitations that are tricky to fix, for example, if a salamander leaves the screen and comes back, the model counts it as a new salamander, resulting in some weird data. The YOLO-based app was able to handle some cases that would have challenged our original model, such as multiple salamanders and salamanders that were a close color match to the backdrop. Overall, YOLO helped us build the salamander detector more quickly, but gave us a lot less control over the outcomes.

| | Color Masking | YOLO |
| --- | --- | --- |
| Complexity to build | High | Low |
| Complexity to modify detection algorithm | Medium | High |
| Consistency of results | High | Medium |
| Ability to handle variability in videos | Low | High |

## Note
### Why Salamander Videos
This project was originally intended to help with a specific research project. This model has been trained on top-down videos of both real and plastic salamanders moving around a rectangular area.