import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="花田喜彘全能 POS", layout="wide")

# --- CSS 樣式 ---
st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}.points-tag{font-size:20px;color:#1D3557;text-align:center;font-weight:bold;}</style>", unsafe_allow_html=True)

# --- 檔案設定 ---
SALES_FILE = "today_sales.csv"
STOCK_FILE = "inventory_settings.csv"

def load_data(file):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# --- 初始化 ---
if 'cart' not in st.session_state: st.session_state.cart = []
history_df = load_data(SALES_FILE)
stock_df = load_data(STOCK_FILE)

product_catalog = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

all_items = []
for cat in product_catalog: all_items.extend(list(product_catalog[cat].keys()))
if stock_df.empty:
    stock_df = pd.DataFrame({"品項": all_items, "初始庫存": 0, "補貨量": 0})
    save_data(stock_df, STOCK_FILE)

def get_remaining_stock(stock_df, history_df):
    stock_map = stock_df.set_index("品項")[["初始庫存", "補貨量"]].sum(axis=1).to_dict()
    if not history_df.empty:
        for _, row in history_df.iterrows():
            try:
                items = eval(row['明細'])
                for itm in items:
                    name = itm.split('] ')[1].split('x')[0]
                    qty = int(itm.split('x')[1])
                    if name in stock_map: stock_map[name] -= qty
            except: pass
    return stock_map

# --- 建立分頁 ---
tab1, tab2, tab3 = st.tabs(["💰 結帳櫃檯", "📦 庫存管理", "📊 業績分析"])

with tab1:
    # 智慧流水號邏輯
    def get_smart_num(history):
        max_n = 0
        if not history.empty:
            for n in history['客戶']:
                if str(n).startswith("現場客 "):
                    try:
                        val = int(n.split("現場客 ")[1])
                        if val > max_n: max_n = val
                    except: pass
        return max_n + 1
    
    next_num = get_smart_num(history_df)
    
    col_n, col_d = st.columns(2)
    with col_n: customer_name = st.text_input("👤 客戶名稱", value=f"現場客 {next_num}")
    with col_d: discount = st.number_input("💸 折扣", min_value=0, value=0, step=5)
    
    st.write("---")
    curr_inv = get_remaining_stock(stock_df, history_df)
    c_cat, c_item, c_qty = st.columns([1, 2, 1])
    with c_cat: category = st.selectbox("📂 分類", list(product_catalog.keys()))
    with c_item:
        item_list = list(product_catalog[category].keys())
        display_list = [f"{i} (餘 {curr_inv.get(i, 0)})" for i in item_list]
        sel_display = st.selectbox("🍎 品項", display_list)
        sel_item = sel_display.split(" (餘")[0]
        rem = curr_inv.get(sel_item, 0)
    with c_qty:
        qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, rem), value=1)
        if rem <= 0: st.error("❌ 售罄")
    
    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True):
        st.session_state.cart.append({"品項": f"[{category[2:4]}] {sel_item}", "單價": product_catalog[category][sel_item], "數量": qty, "小計": product_catalog[category][sel_item]*qty})
    
    st.write("---")
    t_raw = 0
    for i, itm in enumerate(st.session_state.cart):
        ca, cb, cc = st.columns([3, 1, 1])
        ca.write(f"▪️ {itm['品項']}")
        cb.write(f"${itm['單價']} x {itm['數量']}")
        t_raw += itm['小計']
        if cc.button("移除", key=f"del_{i}"): st.session_state.cart.pop(i); st.rerun()
    
    f_total = max(0, t_raw - discount)
    st.markdown(f'<div class="main-price">${f_total:,}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="points-tag">⭐ 本次累積：{f_total//350} 點</div>', unsafe_allow_html=True)

    if st.button("✅ 結帳完成", type="primary", use_container_width=True):
        if st.session_state.cart:
            new_row = {"時間": datetime.now().strftime("%H:%M:%S"), "客戶": customer_name, "明細": str([f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]), "實收": f_total, "小時": datetime.now().hour, "獲得點數": int(f_total//350)}
            history_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(history_df, SALES_FILE)
            st.session_state.cart = []; st.rerun()

    # --- 重要：把紀錄表單加回這裡 ---
    st.write("---")
    if not history_df.empty:
        st.subheader("📊 今日結帳紀錄")
        # 顯示最後 10 筆，最新的在上面
        st.table(history_df[['時間', '客戶', '實收', '獲得點數']].tail(10).iloc[::-1])

with tab2:
    st.subheader("📦 庫存設定")
    edited_df = st.data_editor(stock_df, use_container_width=True, hide_index=True)
    if st.button("💾 儲存庫存"):
        save_data(edited_df, STOCK_FILE)
        st.success("庫存已更新！")
        st.rerun()

with tab3:
    st.subheader("📊 業績圖表分析")
    if not history_df.empty:
        st.metric("今日總營業額", f"${history_df['實收'].sum():,}")
        # 圖表邏輯... (略)
        all_sold = []
        for m in history_df['明細']:
            for item in eval(m):
                name = item.split('] ')[1].split('x')[0]
                q = int(item.split('x')[1])
                all_sold.append({"品項": name, "數量": q})
        sold_df = pd.DataFrame(all_sold).groupby("品項").sum().reset_index()
        fig1 = px.bar(sold_df.sort_values("數量", ascending=False).head(10), x="數量", y="品項", orientation='h', title="🏆 Top 10 熱銷商品")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.write("---")
        csv_data = history_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載完整報表 (CSV)", data=csv_data, file_name=f"花田報表_{datetime.now().strftime('%m%d')}.csv", use_container_width=True)
        
        if st.button("⚠️ 收攤清空所有資料"):
            if os.path.exists(SALES_FILE): os.remove(SALES_FILE)
            if os.path.exists(STOCK_FILE): os.remove(STOCK_FILE)
            st.rerun()
