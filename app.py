import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="花田喜彘全能 POS", layout="wide")
st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}.points-tag{font-size:20px;color:#1D3557;text-align:center;font-weight:bold;}</style>", unsafe_allow_html=True)

S_FILE, K_FILE = "today_sales.csv", "inventory_settings.csv"

def load_df(f):
    if os.path.exists(f):
        try:
            df = pd.read_csv(f)
            if f == S_FILE and not df.empty:
                for c in ['獲得點數', '小時']:
                    if c not in df.columns: df[c] = 0
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

if 'cart' not in st.session_state: st.session_state.cart = []
h_df = load_df(S_FILE)
k_df = load_df(K_FILE)

cat_data = {
    "🐷 白豬系列": {"梅花薄片(1.5 mm)": 175, "梅花厚片(6mm)": 175, "里肌薄片(1.5 mm)": 170, "里肌厚片(6 mm)": 170, "五花薄片(1.5 mm)": 195, "老鼠肉(後腿心)": 165, "小里肌(腰內肉)": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿(特別版3支入)": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬系列": {"黑豬梅花薄片(1.5 mm)": 198, "黑豬梅花厚片(6mm)": 198, "黑豬里肌薄片(1.5 mm)": 180, "黑豬里肌厚片(6 mm)": 180, "黑豬五花薄片(1.5 mm)": 215, "黑豬五花厚片(6 mm)": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花肉條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工品系列": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

all_i = []
for c in cat_data: all_i.extend(list(cat_data[c].keys()))
if k_df.empty:
    k_df = pd.DataFrame({"品項": all_i, "初始庫存": 0, "補貨量": 0})
    k_df.to_csv(K_FILE, index=False)

def get_stock(kd, hd):
    m = kd.set_index("品項")[["初始庫存", "補貨量"]].sum(axis=1).to_dict()
    if not hd.empty:
        for _, r in hd.iterrows():
            try:
                for itm in eval(r['明細']):
                    n = itm.split('] ')[1].split('x')[0]
                    if n in m: m[n] -= int(itm.split('x')[1])
            except: pass
    return m

t1, t2, t3 = st.tabs(["💰 結帳", "📦 庫存", "📊 分析"])

with t1:
    m_n = 0
    if not h_df.empty:
        for n in h_df['客戶']:
            if str(n).startswith("現場客 "):
                try:
                    v = int(n.split("現場客 ")[1])
                    if v > m_n: m_n = v
                except: pass
    
    cur_i = get_stock(k_df, h_df)
    c1, c2 = st.columns(2)
    with c1: c_name = st.text_input("👤 客戶", value=f"現場客 {m_n+1}")
    with c2: dsc = st.number_input("💸 折扣", min_value=0, step=5)
    
    st.write("---")
    ca, cb, cc = st.columns([1, 2, 1])
    with ca: cat = st.selectbox("📂 分類", list(cat_data.keys()))
    with cb:
        i_l = [f"{i} (餘 {cur_i.get(i, 0)})" for i in cat_data[cat].keys()]
        sel = st.selectbox("🍎 品項", i_l).split(" (餘")[0]
        rem = cur_i.get(sel, 0)
    with cc: qty = st.number_input("🔢 數量", min_value=1, max_value=max(1, rem))

    if st.button("➕ 加入清單", disabled=(rem <= 0), use_container_width=True):
        st.session_state.cart.append({"品項": f"[{cat[2:4]}] {sel}", "單價": cat_data[cat][sel], "數量": qty, "小計": cat_data[cat][sel]*qty})
    
    st.write("---")
    tr = 0
    for i, itm in enumerate(st.session_state.cart):
        c_a, c_b, c_c = st.columns([3, 1, 1])
        c_a.write(f"▪️ {itm['品項']}")
        c_b.write(f"${itm['單價']}x{itm['數量']}")
        tr += itm['小計']
        if c_c.button("移除", key=f"d_{i}"): st.session_state.cart.pop(i); st.rerun()
    
    ft = max(0, tr - dsc)
    st.markdown(f'<div class="main-price">${ft:,}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="points-tag">⭐ 點數：{ft//350}</div>', unsafe_allow_html=True)

    if st.button("✅ 結帳完成", type="primary", use_container_width=True):
        if st.session_state.cart:
            new_r = pd.DataFrame([{"時間": datetime.now().strftime("%H:%M:%S"), "客戶": c_name, "明細": str([f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]), "實收": ft, "小時": datetime.now().hour, "獲得點數": int(ft//350)}])
            h_df = pd.concat([h_df, new_r], ignore_index=True)
            h_df.to_csv(S_FILE, index=False, encoding='utf-8-sig')
            st.session_state.cart = []; st.rerun()

    st.write("---")
    if not h_df.empty:
        st.table(h_df[['時間', '客戶', '實收', '獲得點數']].tail(10).iloc[::-1])

with t2:
    st.subheader("📦 庫存設定")
    ed = st.data_editor(k_df, use_container_width=True, hide_index=True)
    if st.button("💾 儲存"): ed.to_csv(K_FILE, index=False); st.rerun()

with t3:
    st.subheader("📊 業績分析")
    if not h_df.empty:
        st.metric("總營收", f"${h_df['實收'].sum():,}")
        als = []
        for m in h_df['明細']:
            for it in eval(m): als.append({"品項": it.split('] ')[1].split('x')[0], "數量": int(it.split('x')[1])})
        sdf = pd.DataFrame(als).groupby("品項").sum().reset_index()
        st.plotly_chart(px.bar(sdf.sort_values("數量", ascending=False).head(10), x="數量", y="品項", orientation='h'), use_container_width=True)
        if st.button("⚠️ 清空資料"):
            if os.path.exists(S_FILE): os.remove(S_
