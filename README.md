<div align=center>

### 가천대학교 인공지능학과 졸업작품

## Members
<img width="160px" src=""/> | <img width="160px" src=""/> | <img width="160px" src=""/> | <img width="160px" src=""/> | 
|:-----:|:-----:|:-----:|:-----:|
|[](https://github.com/)|[](https://github.com/)|[](https://github.com/KwonHalim)|[](https://github.com/)|
|팀원|팀원|팀원|팀원|
|김준기<br/>|이지현<br/>|권하림<br/>|나송주<br/>|

</div>
<br/>


## Architecture
<img width="1110" alt="Image" src="https://github.com/user-attachments/assets/60c16f0a-7cc7-49f7-b19e-17803fb8cd6c" />

# 👶 Smart Baby Sleep Monitoring System

> **YOLOv11 기반 수면 모니터링 시스템**  
> 라즈베리파이에서 로컬 실행되는 AI 모델로 아기의 수면 중 위험 자세와 얼굴 미감지를 감지합니다.

---

## 📌 프로젝트 개요

이 시스템은 수면 중인 아기의 자세(posture) 및 얼굴 노출 여부를 실시간으로 분석하여, 다음과 같은 **위험 상황**을 감지합니다:

- `supine` 자세에서 얼굴이 일정 시간 이상 감지되지 않음 → **이불로 얼굴이 덮였을 가능성**
- `prone` (엎드림) 자세가 지속됨 → **질식 위험 가능성**
- 야간 모드에서 얼굴(`baby_night`)이 지속적으로 감지되지 않음

> 💡 **YOLOv11 커스텀 모델을 라즈베리파이에서 직접 실행**하며, 서버 IP를 연결해야 합니다.

---

## 🛠 기술 스택

| 구성 요소       | 기술                                                            |
|----------------|---------------------------------------------------------------|
| 추론 모델       | [YOLOv11](https://github.com/ultralytics/ultralytics), 커스텀 모델 |
| 비디오 처리     | OpenCV                                                        |
| 장치 환경       | Raspberry Pi 4B / Python 3.9+                                 |

---

## ✅ 주요 기능

### 🌞 주간 모드 (`day`)
- 아기 자세 (`baby`, `supine`, `prone`) 감지
- 얼굴 상태 (`babysmiling`, `babycrying`, `babynormal`) 인식
- supine 상태에서 얼굴 미감지 시 **경고 발생**

### 🌙 야간 모드 (`night`)
- 아기 (`baby`) 및 얼굴 (`baby_night`) 감지
- 지속적인 얼굴 미감지 시 **경고 발생**

### ⚠️ 경고 조건
- `supine` or `baby` ≥ 500 프레임 **AND** 얼굴 미감지 ≥ 450 프레임
- `prone` 자세 ≥ 300 프레임
- 야간 얼굴 미감지 ≥ 450 프레임

---

## ▶️ 실행 방법

1. **YOLO 모델 준비**
   - `../best.pt` 경로에 학습된 YOLOv11 모델을 저장하세요.

2. **테스트 비디오 준비**
   - `video_path`를 아기 영상 파일 경로로 설정 (`.mp4` 등).
   - rtsp 프로토콜을 활용하여 실시간 인식도 가능합니다.

3. **프로그램 실행**
   


