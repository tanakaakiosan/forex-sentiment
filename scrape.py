import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape_forex_factory():
    url = "https://www.forexfactory.com/trades"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # センチメント（Positions / Live Accounts の集計テーブル）を探す
    # Forex Factoryの構造に合わせて、通貨ペアごとのLong/Short比率を抽出
    sentiment_data = {}
    
    # ページ内のテーブルや要素からデータを解析
    # ここでは例として、主要ペアの比率や直近のトレード動向を抽出するロジックを構成
    # ポジション集計テーブル（Positions / Live Accounts）の行を探す
    tables = soup.find_all('table')
    
    # 現在のUTCおよびJSTのタイムスタンプ
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    result = {
        "updated_at": now_str,
        "pairs": {}
    }

    # デモ・ライブのポジション集計セクション（Positions / Live Accounts）からデータを取得
    # Forex Factoryの「Positions」テーブル行をパース
    rows = soup.find_all('tr')
    for row in rows:
        text = row.get_text()
        # 通貨ペア名（例: EUR/USD, USD/JPY, Gold/USD など）が含まれている行をターゲットにする
        if "/" in text and ("Long" in text or "Short" in text or "Traders" in text):
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                pair_name = cols[0].get_text(strip=True)
                # スラッシュを含み、適切なペア名のものだけ処理
                if len(pair_name) <= 10 and "/" in pair_name:
                    result["pairs"][pair_name] = {
                        "raw_info": text.replace("\n", " ").strip()
                    }

    return result

if __name__ == "__main__":
    data = scrape_forex_factory()
    if data and data["pairs"]:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("data.json successfully updated.")
    else:
        print("Failed to retrieve sentiment data or data is empty.")
        # 最低限のJSON構造を維持して書き込み
        fallback_data = {
            "updated_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "pairs": {},
            "error": "Failed to scrape"
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=4)
