# Salamander-Demander-YOLO
## Run App
Set up venv

on Windows:
```bash
cd backend
python3 -m venv venv
source venv\\Scripts\\activate
```

on Mac or Linux:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

## Run Backend
```bash
cd backend/
pip install -r requirements.txt # This will take a moment
python main.py
```

In separate terminal:
## Run Frontend
```bash
cd frontend/
npm i
npm run dev
```
## Train Model
1. Upload ensantina.mp4 or another salamander video to the root of the project
2. Run this in the root of the project to process the video
    First batch — clear old frames and start fresh
    ```
    python scripts/extract_frames.py --video clip1.mp4 clip2.mp4 --clear
    ```
    Add more later without wiping what's already there
    ```
    python scripts/extract_frames.py --interval 30 --video clip3.mp4
    ```

## Label Data in data directory
To open Label Studio:
```bash
docker run -it -p 8080:8080 -v ${PWD}/data/labelstudio:/label-studio/data heartexlabs/label-studio:latest
```
Label the data then extract the zip file created into the data folder of this project.

## Create the Model
### Prepare Dataset
```
python scripts/prepare_dataset.py --export-dir data
```

### Visualize Augmentation
```
python scripts/visualize_augmentations.py
```

### Train The Model
```
python scripts/train.py
```

