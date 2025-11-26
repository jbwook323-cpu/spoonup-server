# main.py - 실시간 통신 기능이 추가된 서버
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from supabase import create_client, Client
from typing import List
import random
import json

app = FastAPI()

# -----------------------------------------------------------
# 👇 [본인 키 입력] Supabase 설정
# -----------------------------------------------------------
SUPABASE_URL = "https://hbiopfdagviotoyotbza.supabase.co"
SUPABASE_KEY = "sb_publishable_E-Fuiryi7pqJ8POA7BH7Gw_3bOdZeUa"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 📡 [핵심] 실시간 통신 관리자 (교환원)
# ==========================================
class ConnectionManager:
    def __init__(self):
        # 접속한 사람들의 명단을 가지고 있음
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📞 누군가 실시간 채널에 접속했습니다! (현재 {len(self.active_connections)}명)")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("📴 누군가 접속을 끊었습니다.")

    # 📢 접속한 모든 사람에게 방송하기 (팝업 띄우기용)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# ==========================================
# 📦 기존 데이터 모델
# ==========================================
class DeliveryRequest(BaseModel):
    store_name: str
    store_addr: str
    cust_addr: str
    cust_phone: str
    food_price: int

class RiderCallRequest(BaseModel):
    order_id: int

# ==========================================
# 🔌 [새로운 창구] 실시간 연결용 (웹소켓)
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 연결을 유지하면서 듣기만 함 (혹은 클라이언트가 보낸 메시지 받기)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==========================================
# 🚀 기존 API (업그레이드 됨)
# ==========================================

# 1. 주문 접수 -> (추가됨) 사장님/기사님에게 "새 주문!" 알림 발송
@app.post("/request-delivery")
async def request_delivery(order: DeliveryRequest): # async가 붙었습니다
    print(f"🚀 [주문 접수] {order.store_name}")
    
    data = {
        "store_name": order.store_name,
        "store_addr": order.store_addr,
        "cust_addr": order.cust_addr,
        "cust_phone": order.cust_phone,
        "food_price": order.food_price,
        "status": "접수대기"
    }
    
    response = supabase.table("orders").insert(data).execute()
    new_id = response.data[0]['id']

    # 📢 [방송] 모든 접속자에게 "새 주문이 들어왔어요!" 라고 소리침
    await manager.broadcast(json.dumps({
        "type": "NEW_ORDER",
        "msg": f"🔔 신규 주문! {order.store_name} ({order.food_price}원)"
    }))
    
    return {"msg": "주문 접수 완료", "order_id": new_id}

# 2. 배차 요청 -> (추가됨) "배차 완료!" 알림 발송
@app.post("/call-rider")
async def call_rider(req: RiderCallRequest):
    print(f"🛵 [배차 요청] {req.order_id}번")
    fake_agency_id = f"VROONG_{random.randint(1000, 9999)}"

    update_data = {"status": "배차요청", "agency_id": fake_agency_id}
    supabase.table("orders").update(update_data).eq("id", req.order_id).execute()

    # 📢 [방송] 배차 소식 알림
    await manager.broadcast(json.dumps({
        "type": "RIDER_MATCHED",
        "msg": f"🛵 {req.order_id}번 주문 배차 완료! ({fake_agency_id})"
    }))

    return {"msg": "요청 완료", "changed_status": "배차요청", "agency_ticket": fake_agency_id}

# 3. 배달 완료
@app.post("/complete-delivery")
def complete_delivery(req: RiderCallRequest):
    # (여기는 알림 생략, 필요하면 추가 가능)
    update_data = {"status": "배달완료"}
    supabase.table("orders").update(update_data).eq("id", req.order_id).execute()
    return {"msg": "완료 처리됨", "final_status": "배달완료"}
    # [기능 4] 대기 중인 주문 목록 조회 (기사님 앱용)
@app.get("/pending-orders")
def get_pending_orders():
    # Supabase에서 'status'가 '접수대기'인 것만 가져오라!
    response = supabase.table("orders").select("*").eq("status", "접수대기").execute()
    return response.data