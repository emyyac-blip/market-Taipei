import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="花田喜彘 POS 4.3.1", layout="wide")

st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}.stock-info{font-size:16px;color:#457B9D;font-weight:bold;}</style>", unsafe_allow_html=True)

SALES_FILE, STOCK_FILE = "today_sales.csv", "stock_master.csv"

def load_stock():
    if os.path.exists(STOCK_FILE):
        try: return pd.read_csv(STOCK_FILE).set_index('品項')['庫存'].to_dict()
        except: return {}
    return {}

def save_stock(stock_dict):
    pd.DataFrame(list(stock_dict.items()), columns=['品項', '庫存']).to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state:
    if os.path.exists(SALES_FILE):
        try: st.session_state.history = pd.read_csv(SALES_FILE).to_dict('records')
        except: st.session_state.history = []
    else: st.session_state.history = []
if 'inventory' not in st.session_state: st.session_state.inventory = load_stock()

def get_next_num(history):
    max_n = 0
    for r in history:
        name = str(r.get('客戶', ''))
        if "現場客 " in name:
            try:
                n = int(name.split("現場客 ")[1])
                if n > max_n: max_n = n
            except: pass
    return max_n + 1

next_num = get_next_num(st.session_state.history)

# --- 關鍵：四大分頁主程式 ---
t1, t2, t3, t4 = st.tabs(["🏠 現場結帳", "📋 訂單明細", "📊 業績總覽", "📦 庫存管理"])

with t1:
    st.title("花田喜彘 - 智慧結帳")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: cust_name = st.text_input("👤 客人名稱", value=f"現場客 {next_num}", key="k1")
    with c2: pay_m = st.selectbox("💳 支付", ["現金", "Line Pay", "轉帳"], key="k2")
    with c3: disc = st.number_input("💸 折扣", min_value=0, value=0, step=5, key="k3")
    with c4: is_p = st.toggle("⭐ 累積點數", value=True, key="k4")
    st.write("---")
    cola, colb, colc = st.columns([1, 2, 1])
    with cola: cat = st.selectbox("📂 分類", list(product_catalog.keys()), key="k5")
    with colb:
        items = list(product_catalog[cat].keys())
        sel_i = st.selectbox("🍎 品項", items, key="k6")
        price = product_catalog[cat][sel_i]
        rem = st.session_state.inventory.get(sel_i, 0)
        st.markdown(f"<div class='stock-info'>現場庫存：{int(rem)} 包</div>", unsafe_allow_html=True)
    with colc: qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, int(rem)), value=1, key="k7")
    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True):
        st.session_state.cart.append({"品項": sel_i, "單價": price, "數量": qty, "小計": price * qty})
    st.write("---")
    total_r = 0
    for i,
