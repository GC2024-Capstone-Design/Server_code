import cv2

# 입력 영상 경로
input_path = '../야간.mp4'
# 출력 영상 경로
output_path = '야간_흑백.mp4'

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(input_path)

# 프레임 너비, 높이, FPS 가져오기
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# 비디오 라이터 설정 (코덱: MP4V)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), isColor=False)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 흑백으로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 영상 저장
    out.write(gray)

# 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()
