import os
import requests
import re # 数字を抽出するために追加
from bs4 import BeautifulSoup

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
        
        # 特売品の枠を特定
        items = soup.select('.product_item')
        
        sale_list = []
        for item in items:
            # 1. 商品名を取得
            name_tag = item.select_one('.name')
            if not name_tag: continue
            name = name_tag.get_text(strip=True)
            
            # 2. 値段の情報を取得（価格エリア全体を一度取る）
            price_area = item.select_one('.price_container, .price_text, .price')
            if not price_area: continue
            
            # 3. エリア内のテキストをすべて取得し、"円" という文字と "数字" を含む部分を探す
            # 産地（静岡県産など）を無視して、値段だけを抜き出す工夫
            price_text = ""
            # price_text クラスがあればそれを最優先
            price_target = price_area.select_one('.price_text')
            if price_target:
                price_text = price_target.get_text(strip=True)
            else:
                # 無ければエリア全体から「円」を含むテキストを探す
                all_text = price_area.get_text(" ", strip=True)
                # 正規表現で「数字+円」のパターンを探す
                match = re.search(r'[\d,]+円\(税込\)|[\d,]+円', all_text)
                if match:
                    price_text = match.group()
                else:
                    price_text = all_text.split()[-1] # 一番最後にあるのが値段であることが多い
            
            # 余計な記号を掃除
            price_text = price_text.replace('', '').strip()
            
            entry = f"・{name}：**{price_text}**"
            if entry not in sale_list:
                sale_list.append(entry)
        
        if not sale_list:
            return "今日はテキストが見つからんかったわ。直接チラシを見てみてな！\n" + url
            
        header = f"【三和 八王子みなみ野店】今日の特売品やで！\n"
        footer = f"\n\n詳細はこちら：\n{url}"
        return header + "\n".join(sale_list[:15]) + footer
        
    except Exception as e:
        return f"ごめん、三和の情報がうまく取れんかった…。\nエラー：{e}"

if __name__ == "__main__":
    if WEBHOOK_URL:
        message = get_sanwa_sale()
        requests.post(WEBHOOK_URL, json={"content": message})
