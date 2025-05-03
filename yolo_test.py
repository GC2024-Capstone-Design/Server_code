from ultralytics import YOLO
import cv2

model = YOLO("../야간2.pt", task="detect")
video_path = "../야간 흑백.mov"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("비디오 파일을 열 수 없습니다.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
wait_time =1   # FPS에 따라 대기 시간 결정

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    annotated_frame = results[0].plot()

    cv2.imshow("YOLO Detection", annotated_frame)

    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
