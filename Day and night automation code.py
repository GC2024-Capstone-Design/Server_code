import os
import time
from datetime import datetime
import subprocess
import cv2
import numpy as np

# 밝기 기준 설정
BRIGHTNESS_THRESHOLD = 50  # 밝기 기준값

def determine_brightness(frame):
    """
    이미지의 밝기를 계산합니다.
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_frame)
    return brightness

def get_time_mode(frame):
    """현재 밝기에 따라 주/야간 모드를 반환."""
    brightness = determine_brightness(frame)
    if brightness > BRIGHTNESS_THRESHOLD:
        return "day"  # 밝으면 주간 모드
    else:
        return "night"  # 어두우면 야간 모드

def start_yolo(mode):
    """YOLO 모델 실행."""
    script_path_day = "./night_baby_detect.py"  # 실행할 스크립트 경로
    script_path_night = "./day_baby_detect.py"  # 실행할 스크립트 경로
    print(f"Starting YOLO in {mode} mode...")
    if mode == "day":
        return subprocess.Popen(["python", script_path_day, "day"]) # 주간 path 입력
    elif mode == "night":
        return subprocess.Popen(["python", script_path_night, "night"]) # 야간 path 입력
    else:
        print("No mode detected. Turn off the program")
        return

def main():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)  # 파라미터 값만 바꾸면 영상/라즈베리파이 카메라 가능

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
    print(f"Initial mode: {current_mode}. Starting YOLO...")

    process = start_yolo(current_mode)  # 첫 YOLO 프로세스 시작

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 가져올 수 없습니다.")
                break

            # 밝기 측정 후 모드 변경 여부 확인
            new_mode = get_time_mode(frame)

            if new_mode != current_mode:
                # 모드 변경 시 기존 YOLO 프로세스 종료 및 재시작
                print(f"Mode changed to {new_mode}. Restarting YOLO...")
                process.terminate()  # 기존 프로세스 종료
                process.wait()  # 종료 대기
                current_mode = new_mode
                process = start_yolo(current_mode)  # 새 프로세스 시작

            time.sleep(10)  # 10초마다 상태 체크

    except KeyboardInterrupt:
        print("Stopping YOLO...")
        process.terminate()  # 프로그램 종료 시 프로세스 종료
        process.wait()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
