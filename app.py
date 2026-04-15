import streamlit as st

# 設定 iPad 滿版模式
st.set_page_config(page_title="花田喜彘結帳系統", layout="wide")

# 自訂 CSS 讓字體變大
st.markdown("""
    <style>
    .main-price {
        font-size: 80px !important;
        font-weight: bold;
        color: #E63946;
        text-align: center;
        background-color: #F1FAEE;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 花田喜彘 - 市集 POS 結帳機")

# 建立「購物車記憶」 (這是 2.0 版的靈魂)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# 真實商品資料庫
products = {
    "黑豬梅花薄片 (200g)": 198,
    "黑豬梅花厚片 (200g)": 198,
    "黑豬里肌薄片 (200g)": 180,
    "黑豬里肌厚片 (200g)": 180,
    "黑豬五花薄片 (200g)": 215,
    "黑豬五花厚片 (200g)": 215,
    "黑豬龍骨 (300g)": 118,
    "黑豬梅花排骨 (300g)": 215,
    "老鼠肉 (220g)": 165,
    "黑豬原味貢丸": 140,
    "黑豬香菇貢丸": 155
}

st.write("---")

# 上方區域：點單輸入區
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    selected_item = st.selectbox("🍎 選擇品項", list(products.keys()))
    unit_price = products[selected_item]

with col2:
    qty = st.number_input("🔢 數量", min_value=1, value=1, step=1)

with col3:
    st.write("") # 排版用空白
    st.write("")
    if st.button("➕ 加入清單", use_container_width=True):
        # 將商品加入購物車記憶中
        st.session_state.cart.append({
            "name": selected_item,
            "price": unit_price,
            "qty": qty,
            "subtotal": unit_price * qty
        })

st.write("---")

# 中間區域：顯示購物車清單
st.subheader("📋 目前結帳清單")

total_amount = 0

if len(st.session_state.cart) == 0:
    st.info("清單目前是空的，請在上方選擇商品並點擊「加入清單」。")
else:
    # 逐一列出購物車內的商品
    for item in st.session_state.cart:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.write(f"▪️ **{item['name']}**")
        c2.write(f"單價 ${item['price']}")
        c3.write(f"數量: {item['qty']}")
        c4.write(f"小計 **${item['subtotal']}**")
        # 累加總金額
        total_amount += item['subtotal']

st.write("---")

# 下方區域：巨大總金額與清空按鈕
st.markdown("### 💰 應收總金額")
st.markdown(f'<div class="main-price">${total_amount:,}</div>', unsafe_allow_html=True)

if st.button("🗑️ 結帳完成 / 下一位客人 (清空清單)", type="primary", use_container_width=True):
    st.session_state.cart = []
    st.rerun()
