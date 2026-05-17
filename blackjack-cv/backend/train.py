"""
Training script for the playing card detection model.

Steps:
  1. Download a playing card dataset from Roboflow Universe.
  2. Fine-tune a lightweight Ultralytics YOLO model for 50 epochs.
  3. Copy the best weights to backend/vision/models/best.pt.

User-adjustable values are marked with  # <-- ADJUST THIS
"""

import os
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Roboflow dataset configuration
# ---------------------------------------------------------------------------

# Set your Roboflow API key as an environment variable:
#   export ROBOFLOW_API_KEY="your_key_here"
API_KEY = os.environ.get("ROBOFLOW_API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "ROBOFLOW_API_KEY environment variable is not set. "
        "Export it before running this script."
    )

WORKSPACE = "augmented-startups"      # <-- ADJUST THIS: your Roboflow workspace slug
PROJECT   = "playing-cards-ow27d"     # <-- ADJUST THIS: your Roboflow project slug
VERSION   = 4                          # <-- ADJUST THIS: dataset version number

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

# Using yolo11n.pt (Ultralytics YOLOv11 nano) as the lightest available model.
# If your Ultralytics version does not include yolo11n.pt, substitute yolov8n.pt.
BASE_MODEL = "yolo11n.pt"              # <-- ADJUST THIS if needed

EPOCHS      = 50
IMAGE_SIZE  = 640
PROJECT_DIR = "card_training"          # local Ultralytics run output directory

# ---------------------------------------------------------------------------
# Download dataset
# ---------------------------------------------------------------------------

from roboflow import Roboflow

rf      = Roboflow(api_key=API_KEY)
project = rf.workspace(WORKSPACE).project(PROJECT)
dataset = project.version(VERSION).download("yolov8")  # YOLOv8 format works with YOLO11

print(f"[Train] Dataset downloaded to: {dataset.location}")

# ---------------------------------------------------------------------------
# Fine-tune model
# ---------------------------------------------------------------------------

from ultralytics import YOLO

model = YOLO(BASE_MODEL)

print(f"[Train] Starting training for {EPOCHS} epochs with {BASE_MODEL}…")
results = model.train(
    data=os.path.join(dataset.location, "data.yaml"),
    epochs=EPOCHS,
    imgsz=IMAGE_SIZE,
    project=PROJECT_DIR,
    name="best_run",
    exist_ok=True,
    verbose=True,
)

# ---------------------------------------------------------------------------
# Copy best weights
# ---------------------------------------------------------------------------

best_weights_src = Path(PROJECT_DIR) / "best_run" / "weights" / "best.pt"
best_weights_dst = Path(__file__).parent / "vision" / "models" / "best.pt"

best_weights_dst.parent.mkdir(parents=True, exist_ok=True)

if best_weights_src.exists():
    shutil.copy(best_weights_src, best_weights_dst)
    print(f"[Train] Best model saved to: {best_weights_dst}")
else:
    print(f"[Train] WARNING: Expected weights not found at {best_weights_src}. "
          "Check training output directory.")
