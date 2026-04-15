import streamlit as st

# 設定 iPad 滿版模式
st.set_page_config(page_title="花田喜彘結帳系統", layout="wide")

# 自訂 CSS 讓字體變大，適合現場看
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
    }
    .product-info {
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 花田喜彘 - 市集 POS 結帳機")

# 真實商品資料庫 (根據你的 2026 販售表更新)
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

# 左右並排，左邊選商品，右邊選數量
col1, col2 = st.columns([2, 1])

with col1:
    selected_item = st.selectbox("🍎 選擇販售品項", list(products.keys()), index=0)
    unit_price = products[selected_item]
    st.markdown(f"### 單價： `${unit_price}`")

with col2:
    qty = st.number_input("🔢 數量", min_value=1, value=1, step=1)

# 計算總額
total_amount = unit_price * qty

st.write("---")
st.markdown("### 💰 應收金額")
st.markdown(f'<div class="main-price">${total_amount:,}</div>', unsafe_allow_html=True)

st.info("💡 提示：在 iPad 上點擊瀏覽器分享按鈕並選擇『加入主畫面』，即可像 App 一樣全螢幕使用。")
