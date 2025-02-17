from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import asyncio
import uvicorn
import json

app = FastAPI()

# 웹소켓 연결된 클라이언트 리스트
connected_clients = set()

@app.websocket("/ws/alert")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # 웹소켓 연결 유지용
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.post("/alert")
async def send_alert(data: dict):
    status = data.get("status", "unknown")
    
    # status가 "danger"인 경우 모든 웹소켓 클라이언트에 메시지 전송
    if status == "danger":
        message = json.dumps({"status": "danger"})
        await broadcast_alert(message)
    
    return JSONResponse(content={"message": "Alert received"}, status_code=200)

async def broadcast_alert(message: str):
    # 현재 연결된 모든 클라이언트에게 메시지 전송
    for client in connected_clients:
        await client.send_text(message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
