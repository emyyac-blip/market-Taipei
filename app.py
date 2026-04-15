import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="花田喜彘 POS 庫存版", layout="wide")

# CSS 樣式加強
st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}.stock-low{color:orange;font-weight:bold;}.stock-out{color:red;font-weight:bold;}</style>", unsafe_allow_html=True)

DATA_FILE = "today_sales.csv"

# --- 1. 設定今日開市庫存 (請在這裡修改每天帶去的數量) ---
# 您可以根據當天載貨狀況調整這些數字
stock_initial = {
    "梅花薄片(1.5 mm)": 20, "梅花厚片(6mm)": 15, "里肌薄片(1.5 mm)": 10,
    "黑豬梅花薄片(1.5 mm)": 25, "黑豬五花薄片(1.5 mm)": 20, "黑豬梅花排骨": 12,
    "原味貢丸": 30, "黑豬高麗菜水餃": 15, "花田純肉鬆": 10
    # ... 其他品項若未列出，預設會是 99 (無限)
}

def load_history():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE).to_dict('records')
        except: return []
    return []

def save_history(history_list):
    pd.DataFrame(history_list).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state: st.session_state.history = load_history()

# --- 2. 智慧流水號與庫存計算 ---
def get_current_stock():
    current_stock = stock_initial.copy()
    for record in st.session_state.history:
        # 解析明細中的數量並扣除
        try:
            items = eval(record['明細'])
            for item in items:
                name = item.split('] ')[1].split('x')[0]
                qty = int(item.split('x')[1])
                if name in current_stock:
                    current_stock[name] -= qty
                else:
                    current_stock[name] = 99 - qty
        except: pass
    return current_stock

current_inventory = get_current_stock()

def get_next_guest_num(history):
    max_num = 0
    for record in history:
        name = str(record.get('客戶', ''))
        if name.startswith("現場客 "):
            try:
                num_part = int(name.split("現場客 ")[1]); 
                if num_part > max_num: max_num = num_part
            except: pass
    return max_num + 1

next_num = get_next_guest_num(st.session_state.history)
default_name = f"現場客 {next_num}"

# 商品清單 (2026.04)
product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

st.title("🛒 花田喜彘 - 庫存監控 POS")

c1, c2 = st.columns(2)
with c1: customer_name = st.text_input("👤 客戶名稱", value=default_name)
with c2: discount = st.number_input("💸 折扣", min_value=0, value=0, step=5)

st.write("---")
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_a: category = st.selectbox("📂 分類", list(product_catalog.keys()))
with col_b:
    item_list = list(product_catalog[category].keys())
    # 在下拉選單顯示庫存狀況
    display_list = []
    for item in item_list:
        rem = current_inventory.get(item, 99)
        display_list.append(f"{item} (餘 {rem})")
    
    selected_display = st.selectbox("🍎 品項", display_list)
    selected_item = selected_display.split(" (餘")[0]
    unit_price = product_catalog[category][selected_item]
    remaining = current_inventory.get(selected_item, 99)

with col_c:
    qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, remaining), value=1)
    if remaining <= 0: st.error("❌ 已售罄")
    elif remaining <= 5: st.warning(f"⚠️ 僅剩 {remaining} 包")

if st.button("➕ 加入清單", disabled=(remaining <= 0), use_container_width=True):
    st.session_state.cart.append({"品項": f"[{category[2:4]}] {selected_item}", "單價": unit_price, "數量": qty, "小計": unit_price * qty})

# (中間購物車與結帳邏輯維持不變...)
st.write("---")
total_raw = 0
if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        ca, cb, cc = st.columns([3, 1, 1])
        ca.write(f"▪️ {item['品項']}")
        cb.write(f"${item['單價']} x {item['數量']}")
        total_raw += item['小計']
        if cc.button("移除", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()

final_total = max(0, total_raw - discount)
st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)

if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
    if st.session_state.cart:
        items_msg = [f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]
        order_info = {"時間": datetime.now().strftime("%H:%M:%S"), "客戶": customer_name, "明細": str(items_msg), "實收": final_total, "獲得點數": int(final_total // 350)}
        st.session_state.history.append(order_info)
        save_history(st.session_state.history)
        st.session_state.cart = []; st.rerun()

# 報表與清空按鈕... (維持原樣)
