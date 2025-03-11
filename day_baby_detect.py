import cv2
from ultralytics import YOLO
import time
import requests

def detect_baby_in_day():
    # 모델 경로 설정
    baby_pose = "../가중치 파일 모음/colab_3000/best.pt"
    day_face = "C:/Users/halim/Downloads/weights.pt"

    # 사용할 YOLO 모델 초기화
    model1 = YOLO(baby_pose)  # 포즈 감지 모델
    model2 = YOLO(day_face)  # 얼굴 감지 모델

    # 스트리밍 소스 설정
    video_path = "rtsp://172.25.83.240:8554/stream1"
    cap = cv2.VideoCapture(video_path)

    # 초기 상태 설정
    frame_count = 0
    supine_or_baby_count = 0  # supine 또는 baby 감지 카운터
    prone_count = 0  # prone 감지 카운터
    face_miss_count = 0  # 얼굴 감지 실패 카운터
    frame_check_interval = 675  # 675프레임(15초 간격) 체크
    paused = False

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            supine_or_baby_detected = False  # supine 또는 baby 감지 플래그, 중복 체크 방지용
            prone_detected = False  # prone 감지 플래그

            # 포즈 감지
            results1 = model1(frame)
            for box in results1[0].boxes:
                cls = box.cls.numpy()[0]
                label = model1.names[int(cls)]

                if label in ["supine", "baby"] and not supine_or_baby_detected:
                    supine_or_baby_count += 1
                    supine_or_baby_detected = True
                    print(f"supine/baby 감지: {label}, supine_or_baby_count: {supine_or_baby_count}")

                if label == "prone" and not prone_detected:
                    prone_count += 1
                    prone_detected = True
                    print(f"prone 감지: prone_count: {prone_count}")

            # 얼굴 인식
            results2 = model2(frame)
            face_detected = False
            for box in results2[0].boxes:
                cls = box.cls.numpy()[0]
                label = model2.names[int(cls)]

                if label in ["babycrying", "babynormal", "babysmiling"]:
                    face_detected = True
                    break

            if not face_detected:  # 얼굴 감지 실패 카운터 증가
                face_miss_count += 1
                print(f"얼굴 미감지: face_miss_count: {face_miss_count}")

            # 675프레임마다 조건 확인
            if frame_count % frame_check_interval == 0:
                # 조건 1: supine 또는 baby 상태인데 얼굴이 지속적으로 감지되지 않는 경우
                if supine_or_baby_count >= 500 and face_miss_count >= 450:
                    paused = True
                    print("🚨 위험 상황: 침구류로 얼굴이 덮였을 가능성")
                    response = requests.post("http://localhost:8000/alert", json={"status": "danger", "reason": "face_cover"})
                    if response.status_code == 200:
                        print("✅ Alert sent successfully!")
                    else:
                        print(f"❌ Failed to send alert. Status code: {response.status_code}")
                    break

                # 조건 2: prone 상태가 지속되는 경우
                if prone_count >= 300:
                    paused = True
                    print("🚨 위험 상황: 아기가 엎드린 상태로 위험")
                    response = requests.post("http://localhost:8000/alert", json={"status": "danger", "reason": "prone_position"})
                    if response.status_code == 200:
                        print("✅ Alert sent successfully!")
                    else:
                        print(f"❌ Failed to send alert. Status code: {response.status_code}")
                    break

                # 카운터 초기화
                print("카운터 초기화")
                print(f"supine_or_baby_count: {supine_or_baby_count}, prone_count: {prone_count}, face_miss_count: {face_miss_count}")
                supine_or_baby_count = 0
                prone_count = 0
                face_miss_count = 0
                continue

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 'q' 키를 누르면 종료
            break
        elif key == ord(' '):  # 스페이스바로 멈추거나 재생
            paused = not paused
        elif paused:  # 멈춘 상태에서는 딜레이 없이 반복
            time.sleep(0.3)

    print("프로그램 종료.")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_baby_in_day()
