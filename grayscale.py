import cv2

# RTSP 스트림 주소 (예시로 적어둔 거라 네 주소로 바꿔야 함)
rtsp_url = "rtsp://172.16.49.161:8554/stream1"
# RTSP 스트림 열기
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("RTSP 스트림을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # Grayscale 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 창에 표시
    cv2.imshow('RTSP Grayscale Stream', gray)

    # 'q' 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
