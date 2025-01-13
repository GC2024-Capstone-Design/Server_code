import cv2
from ultralytics import YOLO
import time
import requests  # FastAPI 서버로 요청을 보내기 위해 필요

def run_yolo_combined():
    baby_pose = "C:/Users/halim/OneDrive/바탕 화면/졸압작품/colab_3000/best.pt"
    night_face = "C:/Users/halim/OneDrive/바탕 화면/졸압작품/night_face/night_best.pt"

    model1 = YOLO(baby_pose)
    model2 = YOLO(night_face)

    rtsp_url = "rtsp://172.25.86.101:8554/stream1"
    cap = cv2.VideoCapture(rtsp_url)

    frame_count = 0
    model1_count = 0
    model2_face_miss_count = 0
    frame_check_interval = 150

    paused = False

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            baby_detected_in_frame = False

            results1 = model1(frame)
            for box in results1[0].boxes:
                cls = box.cls.numpy()[0]
                label = model1.names[int(cls)]
                if label == "baby" and not baby_detected_in_frame:
                    model1_count += 1
                    baby_detected_in_frame = True

            results2 = model2(frame)
            face_detected = any(
                model2.names[int(box.cls.numpy()[0])] == "baby_night"
                for box in results2[0].boxes
            )
            if not face_detected:
                model2_face_miss_count += 1

            if frame_count % frame_check_interval == 0:
                if model1_count >= 150 and model2_face_miss_count >= 100:
                    # FastAPI 서버로 위험 상황 전송
                    requests.post("http://<YOUR_SERVER_IP>:8000/alert", json={"status": "danger"})
                    print("Baby In Danger! - 서버에 알림 전송")

                model1_count = 0
                model2_face_miss_count = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_yolo_combined()
