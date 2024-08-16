from time import time

import cv2
from CodingRider.drone import Drone
from mediapipe.python.solutions import face_detection as mp_face_detection

from src.util import println
from src.util.controller.port import get_controller_port_name

is_takeoff = False
takeoff_time = 0

drone = Drone()
drone.open(get_controller_port_name(0))

capture = cv2.VideoCapture(0)

with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0
) as face_detection:
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            continue

        frame.flags.writeable = False
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame)
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if (detections := results.detections) is not None:
            for detection in detections:
                keypoints = detection.location_data.relative_keypoints

                nose = keypoints[2]
                height, width, channel = frame.shape
                nose_position = (int(nose.x * width), int(nose.y * height))

                text = f"Face detected / x: {nose_position[0]}, y: {nose_position[1]}"
                cv2.putText(frame, text, (10, 30,), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0,), 1)
                cv2.circle(frame, nose_position, 50, (0, 0, 255,), 5, cv2.LINE_AA)

                if (not is_takeoff) and ((current_time := time()) - takeoff_time) > 3:
                    is_takeoff = True
                    takeoff_time = current_time
                    println("Taking off")
                    drone.sendTakeOff()
        elif is_takeoff and ((current_time := time()) - takeoff_time) > 2:
            is_takeoff = False
            takeoff_time = current_time
            drone.sendLanding()
        cv2.imshow("MediaPipe Face Detection", frame)
        if cv2.waitKey(1) == 27:
            break

capture.release()
cv2.destroyAllWindows()