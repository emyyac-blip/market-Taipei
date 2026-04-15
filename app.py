import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 頁面設定
st.set_page_config(page_title="花田喜彘 POS 流水號版", layout="wide")

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
    .points-tag {
        font-size: 24px;
        color: #1D3557;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料存檔設定
DATA_FILE = "today_sales.csv"

def load_history():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE).to_dict('records')
        except: return []
    return []

def save_history(history_list):
    pd.DataFrame(history_list).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 初始化資料
if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state: st.session_state.history = load_history()

# 💡 計算自動流水號：看今天歷史紀錄有幾筆，下一筆就是 n+1
next_guest_number = len(st.session_state.history) + 1
default_name = f"現場客 {next_guest_number}"

# 3. 商品資料庫 (2026.04 希望廣場版)
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
        "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215,
        "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270,
        "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140
    },
    "🌭 加工品系列": {
        "黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290
    }
}

st.title("🛒 花田喜彘 - 高效率流水號 POS")

# --- 結帳區域 ---
c_name, c_disc = st.columns(2)
with c_name:
    # 這裡會自動填入 現場客X，但也可以手動改掉
    customer_name = st.text_input("👤 客人名稱/手機", value=default_name)
with c_disc:
    discount = st.number_input("💸 折扣金額", min_value=0, value=0, step=5)

st.write("---")
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
    st.session_state.cart.append({"品項": f"[{category[2:4]}] {selected_item}", "單價": unit_price, "數量": qty, "小計": unit_price * qty})

st.write("---")
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

# 點數規則：每 350 元 1 點
final_total = max(0, total_raw - discount)
earned_points = final_total // 350

st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="points-tag">⭐ 本次可累積：{int(earned_points)} 點</div>', unsafe_allow_html=True)

if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
    if st.session_state.cart:
        items_summary = [f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]
        order_info = {
            "單號": next_guest_number,
            "時間": datetime.now().strftime("%H:%M:%S"),
            "客戶": customer_name,
            "明細": str(items_summary),
            "實收": final_total,
            "獲得點數": int(earned_points)
        }
        st.session_state.history.append(order_info)
        save_history(st.session_state.history)
        st.session_
