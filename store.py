# store.py - 사장님 전용 앱
import streamlit as st
import requests

# Render 서버 주소
SERVER_URL = "https://spoonup-server.onrender.com"

st.set_page_config(page_title="스푼업 사장님", page_icon="🏪")
st.title("🏪 스푼업 사장님 전용")

st.header("📝 새 주문 접수")

# 입력 폼
store = st.text_input("가게 이름", "스푼업 버거")
addr = st.text_input("배달 주소", "울산 남구 삼산동")
price = st.number_input("가격", value=15000)

if st.button("주문 접수"):
    data = {
        "store_name": store,
        "store_addr": "주소 미정", # 추후 사장님 정보에서 가져올 예정
        "cust_addr": addr,
        "cust_phone": "010-0000-0000",
        "food_price": price
    }
    try:
        res = requests.post(f"{SERVER_URL}/request-delivery", json=data)
        if res.status_code == 200:
            st.success(f"주문 등록 완료! (주문번호: {res.json()['order_id']})")
        else:
            st.error("주문 실패")
    except:
        st.error("서버 연결 실패")