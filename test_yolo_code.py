from ultralytics import YOLO
import cv2
import requests

# YOLO11n 모델 로드
model = YOLO("yolo11n.pt")

# 카메라에서 실시간 영상 가져오기
cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 사용

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("카메라에서 프레임을 가져올 수 없습니다.")
        break

    # YOLO 모델로 객체 감지 수행
    results = model(frame)

    # 사람이 감지되었는지 확인
    person_detected = any(
        model.names[int(box.cls.numpy()[0])] == "person"
        for box in results[0].boxes
    )

    # 사람이 감지되면 FastAPI 서버에 POST 요청 전송
    if person_detected:
        response = requests.post("http://localhost:8000/alert", json={"status": "danger"})
        print("🚨 Person detected! Alert sent to server.")

    # 결과 출력
    cv2.imshow("YOLO11n Realtime Detection", frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 정리
cap.release()
cv2.destroyAllWindows()
