import os
import requests
from bs4 import BeautifulSoup

# Webhook URL（秘密の鍵）
WEBHOOK_URL = os.getenv("SANWA_WEBHOOK_URL")

def get_sanwa_sale():
    url = "https://tokubai.co.jp/%E4%B8%89%E5%92%8C/6845"
    headers = {
        # ブラウザからのアクセスを装うための、より詳細な設定
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 商品の「枠」を、クラス名に頼らず構造から探す
        # トクバイの特売品は、だいたい aタグ か div の中に固まって入っています
        items = soup.find_all(['div', 'a'], class_=lambda x: x and 'product' in x)
        
        sale_list = []
        for item in items:
            # 2. 商品名っぽいものを探す
            name_tag = item.find(['span', 'p', 'div'], class_=lambda x: x and 'name' in x)
            if not name_tag: continue
            
            # 3. 値段っぽいものを探す（数字が含まれる場所を広く探す）
            # price という文字が入っているクラスか、直接的な数字の場所を探す
            price_container = item.find(['span', 'p', 'div'], class_=lambda x: x and 'price' in x)
            
            if name_tag and price_container:
                name = name_tag.get_text(strip=True)
                # 値段の中にある余計な「産地」などの情報を削ぎ落とす
                price_full = price_container.get_text(" ", strip=True)
                # 最初の15文字くらいに値段が凝縮されていることが多いので整理
                price = price_full.split()[0] if price_full else "価格はリンク先へ"

                entry = f"・{name}：**{price}**"
                if entry not in sale_list:
                    sale_list.append(entry)
        
        if not sale_list:
            # もし全滅した場合、ページ内にある「〇〇円」という文字を強引に探す（最終手段）
            for p in soup.find_all(text=lambda t: '円' in t):
                if len(p) < 30: # あまりに長い文章は除外
                    sale_list.append(f"・お得情報：**{p.strip()}**")

        if not sale_list:
            return "今日は本当にテキストデータが隠されとるみたいや…。チラシを直接見てみてな！\n" + url
            
        header = f"【三和 八王子みなみ野店】特売品を見つけ出してきたで！\n"
        footer = f"\n\n詳細はこちら：\n{url}"
        
        return header + "\n".join(sale_list[:15]) + footer
        
    except Exception as e:
        return f"ごめん、三和の情報がうまく取れんかった…。\nエラー：{e}"

if __name__ == "__main__":
    if WEBHOOK_URL:
        message = get_sanwa_sale()
        requests.post(WEBHOOK_URL, json={"content": message})
