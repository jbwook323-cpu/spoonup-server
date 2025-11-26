import streamlit as st
import requests
import time

# ---------------------------------------------------------
# 1. 서버 설정
# ---------------------------------------------------------
# (로컬 테스트용 주소)
SERVER_URL = "https://spoonup-server.onrender.com"

st.set_page_config(page_title="스푼업 기사님", page_icon="🛵")
st.title("🛵 스푼업 라이더 (Auto)")

# ---------------------------------------------------------
# 2. 상태 저장소 (이전 주문 개수 기억하기)
# ---------------------------------------------------------
if 'last_count' not in st.session_state:
    st.session_state.last_count = 0

st.header("📢 실시간 배달 요청")

# ---------------------------------------------------------
# 3. 데이터 가져오기 & 알림 로직
# ---------------------------------------------------------
try:
    # 서버에서 대기 목록 가져오기
    res = requests.get(f"{SERVER_URL}/pending-orders")
    
    if res.status_code == 200:
        orders = res.json()
        current_count = len(orders)
        
        # [핵심 로직] 아까보다 주문이 늘었으면 -> 알림 띄우기!
        if current_count > st.session_state.last_count:
            st.toast(f"🔔 신규 주문 {current_count - st.session_state.last_count}건 도착!", icon="🛵")
            # (원한다면 여기서 소리 재생 코드도 추가 가능)
        
        # 현재 개수 기억해두기
        st.session_state.last_count = current_count

        # 화면에 목록 그리기
        if current_count > 0:
            st.success(f"현재 대기 중인 콜이 {current_count}건 있습니다!")
            for order in orders:
                with st.expander(f"🍔 {order['store_name']} ({order['food_price']}원)"):
                    st.write(f"📍 픽업: {order['store_addr']}")
                    st.write(f"📍 배달: {order['cust_addr']}")
                    
                    if st.button(f"🚀 배차 수락", key=f"btn_{order['id']}"):
                        requests.post(f"{SERVER_URL}/call-rider", json={"order_id": order['id']})
                        st.toast("배차 성공! 안전 운전하세요.")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("현재 대기 중인 콜이 없습니다. (대기 중...)")
            
    else:
        st.error("목록을 불러오지 못했습니다.")

except Exception as e:
    st.error("서버 연결 실패. 잠시 후 다시 시도합니다.")

# ---------------------------------------------------------
# 4. [마법] 3초마다 저절로 새로고침 (레이더 가동)
# ---------------------------------------------------------
time.sleep(2)
st.rerun()