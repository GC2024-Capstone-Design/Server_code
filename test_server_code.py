from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import asyncio
import uvicorn

app = FastAPI()

# 위험 상황을 앱에 전달하기 위한 비동기 이벤트
alert_event = asyncio.Event()

# 웹소켓에 연결된 클라이언트 리스트
connected_clients = set()


# 🔴 YOLO가 호출하는 엔드포인트 (HTTP)
@app.post("/alert")
async def send_alert(data: dict):
    print("🚨 [Alert] Danger alert received!")  # 터미널에 로그 출력
    alert_event.set()  # 이벤트 발생

    # 연결된 웹소켓 클라이언트들에게 알림 전송
    message = {"alert": "Person detected!"}
    await notify_clients(message)

    return JSONResponse(content={"message": "Alert received"}, status_code=200)


# 🔵 웹소켓을 통한 실시간 알림 전송
@app.websocket("/ws/alert")
async def websocket_alert(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)  # 클라이언트 추가
    print("🔗 [WebSocket] Client connected")

    try:
        while True:
            await alert_event.wait()  # 이벤트 발생 대기
            alert_event.clear()  # 이벤트 초기화

            # 웹소켓을 통해 클라이언트에게 알림 전송
            message = {"alert": "Person detected!"}
            await websocket.send_json(message)

    except Exception as e:
        print(f"❌ [WebSocket] Error: {e}")

    finally:
        connected_clients.remove(websocket)
        print("🔌 [WebSocket] Client disconnected")


# ⚡ 연결된 모든 웹소켓 클라이언트에게 메시지 전송
async def notify_clients(message: dict):
    if connected_clients:
        await asyncio.gather(*[client.send_json(message) for client in connected_clients])


if __name__ == "__main__" :
	uvicorn.run(app)
