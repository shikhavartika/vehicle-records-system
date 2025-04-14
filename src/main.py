import cv2
import yaml
import logging
import time
from datetime import datetime

from camera_handler import CameraHandler
from vision.detector import VehicleDetector
from vision.recognizer import LicensePlateRecognizer
from logic.entry_exit import EntryExitLogic
from database import db_manager
from utils import drawing

# --- Configuration and Logging Setup ---
try:
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("Error: config/config.yaml not found.")
    exit(1)
except yaml.YAMLError as e:
     print(f"Error parsing config/config.yaml: {e}")
     exit(1)


log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO').upper(), logging.INFO)
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialization ---
logging.info("Initializing Vehicle Record System...")
db_manager.initialize_database() # Ensure tables exist

detector = VehicleDetector(
    model_path=config['vision']['detector_model_path'],
    confidence_threshold=config['vision']['detection_confidence_threshold']
)
recognizer = LicensePlateRecognizer() if config['vision']['lpr_enabled'] else None

cameras = {}
entry_exit_logics = {}
for cam_config in config['cameras']:
    cam_id = cam_config['id']
    cameras[cam_id] = CameraHandler(cam_config['source'])
    entry_exit_logics[cam_id] = EntryExitLogic(cam_config)

# --- Main Loop ---
running = True
frame_count = 0
last_log_time = time.time()

try:
    while running:
        start_time = time.time()

        for cam_id, camera in cameras.items():
            ret, frame = camera.read_frame()
            if not ret or frame is None:
                # logging.warning(f"Skipping frame for camera {cam_id}")
                continue # Skip if frame reading failed

            display_frame = frame.copy() # Make a copy for drawing

            # 1. Detect Vehicles
            detections = detector.detect(frame)

            # Draw zones for visualization
            entry_exit_logics[cam_id].draw_zones(display_frame)

            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                vehicle_crop = frame[y1:y2, x1:x2]
                plate_text = None
                vehicle_id = f"veh_{det['bbox']}" # Temporary ID based on bbox

                # 2. Recognize License Plate (if enabled and crop is valid)
                if recognizer and vehicle_crop.size > 0:
                    plate_text = recognizer.recognize(vehicle_crop)
                    if plate_text:
                        vehicle_id = plate_text # Use plate as ID if recognized

                # 3. Determine Entry/Exit Event
                event = entry_exit_logics[cam_id].determine_event(vehicle_id, det['bbox'])

                # 4. Log Event to Database
                if event:
                    # Optional: Save a snapshot image
                    # timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    # image_filename = f"captures/{cam_id}_{vehicle_id}_{event}_{timestamp_str}.jpg"
                    # cv2.imwrite(image_filename, vehicle_crop) # Ensure 'captures' directory exists
                    db_manager.log_vehicle_event(cam_id, event, license_plate=plate_text) #, image_path=image_filename)
                elif time.time() - last_log_time > 60: # Log detection periodically even without entry/exit
                    # Avoid flooding db, log only occasionally if no specific event
                    # db_manager.log_vehicle_event(cam_id, "DETECTED", license_plate=plate_text)
                    # last_log_time = time.time() # Reset timer only if logged
                    pass


                # 5. Draw Detection on Display Frame
                drawing.draw_detection(display_frame, det, plate_text=plate_text)


            # Display the processed frame (optional)
            cv2.imshow(f"Camera {cam_id}", display_frame)

            frame_count += 1

        # Handle Keyboard Interrupt (Press 'q' to quit)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            logging.info("Quit signal received. Shutting down.")
            running = False

        # Optional: Calculate and log FPS
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
             fps = 1.0 / elapsed_time
             logging.debug(f"Processing FPS: {fps:.2f}")

except KeyboardInterrupt:
    logging.info("Keyboard interrupt received. Shutting down.")
    running = False
finally:
    # --- Cleanup ---
    logging.info("Releasing resources...")
    for camera in cameras.values():
        camera.release()
    cv2.destroyAllWindows()
    logging.info("System shut down.")