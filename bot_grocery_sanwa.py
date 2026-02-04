import os
import requests
import re
from bs4 import BeautifulSoup

# Webhook URL
WEBHOOK_URL = os.getenv("SANWA_WEBHOOK_URL")

def get_sanwa_sale():
    url = "https://tokubai.co.jp/%E4%B8%89%E5%92%8C/6845"
    # より「人間がブラウザで見てる」感を出すためのヘッダー
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "ja-JP,ja;q=0.9"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. まずは「商品の枠」を広めに探す
        items = soup.find_all(class_=re.compile("product|item|card"))
        
        sale_list = []
        for item in items:
            # 商品名を探す
            name_tag = item.find(class_=re.compile("name|title"))
            # 値段を探す
            price_tag = item.find(class_=re.compile("price"))
            
            if name_tag and price_tag:
                name = name_tag.get_text(strip=True)
                # 値段のテキストから「数字と円」だけを抜き出す
                price_full = price_tag.get_text(strip=True)
                # 正規表現で「数字(カンマ込)＋円」を抽出
                price_match = re.search(r'[\d,]+円', price_full)
                
                if price_match:
                    price = price_match.group()
                    # 重複を防いでリストに追加
                    entry = f"・{name}：**{price}**"
                    if entry not in sale_list:
                        sale_list.append(entry)

        # 2. 【最終手段】もし上記で見つからなかった場合、ページ内の全テキストから探す
        if not sale_list:
            # ページ内のすべての「円」を含む要素をチェック
            for tag in soup.find_all(['span', 'p', 'div']):
                text = tag.get_text(strip=True)
                if '円' in text and len(text) < 20:
                    # 数字が含まれているか確認
                    if re.search(r'\d', text):
                        # その近く（親要素）にある商品名っぽいのを探す
                        parent_text = tag.parent.get_text(" ", strip=True)
                        if parent_text not in sale_list:
                            sale_list.append(f"・お得品：**{text}**")

        if not sale_list:
            return f"今日は本当にテキストデータが取れんかった…。直接チラシを見てな！\n{url}"
            
        header = "【三和 八王子みなみ野店】特売品を力技で見つけてきたで！\n"
        footer = f"\n\n詳細はこちら：\n{url}"
        
        # 似たような項目を整理して最大15件
        unique_sales = list(dict.fromkeys(sale_list))
        return header + "\n".join(unique_sales[:15]) + footer
        
    except Exception as e:
        return f"ごめん、三和の情報がうまく取れんかった…。\nエラー：{e}"

if __name__ == "__main__":
    if WEBHOOK_URL:
        message = get_sanwa_sale()
        requests.post(WEBHOOK_URL, json={"content": message})
