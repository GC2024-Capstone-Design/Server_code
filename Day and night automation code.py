import time
from datetime import datetime
import cv2
import numpy as np
from day_baby_detect import detect_baby_in_day
from night_baby_detect import detect_baby_in_night

def get_time_mode(frame):
    b, g, r = cv2.split(frame)
    diff_rg = np.abs(np.mean(r) - np.mean(g))
    diff_rb = np.abs(np.mean(r) - np.mean(b))

    print(f"R: {r}, G: {g}, B: {b}")  # RGB 평균 값 출력
    
    if diff_rg < 0 and diff_rb < 0:  # 채널 간 차이가 작다면 IR 모드로 판단
        return 'night'
    return 'day'


def start_yolo(mode, frame):
    """YOLO 모델 실행."""
    print(f"Running YOLO in {mode} mode...")
    if mode == "day":
        detect_baby_in_day(frame)  # 주간 모드에서 아기 감지
    elif mode == "night":
        detect_baby_in_night(frame)  # 야간 모드에서 아기 감지
    else:
        print("No mode detected. Turn off the program")

def main():
    print("프로그램 시작...")
    # 카메라 초기화
    rtsp_url = "rtsp://172.25.83.240:8554/stream1"  # RTSP 스트림 URL
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    print("카메라가 실행 중입니다. 'q'를 눌러 종료하세요.")

    # 첫 번째 프레임을 가져와서 초기 모드 설정
    ret, frame = cap.read()
    if not ret:
        print("프레임을 가져올 수 없습니다.")
        return

    current_mode = get_time_mode(frame)  # 초기 모드 설정
    print(f"Initial mode: {current_mode}. Running YOLO...")

    try:
        while True:
            ret, frame = cap.read()
            print("새로 실행")
            if not ret:
                print("프레임을 가져올 수 없습니다.")
                break

            # 밝기 측정 후 모드 변경 여부 확인
            new_mode = get_time_mode(frame)
            print(f"현재 모드: {new_mode}")

            if new_mode != current_mode:
                # 모드 변경 시 모드 변경
                print(f"Mode changed to {new_mode}.")
                current_mode = new_mode

            start_yolo(current_mode, frame)  # 현재 모드에 따라 YOLO 실행

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
