from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import random # 가짜 영수증 번호를 만들기 위한 도구

app = FastAPI()

# -----------------------------------------------------------
# 👇 [중요] 어제 쓰시던 본인의 URL과 KEY를 다시 넣어주세요!
# -----------------------------------------------------------
SUPABASE_URL = "https://hbiopfdagviotoyotbza.supabase.co"
SUPABASE_KEY = "sb_publishable_E-Fuiryi7pqJ8POA7BH7Gw_3bOdZeUa"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. 주문 들어올 때 쓰는 양식
class DeliveryRequest(BaseModel):
    store_name: str
    store_addr: str
    cust_addr: str
    cust_phone: str
    food_price: int

# 2. 기사님 부를 때 쓰는 양식 (주문번호만 있으면 됨)
class RiderCallRequest(BaseModel):
    order_id: int

# [기능 1] 주문 접수 (기존과 동일)
@app.post("/request-delivery")
def request_delivery(order: DeliveryRequest):
    print(f"🚀 [주문 접수] {order.store_name} -> {order.cust_addr}")
    data = {
        "store_name": order.store_name,
        "store_addr": order.store_addr,
        "cust_addr": order.cust_addr,
        "cust_phone": order.cust_phone,
        "food_price": order.food_price,
        "status": "접수대기" # 처음엔 대기 상태
    }
    response = supabase.table("orders").insert(data).execute()
    # 방금 저장된 주문의 번호(ID)를 가져옴
    new_id = response.data[0]['id']
    return {"msg": "주문이 접수되었습니다.", "order_id": new_id}

# [기능 2] 배달 기사 호출 (새로 추가됨!)
@app.post("/call-rider")
def call_rider(req: RiderCallRequest):
    print(f"🛵 [배차 요청] 주문번호 {req.order_id}번 기사님 호출합니다...")
    
    # 1. (가짜) 배달대행사 연동 시뮬레이션
    # 실제로는 여기서 부릉/생각대로 서버로 요청을 보냅니다.
    fake_agency_id = f"VROONG_{random.randint(1000, 9999)}"

    # 2. DB 상태 업데이트 ('접수대기' -> '배차요청')
    update_data = {
        "status": "배차요청",
        "agency_id": fake_agency_id
    }
    
    # Supabase야, ID가 이거랑 똑같은 줄을 찾아서 업데이트해줘!
    response = supabase.table("orders").update(update_data).eq("id", req.order_id).execute()

    return {
        "msg": "기사님에게 요청을 보냈습니다.",
        "changed_status": "배차요청",
        "agency_ticket": fake_agency_id
    }# [기능 3] 배달 완료 처리 (기사님이 '완료' 눌렀을 때)
@app.post("/complete-delivery")
def complete_delivery(req: RiderCallRequest):
    print(f"✅ [배달 완료] 주문번호 {req.order_id}번 배달이 끝났습니다!")

    # DB 상태 업데이트 ('배차요청' -> '배달완료')
    # 실제로는 배달 완료 시간도 같이 기록합니다.
    update_data = {
        "status": "배달완료"
    }
    
    response = supabase.table("orders").update(update_data).eq("id", req.order_id).execute()

    return {
        "msg": "수고하셨습니다! 배달이 완료 처리되었습니다.",
        "final_status": "배달완료"
    }
    