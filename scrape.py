import json
from datetime import datetime, timezone
import cloudscraper
from bs4 import BeautifulSoup

def scrape_forex_factory():
    url = "https://www.forexfactory.com/trades"
    
    # cloudscraperを使用してCloudflareなどのボット対策を回避
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 現在のUTCのタイムスタンプ
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    result = {
        "updated_at": now_str,
        "pairs": {}
    }

    rows = soup.find_all('tr')
    for row in rows:
        text = row.get_text()
        if "/" in text and ("Long" in text or "Short" in text or "Traders" in text):
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                pair_name = cols[0].get_text(strip=True)
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
        fallback_data = {
            "updated_at": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "pairs": {},
            "error": "Failed to scrape"
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=4)
