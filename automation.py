import cv2
import numpy as np
import requests
from ultralytics import YOLO


def get_time_mode(frame):
    b, g, r = cv2.split(frame)
    mean_b = np.mean(b)
    mean_g = np.mean(g)
    mean_r = np.mean(r)

    print(f"Mean R: {mean_r}, Mean G: {mean_g}, Mean B: {mean_b}")  # RGB 평균 값 출력

    # 빨간색 채널의 평균 값이 특정 임계값 이상이고, 다른 채널보다 현저히 높으면 야간 모드로 판단
    if mean_g < 100:
        return 'night'
    return 'day'


def draw_boxes(frame, results, model, color):
    for box in results[0].boxes:
        cls = box.cls.numpy()[0]
        label = model.names[int(cls)]
        conf = box.conf.numpy()[0]
        x1, y1, x2, y2 = map(int, box.xyxy.numpy()[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

def detect_baby_in_day(frame):
    # 모델 경로 설정
    baby_pose = "../3000_best.pt"
    day_face = "../best.pt"

    # 사용할 YOLO 모델 초기화
    model1 = YOLO(baby_pose)  # 포즈 감지 모델
    model2 = YOLO(day_face)  # 얼굴 감지 모델

    # 초기 상태 설정
    frame_count = 0
    supine_or_baby_count = 0  # supine 또는 baby 감지 카운터
    prone_count = 0  # prone 감지 카운터
    face_miss_count = 0  # 얼굴 감지 실패 카운터
    frame_check_interval = 10  # 675프레임(15초 간격) 체크
    paused = False

    frame_count += 1
    supine_or_baby_detected = False  # supine 또는 baby 감지 플래그, 중복 체크 방지용
    prone_detected = False  # prone 감지 플래그

    # 포즈 감지
    results1 = model1(frame)
    draw_boxes(frame, results1, model1, (0, 255, 0))  # 경계 상자 그리기 (초록색)
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
    draw_boxes(frame, results2, model2, (0, 255, 0))  # 경계 상자 그리기 (초록색)
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
            print("🚨 위험 상황: 침구류로 얼굴이 덮였을 가능성")
            response = requests.post("http://localhost:8000/alert", json={"status": "danger", "reason": "face_cover"})
        # 조건 2: prone 상태가 지속되는 경우
        if prone_count >= 300:
            print("🚨 위험 상황: 아기가 엎드린 상태로 위험")
            response = requests.post("http://localhost:8000/alert", json={"status": "danger", "reason": "prone_position"})

        # 카운터 초기화
        print("카운터 초기화")
        print(f"supine_or_baby_count: {supine_or_baby_count}, prone_count: {prone_count}, face_miss_count: {face_miss_count}")
        supine_or_baby_count = 0
        prone_count = 0
        face_miss_count = 0

def detect_baby_in_night(frame):
    # 모델 경로 설정
    baby_pose = "../3000_best.pt"
    night_face = "../night_best.pt"

    # 사용할 YOLO 모델 초기화
    model1 = YOLO(baby_pose)
    model2 = YOLO(night_face)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

    # 초기 상태 설정
    frame_count = 0
    model1_count = 0  # supine/baby 감지 카운터
    model2_face_miss_count = 0  # 얼굴 감지 실패 카운터
    frame_check_interval = 10  # 300프레임마다 체크
    paused = False

    frame_count += 1
    baby_detected_in_frame = False  # 플래그: 한 프레임에서 한 번만 증가하도록 설정

    # 포즈 탐지
    results1 = model1(gray_frame)
    draw_boxes(frame, results1, model1, (0, 255, 0))  # 경계 상자 그리기 (초록색)
    for box in results1[0].boxes:
        cls = box.cls.numpy()[0]
        label = model1.names[int(cls)]

        if label == "baby" and not baby_detected_in_frame:
            model1_count += 1
            baby_detected_in_frame = True  # 플래그를 True로 설정하여 중복 증가 방지
            print("야간 아기 인식 추가: {}".format(model1_count))

    # 얼굴 인식
    results2 = model2(gray_frame)
    draw_boxes(frame, results2, model2, (255, 0, 0))  # 경계 상자 그리기 (파란색)
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
        if model1_count >= 500 and model2_face_miss_count >= 450:
            print("baby_count:{}, baby_night_face_detect:{}".format(model1_count, model2_face_miss_count))
            print("🚨 Baby In Danger! Sending alert to server...")

        print("카운터 초기화되었습니다.")
        frame_count = 0
        print("baby_count:{}, baby_night_face_not_detect:{}".format(model1_count, model2_face_miss_count))

        model1_count = 0
        model2_face_miss_count = 0

def main():
    print("프로그램 시작...")
    rtsp_url = "rtsp://172.25.83.240:8554/stream1"
    cap = cv2.VideoCapture(rtsp_url)
    # 비디오 파일 경로
    # video_path = "/Users/kwonhalim/Desktop/capstone_design/야간.mp4"
    # cap = cv2.VideoCapture(video_path)
    cap = cv2.VideoCapture(rtsp_url)  # RTSP 스트림 열기

    if not cap.isOpened():
        print("비디오 파일을 열 수 없습니다.")
        return

    print("비디오가 실행 중입니다. 'q'를 눌러 종료하세요.")


    # 첫 번째 프레임을 가져와서 초기 모드 설정
    ret, frame = cap.read()
    if not ret:
        print("프레임을 가져올 수 없습니다.")
        return

    current_mode = get_time_mode(frame)  # 초기 모드 설정
    print(f"Initial mode: {current_mode}. Running YOLO...")
    
    frame_count = 0  # 프레임 카운터 추가

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 가져올 수 없습니다.")
                break

            # 10프레임마다 주간/야간 모드 재확인
            if frame_count % 10 == 0:
                current_mode = get_time_mode(frame)
                print(f"Mode rechecked at frame {frame_count}: {current_mode}")



            # 현재 프레임을 흑백으로 변환
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame_3channel = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)  # YOLO는 3채널 입력을 요구


            # 현재 프레임을 창으로 표시
            if current_mode == "day":
                detect_baby_in_day(frame)
            else:
                detect_baby_in_night(frame)

            cv2.imshow('auto', gray_frame_3channel)
            cv2.imshow('original', frame)
            frame_count += 1  # 프레임 카운터 증가

            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 'q' 키를 누르면 종료
                break

    except KeyboardInterrupt:
        print("Stopping YOLO...")
        return 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()