import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定 iPad 滿版模式
st.set_page_config(page_title="花田喜彘結帳系統", layout="wide")

# 自訂 CSS
st.markdown("""
    <style>
    .main-price {
        font-size: 70px !important;
        font-weight: bold;
        color: #E63946;
        text-align: center;
        background-color: #F1FAEE;
        padding: 15px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 雲端硬碟檔案名稱 (這招可以抵抗 iPad 重新整理)
DATA_FILE = "today_sales.csv"

# 讀取雲端硬碟的歷史紀錄
def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict('records')
    return []

# 存入雲端硬碟
def save_history(history_list):
    df = pd.DataFrame(history_list)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 1. 初始化記憶體
if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state: st.session_state.history = load_history()

# 2. 商品資料庫
products = {
    "黑豬梅花薄片 (200g)": 198, "黑豬梅花厚片 (200g)": 198,
    "黑豬里肌薄片 (200g)": 180, "黑豬里肌厚片 (200g)": 180,
    "黑豬五花薄片 (200g)": 215, "黑豬五花厚片 (200g)": 215,
    "黑豬龍骨 (300g)": 118, "黑豬梅花排骨 (300g)": 215,
    "老鼠肉 (220g)": 165, "黑豬原味貢丸": 140, "黑豬香菇貢丸": 155
}

st.title("🛒 花田喜彘 - 市集 POS 3.2 不斷線版")

# 3. 輸入區
c_name, c_disc = st.columns(2)
with c_name: customer_name = st.text_input("👤 客人名稱", value="現場客")
with c_disc: discount = st.number_input("💸 折扣金額", min_value=0, value=0)

st.write("---")

col1, col2, col3 = st.columns([2, 1, 1])
with col1: selected_item = st.selectbox("🍎 選擇品項", list(products.keys()))
with col2: qty = st.number_input("🔢 數量", min_value=1, value=1)
with col3:
    st.write(""); st.write("")
    if st.button("➕ 加入清單", use_container_width=True):
        st.session_state.cart.append({
            "品項": selected_item, "單價": products[selected_item],
            "數量": qty, "小計": products[selected_item] * qty
        })

# 4. 顯示購物車
total_raw = 0
for item in st.session_state.cart:
    total_raw += item['小計']
    st.write(f"▪️ {item['品項']} x {item['數量']} = ${item['小計']}")

# 5. 總金額
final_total = max(0, total_raw - discount)
st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)

# 6. 結帳與自動備份到雲端硬碟
if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
    if st.session_state.cart:
        order_info = {
            "時間": datetime.now().strftime("%H:%M:%S"),
            "客戶": customer_name,
            "品項明細": str([f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]),
            "原價": total_raw,
            "折扣": discount,
            "實收": final_total
        }
        st.session_state.history.append(order_info)
        save_history(st.session_state.history) # 關鍵：馬上寫入硬碟
        st.session_state.cart = [] # 清空上方購物車
        st.rerun()

st.write("---")

# 7. 今日戰報與收攤管理
if st.session_state.history:
    st.subheader("📊 今日已結帳紀錄")
    df = pd.DataFrame(st.session_state.history)
    st.table(df)
    
    # 底部兩顆大按鈕：下載 與 清空
    c_down, c_clear = st.columns(2)
    with c_down:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 1. 下載今日報表 (Excel)", data=csv, file_name=f"花田喜彘_{datetime.now().strftime('%m%d')}_報表.csv", mime="text/csv", use_container_width=True)
    with c_clear:
        if st.button("⚠️ 2. 收攤清空今日紀錄", use_container_width=True):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE) # 刪除硬碟裡的檔案
            st.session_state.history = []
            st.rerun()
