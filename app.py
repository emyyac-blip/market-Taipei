import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 頁面設定
st.set_page_config(page_title="花田喜彘 POS 4.3", layout="wide")

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
    .stock-info {
        font-size: 16px;
        color: #457B9D;
        font-weight: bold;
    }
    .stNumberInput div div input {
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

SALES_FILE = "today_sales.csv"
STOCK_FILE = "stock_master.csv"

# --- 資料核心處理 ---
def load_stock():
    if os.path.exists(STOCK_FILE):
        try: return pd.read_csv(STOCK_FILE).set_index('品項')['庫存'].to_dict()
        except: return {}
    return {}

def save_stock(stock_dict):
    pd.DataFrame(list(stock_dict.items()), columns=['品項', '庫存']).to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 商品清單 (供系統參考)
product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

# 初始化狀態
if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state:
    if os.path.exists(SALES_FILE):
        try: st.session_state.history = pd.read_csv(SALES_FILE).to_dict('records')
        except: st.session_state.history = []
    else: st.session_state.history = []
if 'inventory' not in st.session_state: st.session_state.inventory = load_stock()

# 流水號
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

# --- 四大分頁 ---
t1, t2, t3, t4 = st.tabs(["🏠 現場結帳", "📋 訂單明細", "📊 業績總覽", "📦 庫存管理"])

# --- TAB 1：現場結帳 (維持不變) ---
with t1:
    st.title("花田喜彘 - 智慧結帳")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: cust_name = st.text_input("👤 客人名稱", value=f"現場客 {next_num}", key="pos_name")
    with c2: pay_method = st.selectbox("💳 支付", ["現金", "Line Pay", "轉帳"])
    with c3: discount = st.number_input("💸 折扣", min_value=0, value=0, step=5)
    with c4: is_point = st.toggle("⭐ 累積點數", value=True)

    st.write("---")
    cola, colb, colc = st.columns([1, 2, 1])
    with cola: cat = st.selectbox("📂 分類", list(product_catalog.keys()))
    with colb:
        items = list(product_catalog[cat].keys())
        sel_item = st.selectbox("🍎 品項", items)
        price = product_catalog[cat][sel_item]
        rem = st.session_state.inventory.get(sel_item, 0)
        st.markdown(f"<div class='stock-info'>現場庫存：{int(rem)} 包</div>", unsafe_allow_html=True)
    with colc: qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, int(rem)), value=1)

    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True):
        st.session_state.cart.append({"品項": sel_item, "單價": price, "數量": qty, "小計": price * qty})

    st.write("---")
    total_raw = 0
    for i, item in enumerate(st.session_state.cart):
        ca, cb, cc = st.columns([3, 1, 1])
        ca.write(f"▪️ {item['品項']} (${item['單價']}x{item['數量']})")
        total_raw += item['小計']
        if cc.button("移除", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()

    final_total = max(0, total_raw - discount)
    pts = (final_total // 350) if is_point else 0

    st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:20px;'>⭐ 本次累積：{int(pts)} 點 (支付：{pay_method})</p>", unsafe_allow_html=True)

    if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
        if st.session_state.cart:
            for item in st.session_state.cart:
                n = item['品項']
                if n in st.session_state.inventory: st.session_state.inventory[n] -= item['數量']
            save_stock(st.session_state.inventory)
            summary = [f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]
            st.session_state.history.append({"時間": datetime.now().strftime("%H:%M:%S"), "客戶": cust_name, "明細": str(summary), "實收": final_total, "支付": pay_method, "點數": int(pts)})
            pd.DataFrame(st.session_state.history).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
            st.session_state.cart = []; st.rerun()

# --- TAB 2：訂單明細 (維持不
