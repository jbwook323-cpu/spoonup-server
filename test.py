import requests
import time

# 내 서버 주소
URL_ORDER = "http://127.0.0.1:8000/request-delivery"
URL_CALL = "http://127.0.0.1:8000/call-rider"

# 1. [주문] 짜장면 주문 넣기
print("1️⃣ 주문을 넣습니다...")
order_data = {
    "store_name": "스푼업 반점",
    "store_addr": "울산 중구 성남동",
    "cust_addr": "테스트 아파트 101동",
    "cust_phone": "010-1234-1234",
    "food_price": 22000
}
res1 = requests.post(URL_ORDER, json=order_data)
result1 = res1.json()

# 방금 생성된 주문번호(ID) 가져오기
new_order_id = result1['order_id']
print(f"   👉 주문 성공! 주문번호: {new_order_id}번")

print("-" * 30)
time.sleep(2) # 2초 정도 고민하는 척 (사장님이 주문 확인 중)

# 2. [배차] 기사님 호출 버튼 누르기
print(f"2️⃣ {new_order_id}번 주문의 배달 기사님을 부릅니다...")
call_data = {
    "order_id": new_order_id
}
res2 = requests.post(URL_CALL, json=call_data)
result2 = res2.json()

print(f"   👉 호출 완료! 상태: {result2['changed_status']}")
print(f"   👉 배달대행사 접수번호: {result2['agency_ticket']}")
# ... (위쪽 코드 그대로 유지) ...

print("-" * 30)
time.sleep(2) # 2초 후 (기사님이 배달 중...)

# 3. [완료] 배달 완료 처리
print(f"3️⃣ {new_order_id}번 배달을 완료 처리합니다...")
res3 = requests.post("http://127.0.0.1:8000/complete-delivery", json={"order_id": new_order_id})
print(f"   👉 최종 결과: {res3.json()['msg']}")
