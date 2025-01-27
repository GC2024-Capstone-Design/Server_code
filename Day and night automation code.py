import os
import time
from datetime import datetime
import subprocess

def get_time_mode():
    """현재 시간에 따라 주/야간 모드를 반환. 추후 밝기에 따라서 주/야간 구별하도록 로직 추가해야함."""
    current_hour = datetime.now().hour
    if 6 <= current_hour < 18: #06시부터 18시까지는 주간으로 판단, 나머지는 야간
        return "day"  # 주간 모드
    else:
        return "night"  # 야간 모드

def start_yolo(mode):
    """YOLO 모델 실행."""
    script_path_day = "./night_baby_detect.py"  # 실행할 스크립트 경로
    script_path_night = "./day_baby_detect.py"  # 실행할 스크립트 경로
    print(f"Starting YOLO in {mode} mode...")
    if mode == "day":
        return subprocess.Popen(["python", script_path_day, "day"]) #여기에다가는 주간 path 입력
    elif mode == "night":
        return subprocess.Popen(["python", script_path_night, "night"]) #여기에다가는 야간 path 입력
    else:
        print("No mode detected. Turn off the program")
        return

def main():
    current_mode = get_time_mode()  # 초기 모드 설정
    print(f"Initial mode: {current_mode}. Starting YOLO...")
    process = start_yolo(current_mode)  # 첫 YOLO 프로세스 시작

    try:
        while True:
            new_mode = get_time_mode()

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

if __name__ == "__main__":
    main()