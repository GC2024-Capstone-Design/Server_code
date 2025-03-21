import cv2
from ultralytics import YOLO
import time
import requests

def detect_baby_in_night(frame):
    # 모델 경로 설정
    baby_pose = "../best.pt"
    night_face = "../best.pt"

    # 사용할 YOLO 모델 초기화
    model1 = YOLO(baby_pose)
    model2 = YOLO(night_face)

    # 스트리밍 소스 설정
    # video_path = "C:/Users/halim/OneDrive/바탕 화면/졸압작품/night baby(1) - Clipchamp로 제작.mp4"
    # cap = cv2.VideoCapture(video_path)

    # 현재는 스트리밍 소스가 영상으로 되어있음
    # 추후 카메라 연결 시 밑의 코드로 변경 후 스트리밍 소스 제거
    # cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 사용

    #     # 초당 프레임 계산 코드
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # print(f"Source Video FPS: {fps}")

    # 초기 상태 설정
    frame_count = 0
    model1_count = 0  # supine/baby 감지 카운터
    model2_face_miss_count = 0  # 얼굴 감지 실패 카운터
    frame_check_interval = 10  # 300프레임마다 체크
    paused = False

    while True:
        if not paused:
            # ret, frame = cap.read()
            # if not ret:
                # break

            frame_count += 1
            baby_detected_in_frame = False  # 플래그: 한 프레임에서 한 번만 증가하도록 설정

            # 포즈 탐지
            results1 = model1(frame)
            for box in results1[0].boxes:
                cls = box.cls.numpy()[0]
                label = model1.names[int(cls)]

                if label == "baby" and not baby_detected_in_frame:
                    model1_count += 1
                    baby_detected_in_frame = True  # 플래그를 True로 설정하여 중복 증가 방지
                    print("baby_count 증가, model1_count의 수: {}".format(model1_count))

            # 얼굴 인식
            results2 = model2(frame)
            face_detected = False
            for box in results2[0].boxes:
                cls = box.cls.numpy()[0]
                label = model2.names[int(cls)]

                if label == "baby_night":
                    face_detected = True
                    break

            if not face_detected:  # 얼굴 감지 실패 카운터 증가
                model2_face_miss_count += 1
                print("face_미감지 증가, model2_face_miss_count의 수: {}".format(model2_face_miss_count))

            # 300프레임마다 조건 확인
            if frame_count % frame_check_interval == 0:
                # moddel1_count가 뜻하는 것: 아기가 있는 프레임의 개수
                # model2_face_miss_count가 뜻하는 것: 아기가 있는 것과 무관하게 얼굴 인식이 되지 않은 프레임의 개수
                # 만약 model1_count를 증가 시 아기인 것이 더욱 확실해 지는 것
                # 만약 model2_face_miss_count 증가 시 위험이 아닐 가능성에도 알림이 울리게 하는 것
                if model1_count >= 500 and model2_face_miss_count >= 450:
                    paused = True
                    print("baby_count:{}, baby_night_face_detect:{}".format(model1_count, model2_face_miss_count))
                    print("🚨 Baby In Danger! Sending alert to server...")
                    response = requests.post("http://localhost:8000/alert", json={"status": "danger"})
                    if response.status_code == 200:
                        print("✅ Alert sent successfully!")
                    else:
                        print(f"❌ Failed to send alert. Status code: {response.status_code}")
                    return

                print("카운터 초기화되었습니다.")
                frame_count = 0
                print("baby_count:{}, baby_night_face_not_detect:{}".format(model1_count, model2_face_miss_count))

                model1_count = 0
                model2_face_miss_count = 0
                return

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 'q' 키를 누르면 종료
            break
        elif key == ord(' '):  # 스페이스바로 멈추거나 재생
            paused = not paused
        elif paused:  # 멈춘 상태에서는 딜레이 없이 반복
            time.sleep(0.3)

    print("프로그램 종료.")

if __name__ == "__main__":
    detect_baby_in_night()
