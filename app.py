import pandas as pd

def run_calculator():
    print("--- 花田喜彘 訂單計算工具 ---")
    
    # 修改重點：加上 encoding='cp950' 來處理繁體中文
    try:
        # 先嘗試台灣常用的 cp950 (ANSI)
        df = pd.read_csv('希望廣場202604.csv', encoding='cp950')
    except UnicodeDecodeError:
        # 如果還是失敗，嘗試 utf-8
        df = pd.read_csv('希望廣場202604.csv', encoding='utf-8')
    except Exception as e:
        print(f"讀取失敗，原因：{e}")
        return

    total_amount = 0
    results = []

    # 根據你的 CSV 結構，我們直接從「品名」和「售價」這兩欄抓資料
    # 使用 fillna(0) 避免空白格導致計算錯誤
    df['售價'] = pd.to_numeric(df['售價'], errors='coerce').fillna(0)
    
    # 過濾掉沒有品名的列
    items = df[df['品名'].notna()]

    for index, row in items.iterrows():
        name = row['品名']
        price = int(row['售價'])
        
        # 排除標題列與沒有價格的項目
        if name in ['白豬', '黑豬', '品名'] or price == 0:
            continue
            
        # 提示輸入
        qty_input = input(f"{name} (單價: {price}) - 請輸入數量: ")
        
        if not qty_input.strip() or qty_input == "0":
            continue
            
        try:
            qty = int(qty_input)
            subtotal = price * qty
            total_amount += subtotal
            results.append(f"● {name:20} x {qty:2} = {subtotal:5} 元")
        except ValueError:
            print("請輸入數字！跳過此項。")

    print("\n" + "="*30)
    print("      訂 單 結 帳 明 細")
    print("="*30)
    for res in results:
        print(res)
    print("-" * 30)
    print(f"總計金額： {total_amount} 元")
    print("="*30)
    input("\n按任意鍵結束程式...")

if __name__ == "__main__":
    run_calculator()
