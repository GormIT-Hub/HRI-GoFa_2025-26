from ultralytics import YOLO
import cv2
import numpy as np

import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

def prepoznajObjekte(img_path:str) -> tuple[dict, np.ndarray]:

    MODEL_PATH = r"final_model\best_simplified.onnx"
    IMAGE_PATH = img_path 
    CONF_THRESH = 0.80

    names = ["Box", "Cup", "Green apple", "Red apple", "Red pepper"] 

    model = YOLO(MODEL_PATH)

    img0 = cv2.imread(IMAGE_PATH)

    if img0 is None:
        raise ValueError(f"Image failed to load: {IMAGE_PATH}")

    results = model.predict(source=img0, conf=CONF_THRESH, verbose=False)

    detections = {}

    for result in results:
        boxes = result.boxes

        for box in boxes:
            
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            label = names[cls]

            # Calculate center
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if label not in detections:
                detections[label] = []

            detections[label].append({
                "center": (cx, cy),
                "confidence": conf
            })

            # Draw bbox, center and label text
            cv2.rectangle(img0, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.circle(img0, (int(cx), int(cy)), 5, (0, 0, 255), -1)
            cv2.putText(
                img0,
                f"{label} {conf:.2f}",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    detections_lower = {k.lower(): v for k, v in detections.items()}

    return detections_lower, img0

if __name__ == '__main__':

    # Use example:
    dets, img = prepoznajObjekte("path/to/file")

    print(f'{dets=}')
    cv2.imshow("annotated_img", img)
    cv2.waitKey(0)
