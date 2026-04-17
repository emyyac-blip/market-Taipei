import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 頁面基本設定
st.set_page_config(page_title="花田喜彘 POS 4.3.4", layout="wide")

st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}.stock-info{font-size:16px;color:#457B9D;font-weight:bold;}</style>", unsafe_allow_html=True)

SALES_FILE, STOCK_FILE = "today_sales.csv", "stock_master.csv"

# --- 資料讀取與儲存 ---
def load_stock():
    if os.path.exists(STOCK_FILE):
        try: return pd.read_csv(STOCK_FILE).set_index('品項')['庫存'].to_dict()
        except: return {}
    return {}

def save_stock(stock_dict):
    pd.DataFrame(list(stock_dict.items()), columns=['品項', '庫存']).to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 2026.04 希望廣場清單
product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230,"黑豬腩排": 315, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
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

# 流水號邏輯
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

# TAB 1：結帳
with t1:
    st.title("花田喜彘 - 智慧結帳")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: cust_name = st.text_input("👤 客人名稱", value=f"現場客 {next_num}", key="k_name_v434")
    with c2: pay_m = st.selectbox("💳 支付", ["現金", "Line Pay"], key="k_pay_v434")
    with c3: disc = st.number_input("💸 折扣", min_value=0, value=0, step=5, key="k_disc_v434")
    with c4: is_p = st.toggle("⭐ 累積點數", value=True, key="k_pts_v434")
    st.write("---")
    cola, colb, colc = st.columns([1, 2, 1])
    with cola: cat = st.selectbox("📂 分類", list(product_catalog.keys()), key="k_cat_v434")
    with colb:
        items = list(product_catalog[cat].keys())
        sel_i = st.selectbox("🍎 品項", items, key="k_item_v434")
        price = product_catalog[cat][sel_i]
        rem = st.session_state.inventory.get(sel_i, 0)
        st.markdown(f"<div class='stock-info'>現場庫存：{int(rem)} 包</div>", unsafe_allow_html=True)
    with colc: qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, int(rem)), value=1, key="k_qty_v434")
    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True, key="k_add_v434"):
        st.session_state.cart.append({"品項": sel_i, "單價": price, "數量": qty, "小計": price * qty})
    st.write("---")
    total_r = 0
    for i, itm in enumerate(st.session_state.cart):
        ca, cb, cc = st.columns([3, 1, 1])
        ca.write(f"▪️ {itm['品項']} (${itm['單價']}x{itm['數量']})")
        total_r += itm['小計']
        if cc.button("移除", key=f"del_{i}_v434"): st.session_state.cart.pop(i); st.rerun()
    f_total = max(0, total_r - disc)
    pts_calc = (f_total // 350) if is_p else 0
    st.markdown(f'<div class="main-price">${f_total:,}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:20px;'>⭐ 本次累積：{int(pts_calc)} 點 (支付：{pay_m})</p>", unsafe_allow_html=True)
    if st.button("✅ 結帳完成 / 下一單", type="primary", use_container_width=True, key="k_chk_v434"):
        if st.session_state.cart:
            for itm in st.session_state.cart:
                n = itm['品項']
                if n in st.session_state.inventory: st.session_state.inventory[n] -= itm['數量']
            save_stock(st.session_state.inventory)
            summary = [f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]
            st.session_state.history.append({"時間": datetime.now().strftime("%H:%M:%S"), "客戶": cust_name, "明細": str(summary), "實收": f_total, "支付": pay_m, "點數": int(pts_calc)})
            pd.DataFrame(st.session_state.history).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
            st.session_state.cart = []; st.rerun()

# TAB 2：明細
with t2:
    st.title("📋 今日訂單清單")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        st.table(df_history)
        st.download_button("📥 下載 Excel 報表", data=df_history.to_csv(index=False).encode('utf-8-sig'), file_name="今日報表.csv", use_container_width=True, key="k_dl_v434")
    else: st.info("目前尚無成交紀錄")

# TAB 3：業績總覽 (修正處)
with t3:
    st.title("📊 今日業績統計")
    if st.session_state.history:
        df_stats = pd.DataFrame(st.session_state.history) # 確保定義了 df_stats
        st.metric("今日總營業額", f"${df_stats['實收'].sum():,}")
        st.write("---")
        for m in ["現金", "Line Pay", "轉帳"]:
            m_sum = df_stats[df_stats['支付'] == m]['實收'].sum()
            st.write(f"▪️ {m}: ${m_sum:,}")
        if st.button("⚠️ 收攤清空業績 (不傷庫存)", use_container_width=True, key="k_clr_v434"):
            if os.path.exists(SALES_FILE): os.remove(SALES_FILE)
            st.session_state.history = []; st.rerun()
    else: st.info("尚無數據")

# TAB 4：庫存盤點 (全清單版)
with t4:
    st.title("📦 庫存快速盤點")
    new_inv = st.session_state.inventory.copy()
    all_list = []
    for cn, ci in product_catalog.items():
        for iname in ci.keys(): all_list.append({"分類": cn, "品項": iname})
    l_col, r_col = st.columns(2)
    for idx, row in enumerate(all_list):
        target = l_col if idx % 2 == 0 else r_col
        with target:
            u_key = f"st_in_{row['分類']}_{row['品項']}_v434"
            v = st.number_input(f"{row['分類']}-{row['品項']}", value=int(st.session_state.inventory.get(row['品項'], 0)), key=u_key)
            new_inv[row['品項']] = v
    if st.button("💾 一鍵儲存所有庫存", type="primary", use_container_width=True, key="k_sv_v434"):
        st.session_state.inventory = new_inv
        save_stock(st.session_state.inventory)
        st.success("✅ 庫存已同步！"); st.rerun()
