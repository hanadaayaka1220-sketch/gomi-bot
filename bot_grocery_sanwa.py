import os
import requests
from bs4 import BeautifulSoup

# Webhook URL（秘密の鍵）
WEBHOOK_URL = os.getenv("SANWA_WEBHOOK_URL")

def get_sanwa_sale():
    url = "https://tokubai.co.jp/%E4%B8%89%E5%92%8C/6845"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 商品の枠を特定
        items = soup.select('.product_item')
        
        sale_list = []
        for item in items:
            # 商品名を取得
            name_tag = item.select_one('.name')
            
            # 値段を取得（数字が含まれるクラスを優先的に探す）
            # トクバイの仕様に合わせて price_text や price_value を重点チェック
            price_tag = item.select_one('.price_text, .price, .product_price')
            
            if name_tag and price_tag:
                name = name_tag.get_text(strip=True)
                # 値段のテキストを取得し、改行や余計な空白を詰める
                price = price_tag.get_text(strip=True).replace('\n', '').replace(' ', '')
                
                entry = f"・{name}：**{price}**"
                if entry not in sale_list:
                    sale_list.append(entry)
        
        if not sale_list:
            return "今日はテキスト形式の特売データが見つからんかったわ。リンクからチラシを見てな！\n" + url
            
        header = f"【三和 八王子みなみ野店】今日の特売品リストやで！\n"
        footer = f"\n\n詳細はこちら：\n{url}"
        
        return header + "\n".join(sale_list[:15]) + footer
        
    except Exception as e:
        return f"ごめん、三和の情報がうまく取れんかった…。\nエラー：{e}"

if __name__ == "__main__":
    if WEBHOOK_URL:
        message = get_sanwa_sale()
        requests.post(WEBHOOK_URL, json={"content": message})
