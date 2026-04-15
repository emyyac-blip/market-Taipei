import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="花田 POS", layout="wide")
st.markdown("<style>.main-price{font-size:70px!important;font-weight:bold;color:#E63946;text-align:center;background-color:#F1FAEE;padding:15px;border-radius:15px;}</style>", unsafe_allow_html=True)

# 檔案設定
S_F, K_F = "sales.csv", "stock.csv"

def get_df(f):
    if os.path.exists(f):
        try:
            df = pd.read_csv(f)
            # 💡 這裡會自動清理舊欄位，防止紅字報錯
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

# 初始化
if 'cart' not in st.session_state: st.session_state.cart = []
h_df, k_df = get_df(S_F), get_df(K_F)

# 品項與價格
menu = {
    "🐷 白豬": {"梅花薄片": 175, "梅花厚片": 175, "里肌薄片": 170, "里肌厚片": 170, "五花薄片": 195, "老鼠肉": 165, "小里肌": 175, "霜降肉": 245, "松坂肉": 360, "梅花肉丁": 240, "龍骨": 109, "尾冬骨": 160, "梅花排骨": 210, "小戰斧": 285, "棒棒腿": 220, "德國豬腳": 252, "月亮軟骨": 250, "豬肉絲": 130, "豬絞肉": 130},
    "🐗 黑豬": {"黑豬梅花薄片": 198, "黑豬梅花厚片": 198, "黑豬里肌薄片": 180, "黑豬里肌厚片": 180, "黑豬五花薄片": 215, "黑豬五花厚片": 215, "黑豬龍骨": 118, "黑豬梅花排骨": 230, "黑豬帶皮五花條": 265, "黑豬豬腳": 270, "黑豬小里肌": 190, "黑豬霜降肉": 285, "黑豬松坂肉": 390, "黑豬豬肉絲": 140, "黑豬豬絞肉": 140},
    "🌭 加工": {"黑豬高麗菜水餃": 239, "黑豬筊白筍水餃": 219, "花田純肉鬆": 260, "花田寶寶肉鬆": 290}
}

all_i = []
for c in menu: all_i.extend(list(menu[c].keys()))
if k_df.empty: k_df = pd.DataFrame({"品項":all_i, "初始":0, "補貨":0})

def cur_s(kd, hd):
    m = kd.set_index("品項")[["初始", "補貨"]].sum(axis=1).to_dict()
    if not hd.empty:
        for _, r in hd.iterrows():
            try:
                for it in eval(r['明細']):
                    n = it.split('] ')[1].split('x')[0]
                    if n in m: m[n] -= int(it.split('x')[1])
            except: pass
    return m

t1, t2, t3 = st.tabs(["💰 結帳", "📦 庫存", "📊 分析"])

with t1:
    m_n = 0
    if not h_df.empty and '客戶' in h_df.columns:
        for n in h_df['客戶']:
            if "現場客 " in str(n):
                try: m_n = max(m_n, int(n.split("現場客 ")[1]))
                except: pass
    st_m = cur_s(k_df, h_df)
    c1, c2 = st.columns(2)
    with c1: c_n = st.text_input("👤 客戶", value=f"現場客 {m_n+1}")
    with c2: dsc = st.number_input("💸 折扣", min_value=0, step=5)
    st.write("---")
    ca, cb, cc = st.columns([1, 2, 1])
    with ca: cat = st.selectbox("📂 分類", list(menu.keys()))
    with cb:
        i_l = [f"{i} (餘 {st_m.get(i,0)})" for i in menu[cat].keys()]
        sel = st.selectbox("🍎 品項", i_l).split(" (餘")[0]
        rem = st_m.get(sel, 0)
    with cc: qty = st.number_input("🔢 數量", 1, max(1, rem))
    if st.button("➕ 加入", use_container_width=True, disabled=(rem<=0)):
        st.session_state.cart.append({"品項":f"[{cat[2:]}] {sel}", "單價":menu[cat][sel], "數量":qty, "小計":menu[cat][sel]*qty})
    st.write("---")
    tr = 0
    for i, it in enumerate(st.session_state.cart):
        c_a, c_b, c_c = st.columns([3,1,1])
        c_a.write(f"▪️ {it['品項']}"); c_b.write(f"${it['單價']}x{it['數量']}"); tr += it['小計']
        if c_c.button("移除", key=f"d{i}"): st.session_state.cart.pop(i); st.rerun()
    ft = max(0, tr - dsc)
    st.markdown(f'<div class="main-price">${ft:,}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center">⭐ 點數：{ft//350}</div>', unsafe_allow_html=True)
    if st.button("✅ 結帳", type="primary", use_container_width=True):
        if st.session_state.cart:
            new = pd.DataFrame([{"時間":datetime.now().strftime("%H:%M:%S"), "客戶":c_n, "明細":str([f"{i['品項']}x{i['數量']}" for i in st.session_state.cart]), "實收":ft, "小時":datetime.now().hour, "獲得點數":int(ft//350)}])
            h_df = pd.concat([h_df, new], ignore_index=True)
            h_df.to_csv(S_F, index=False, encoding='utf-8-sig'); st.session_state.cart=[]; st.rerun()
    # 💡 這裡做了「防報錯」顯示，只抓有存在的欄位
    if not h_df.empty:
        v_cols = [c for c in ['時間', '客戶', '實收'] if c in h_df.columns]
        st.table(h_df[v_cols].tail(5).iloc[::-1])

with t2:
    st.subheader("📦 庫存設定"); ed = st.data_editor(k_df, use_container_width=True, hide_index=True)
    if st.button("💾 儲存庫存"): ed.to_csv(K_F, index=False); st.rerun()

with t3:
    st.subheader("📊 業績分析")
    if not h_df.empty:
        st.metric("總營收", f"${h_df['實收'].sum():,}")
        if st.button("⚠️ 收攤清空資料"):
            if os.path.exists(S_F): os.remove(S_F)
            if os.path.exists(K_F): os.remove(K_F)
            st.rerun()
