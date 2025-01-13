from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()

# 위험 상황을 앱에 전달하기 위한 비동기 이벤트
alert_event = asyncio.Event()

# 위험 상황 발생 시 호출할 경로
@app.post("/alert")
async def send_alert(data: dict):
    print("🚨 [Alert] Danger alert received!")  # CMD에 출력
    alert_event.set()  # 이벤트 발생
    return JSONResponse(content={"message": "Alert received"}, status_code=200)

# 앱에서 위험 상황을 체크하는 경로
@app.get("/check_alert")
async def check_alert():
    await alert_event.wait()  # 이벤트 발생 시까지 대기
    alert_event.clear()  # 이벤트 초기화
    print("✅ [Check Alert] Event acknowledged.")  # CMD에 출력
    return JSONResponse(content={"alert": "Person detected!"}, status_code=200)
