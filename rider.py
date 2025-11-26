# rider.py - 기사님 전용 앱 (목록 조회 기능 추가)
import streamlit as st
import requests
import pandas as pd

# Render 서버 주소
SERVER_URL = "https://spoonup-server.onrender.com"

st.set_page_config(page_title="스푼업 기사님", page_icon="🛵")
st.title("🛵 스푼업 라이더")

st.header("📢 배차 대기 목록")

# [핵심] 서버에서 '접수대기' 주문 명단 가져오기
try:
    res = requests.get(f"{SERVER_URL}/pending-orders")
    if res.status_code == 200:
        orders = res.json()
        
        if len(orders) > 0:
            st.success(f"현재 대기 중인 콜이 {len(orders)}건 있습니다!")
            
            # 주문 하나하나를 카드로 보여주기
            for order in orders:
                with st.expander(f"🍔 {order['store_name']} - {order['food_price']}원 (주문번호 {order['id']})"):
                    st.write(f"📍 픽업: {order['store_addr']}")
                    st.write(f"📍 배달: {order['cust_addr']}")
                    
                    # 바로 수락 버튼
                    if st.button(f"🚀 배차 수락 (ID: {order['id']})", key=f"btn_{order['id']}"):
                        # 수락 요청 보내기
                        res_call = requests.post(f"{SERVER_URL}/call-rider", json={"order_id": order['id']})
                        if res_call.status_code == 200:
                            st.toast("배차 성공! 안전 운전하세요.")
                            st.rerun() # 화면 새로고침해서 목록에서 지우기
                        else:
                            st.error("오류 발생")
        else:
            st.info("현재 대기 중인 주문이 없습니다. (새로고침 해보세요)")
    else:
        st.error("목록을 불러오지 못했습니다.")
except Exception as e:
    st.error(f"서버 연결 실패: {e}")

# 수동 새로고침 버튼
if st.button("🔄 목록 새로고침"):
    st.rerun()