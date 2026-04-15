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
    .stSelectbox label {
        font-size: 18px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 雲端資料檔案
DATA_FILE = "today_sales.csv"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE).to_dict('records')
        except:
            return []
    return []

def save_history(history_list):
    df = pd.DataFrame(history_list)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 初始化記憶體
if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state: st.session_state.history = load_history()

# === 根據您的 CSV 更新商品資料庫 ===
product_catalog = {
    "🐷 白豬系列": {
        "梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170,
        "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165,
        "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240,
        "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285,
        "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250,
        "豬肉絲": 130, "豬絞肉": 130
    },
    "🐗 黑豬系列": {
        "黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180,
        "黑豬里肌厚片(6 mm)": 180, "黑豬五五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215,
        "黑豬龍骨": 118, "黑豬梅花排骨": 215, "黑豬老鼠肉": 165, "黑豬松坂肉": 395
    },
    "🌭 加工品系列": {
        "原味貢丸": 140, "香菇貢丸": 155, "噴水肉丸": 160, "原味香腸": 160,
        "黑胡椒香腸": 160, "蒜味香腸": 160, "馬告香腸": 190, "鹹豬肉": 170,
        "培根 slice": 195, "原味肉鬆": 195, "海苔肉鬆": 195, "黑豬肉乾": 180
    }
}

st.title("🛒 花田喜彘 - 希望廣場 POS 3.3")

# 1. 客戶資訊
c_name, c_disc = st.columns(2)
with c_name:
    customer_name = st.text_input("👤 客人名稱", value="現場客")
with c_disc:
    discount = st.number_input("💸 折扣金額", min_value=0, value=0, step=5)

st.write("---")

# 2. 分類點單區
col_cat, col_item, col_qty = st.columns([1, 2, 1])

with col_cat:
    category = st.selectbox("📂 分類", list(product_catalog.keys()))

with col_item:
    item_options = list(product_catalog[category].keys())
    selected_item = st.selectbox("🍎 品項", item_options)
    unit_price = product_catalog[category][selected_item]

with col_qty:
    qty = st.number_input("🔢 數量", min_value=1, value=1)
    st.write(f"單價: ${unit_price}")

if st.button("➕ 加入清單", use_container_width=True):
    st.session_state.cart.append({
        "品項": f"[{category[2:4]}] {selected_item}",
        "單價": unit_price,
        "數量": qty,
        "小計": unit_price * qty
    })

st.write("---")

# 3. 購物車顯示
total_raw = 0
if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"▪️ {item['品項']}")
        c2.write(f"${item['單價']} x {item['數量']}")
        total_raw += item['小計']
        if c3.button("移除", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

# 4. 總額計算
final_total = max(0, total_raw - discount)
st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)

# 5. 結帳與存檔
if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
    if st.session_state.cart:
        order_info = {
            "時間": datetime.now().strftime("%H:%M:%S"),
            "客戶": customer_name,
            "明細": str([f"{
