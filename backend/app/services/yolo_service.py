from ultralytics import YOLO


model = YOLO("app/models/weight/best.pt")


def process_frame(frame):

    results = model(frame)

    detections = []

    annotated_frame = results[0].plot()

    for box in results[0].boxes:

        cls = int(box.cls[0])

        conf = float(box.conf[0])

        detections.append({
            "class_id": cls,
            "confidence": round(conf, 2)
        })

    return annotated_frame, detections