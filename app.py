import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 頁面設定
st.set_page_config(page_title="花田喜彘 POS 4.1", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

SALES_FILE = "today_sales.csv"
STOCK_FILE = "stock_master.csv"

# --- 資料核心處理 ---
def load_stock():
    if os.path.exists(STOCK_FILE):
        return pd.read_csv(STOCK_FILE).set_index('品項')['庫存'].to_dict()
    return {"黑豬梅花薄片(1.5 mm)": 20, "黑豬五花薄片(1.5 mm)": 20}

def save_stock(stock_dict):
    pd.DataFrame(list(stock_dict.items()), columns=['品項', '庫存']).to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 初始化
if 'cart' not in st.session_state: st.session_state.cart = []
if 'history' not in st.session_state:
    if os.path.exists(SALES_FILE):
        try: st.session_state.history = pd.read_csv(SALES_FILE).to_dict('records')
        except: st.session_state.history = []
    else: st.session_state.history = []
if 'inventory' not in st.session_state: st.session_state.inventory = load_stock()

# 流水號邏輯
def get_next_num(history):
    max_n = 0
    for r in history:
        name = str(r.get('客戶', ''))
        if name.startswith("現場客 "):
            try:
                n = int(name.split(" ")[1])
                if n > max_n: max_n = n
            except: pass
    return max_n + 1

next_num = get_next_num(st.session_state.history)

# 2026.04 希望廣場商品清單
product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

# --- 分頁導覽設定 ---
tab1, tab2 = st.tabs(["🏠 現場結帳", "📦 庫存存摺"])

with tab1:
    st.title("花田喜彘 - 智慧結帳")
    
    # 結帳資訊列
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: cust_name = st.text_input("👤 客戶名稱", value=f"現場客 {next_num}")
    with c2: pay_method = st.selectbox("💳 支付", ["現金", "Line Pay", "轉帳"])
    with c3: discount = st.number_input("💸 折扣", min_value=0, value=0, step=5)
    with c4: is_point = st.toggle("⭐ 累積點數", value=True)

    st.write("---")

    # 點單區
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a: cat = st.selectbox("📂 分類", list(product_catalog.keys()))
    with col_b:
        items = list(product_catalog[cat].keys())
        sel_item = st.selectbox("🍎 品項", items)
        price = product_catalog[cat][sel_item]
        rem = st.session_state.inventory.get(sel_item, 0)
        st.markdown(f"<div class='stock-info'>現場庫存：{rem} 包</div>", unsafe_allow_html=True)
    with col_c: qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, int(rem)), value=1)

    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True):
        st.session_state.cart.append({"品項": sel_item, "單價": price, "數量": qty, "小計": price * qty})

    st.write("---")
    total_raw = 0
    for i, item in enumerate(st.session_state.cart):
        ca, cb, cc = st.columns([3, 1, 1])
        ca.write(f"▪️ {item['品項']}")
        cb.write(f"${item['單價']} x {item['數量']}")
        total_raw += item['小計']
        if cc.button("移除", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()

    final_total = max(0, total_raw - discount)
    earned_points = (final_total // 350) if is_point else 0

    st.markdown(f'<div class="main-price">${final_total:,}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:20px;'>⭐ 本次累積：{int(earned_points)} 點 (支付：{pay_method})</p>", unsafe_allow_html=True)

    if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True):
        if st.session_state.cart:
            for item in st.session_state.cart:
                name = item['品項']
                if name in st.session_state.inventory: st.session_state.inventory[name] -= item['數量']
            save_stock(st.session_state.inventory)
            summary = [f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]
            st.session_state.history.append({
                "時間": datetime.now().strftime("%H:%M:%S"),
                "客戶": cust_name, "明細": str(summary), "實收": final_total, 
                "支付": pay_method, "點數": int(earned_points)
            })
            pd.DataFrame(st.session_state.history).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
            st.session_state.cart = []; st.rerun()

    st.write("---")
    if st.session_state.history:
        df_h = pd.DataFrame(st.session_state.history)
        st.table(df_h)
        cd, cl = st.columns(2)
        with cd: st.download_button("📥 下載業績", data=df_h.to_csv(index=False).encode('utf-8-sig'), file_name="今日業績.csv", use_container_width=True)
        with cl:
            if st.button("⚠️ 收攤清空業績 (不傷庫存)", use_container_width=True):
                if os.path.exists(SALES_FILE): os.remove(SALES_FILE)
                st.session_state.history = []; st.rerun()

with tab2:
    st.title("📦 庫存存摺管理")
    st.write("在這裡您可以進行每日進貨或盤點校正。")
    
    # 全部品項清單
    all_p = []
    for c_i in product_catalog.values(): all_p.extend(list(c_i.keys()))
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s_item = st.selectbox("選擇要調整的商品", sorted(all_p))
        s_curr = st.session_state.inventory.get(s_item, 0)
        st.metric("目前庫存", f"{int(s_curr)} 包")
    with col_s2:
        s_new = st.number_input("輸入正確數量 (進貨後總數)", value=int(s_curr))
        if st.button("💾 確認更新庫存"):
            st.session_state.inventory[s_item] = s_new
            save_stock(st.session_state.inventory)
            st.success(f"{s_item} 已更新為 {s_new} 包！")
            st.rerun()
    
    st.write("---")
    st.subheader("📋 全品項即時庫存表")
    stock_df = pd.DataFrame(list(st.session_state.inventory.items()), columns=['品項', '庫存數量'])
    st.dataframe(stock_df.sort_values(by='庫存數量'), use_container_width=True)
