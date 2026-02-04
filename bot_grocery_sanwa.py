import os
import requests
from bs4 import BeautifulSoup

# Discordの新しいチャンネル用のWebhook URL
WEBHOOK_URL = os.getenv("SANWA_WEBHOOK_URL")

def get_sanwa_sale():
    # 三和 八王子みなみ野店のトクバイページ
    url = "https://tokubai.co.jp/%E4%B8%89%E5%92%8C/6845"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.31"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 特売品のリストを取得（トクバイの構成に合わせています）
        # クラス名はサイトの更新で変わることがありますが、現在は product_item を探します
        items = soup.find_all(class_='product_item')
        
        sale_list = []
        for item in items:
            name_tag = item.find(class_='name')
            price_tag = item.find(class_='price')
            
            if name_tag and price_tag:
                name = name_tag.get_text(strip=True)
                price = price_tag.get_text(strip=True)
                sale_list.append(f"・{name}：**{price}**")
        
        if not sale_list:
            return "今日は目玉商品のテキスト情報がないみたい。リンクからチラシを見てみて！"
            
        header = f"【三和 八王子みなみ野店】今日の特売品！\n"
        footer = f"\n\n詳細はこちら：\n{url}"
        return header + "\n".join(sale_list[:15]) + footer # 最大15件表示
        
    except Exception as e:
        return f"ごめん、三和の情報がいい感じに取れんかった…。\nエラー：{e}"

if __name__ == "__main__":
    if WEBHOOK_URL:
        message = get_sanwa_sale()
        requests.post(WEBHOOK_URL, json={"content": message})
