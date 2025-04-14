import cv2

def draw_detection(frame, detection, plate_text=None, color=(255, 0, 0)):
    """Draws a bounding box and label for a detected vehicle."""
    x1, y1, x2, y2 = detection['bbox']
    confidence = detection.get('confidence', 0)
    label = f"{detection['class']} {confidence:.2f}"
    if plate_text:
        label = f"{plate_text} ({label})"

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)