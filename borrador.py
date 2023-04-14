#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:16:59 2023

@author: henry
"""

import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
net = cv2.dnn.readNet("/home/henry/anylabeling_data/models/yolov8/yolov8x.onnx")
#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)




config = {'type': 'yolov8',
          'name': 'yolov8x',
          'display_name':'YOLOv5n Ultralytics',
          'model_path': 'anylabeling_assets/models/yolov5/yolov8x.onnx',
          'input_width': 640,
          'input_height': 640,
          'score_threshold': 0.5,
          'nms_threshold': 0.45,
          'confidence_threshold': 0.45,
          'classes': ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']}
classes = config["classes"]



input_image = cv2.imread('bus.jpg')
input_image = cv2.imread('coco_sample/000000000009.jpg')
[height, width, _] = input_image.shape


# Create a 4D blob from a frame.
blob = cv2.dnn.blobFromImage(
    input_image,
    1 / 255,
    (config["input_width"], config["input_height"]),
    [0, 0, 0],
    1,
    crop=False,
)
net.setInput(blob)
outputs = net.forward()
print(outputs)
outputs = np.array([cv2.transpose(outputs[0])])




# ========================================= post



# Lists to hold respective values while unwrapping.
class_ids = []
confidences = []
boxes = []

# Rows.
rows = outputs.shape[1]

image_height, image_width = input_image.shape[:2]

# Resizing factor.
x_factor = image_width / config["input_width"]
y_factor = image_height / config["input_height"]

# Iterate through 25200 detections.
for r in tqdm(range(rows)):
    row = outputs[0][r]
    classes_scores = row[4:]
    
    # Get the index of max class score and confidence.
    _, confidence, _, (_, class_id) = cv2.minMaxLoc(classes_scores)

    # Discard confidence lower than threshold
    if  confidence >= config["confidence_threshold"]:
        confidences.append(confidence)
        class_ids.append(class_id)

        cx, cy, w, h = row[0], row[1], row[2], row[3]

        left = int((cx - w / 2) * x_factor)
        top = int((cy - h / 2) * y_factor)
        width = int(w * x_factor)
        height = int(h * y_factor)
        
        box = np.array([left, top, width, height])
        boxes.append(box)

# Perform non maximum suppression to eliminate redundant
# overlapping boxes with lower confidences.
indices = cv2.dnn.NMSBoxes(
    boxes,
    confidences,
    config["confidence_threshold"],
    config["nms_threshold"]
)

output_boxes = []
for i in indices:
    box = boxes[i]
    left = box[0]
    top = box[1]
    width = box[2]
    height = box[3]
    label = classes[class_ids[i]]
    score = confidences[i]

    output_box = {
        "x1": left,
        "y1": top,
        "x2": left + width,
        "y2": top + height,
        "label": label,
        "score": score,
    }

    output_boxes.append(output_box)
    cv2.rectangle(input_image, (left, top), ((left + width), (top + height)), (0,255,0), 3)

cv2.imwrite("test.jpg", input_image)
#Image.fromarray(cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB))
