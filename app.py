import streamlit as st
import requests
import pandas as pd

# 우리 서버 주소
SERVER_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="스푼업 기사님 앱", page_icon="🛵")

st.title("🛵 스푼업 기사님 전용 앱")
st.subheader("현재 대기 중인 콜을 확인하세요")

# 1. 서버에서 데이터 가져오기 (Supabase랑 직접 통신 안 하고, 우리 서버에게 물어봄)
# (간단하게 구현하기 위해 test.py처럼 직접 요청을 쏘는 버튼을 만듭니다)

# 탭 만들기 (기사님용 / 관리자용)
tab1, tab2 = st.tabs(["기사님 (주문수락)", "관리자 (주문생성)"])

with tab1:
    st.write("### 📢 배차 대기 목록")
    
    # 주문 번호를 입력해서 배차 받는 심플한 방식
    order_id_input = st.number_input("배차 받을 주문번호를 입력하세요", min_value=1, step=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 배차 요청 (수락)"):
            try:
                res = requests.post(f"{SERVER_URL}/call-rider", json={"order_id": order_id_input})
                if res.status_code == 200:
                    st.success(f"배차 성공! {res.json()['msg']}")
                    st.info(f"영수증: {res.json()['agency_ticket']}")
                else:
                    st.error("오류가 발생했습니다.")
            except:
                st.error("서버가 꺼져있거나 연결할 수 없습니다.")

    with col2:
        if st.button("✅ 배달 완료"):
            try:
                res = requests.post(f"{SERVER_URL}/complete-delivery", json={"order_id": order_id_input})
                if res.status_code == 200:
                    st.balloons() # 성공 축하 효과
                    st.success("배달 완료 처리되었습니다! 고생하셨습니다.")
                else:
                    st.error("오류가 발생했습니다.")
            except:
                st.error("서버 연결 실패")

with tab2:
    st.write("### 📝 새 주문 넣기 (테스트용)")
    store = st.text_input("가게 이름", "스푼업 버거")
    addr = st.text_input("배달 주소", "울산 남구 삼산동")
    price = st.number_input("가격", value=15000)
    
    if st.button("주문 접수"):
        data = {
            "store_name": store,
            "store_addr": "가게 주소 미정",
            "cust_addr": addr,
            "cust_phone": "010-0000-0000",
            "food_price": price
        }
        try:
            res = requests.post(f"{SERVER_URL}/request-delivery", json=data)
            if res.status_code == 200:
                new_id = res.json()['order_id']
                st.success(f"주문이 등록되었습니다! 주문번호: {new_id}")
            else:
                st.error("주문 실패")
        except:
            st.error("서버 연결 실패")
                