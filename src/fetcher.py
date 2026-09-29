import json
import time
import re
from datetime import datetime, timedelta, timezone
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

def clean_html(raw_html: str) -> str:
    """HTMLタグを除去し、テキストのみを抽出"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', text)

def fetch_latest_news(sources_path: str = "sources.json", hours_limit: int = 48, max_items_per_source: int = 5):
    """
    sources.jsonから取得元を読み込み、直近ニュースを取得
    """
    with open(sources_path, "r", encoding="utf-8") as f:
        sources = json.load(f)

    all_articles = []
    seen_urls = set()
    now = datetime.now(timezone.utc)
    time_cutoff = now - timedelta(hours=hours_limit)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ニュース取得を開始します (過去{hours_limit}時間以内の記事)...")

    for src in sources:
        print(f" -> 取得中: {src['name']} ({src['url']})")
        try:
            feed = feedparser.parse(src['url'])
            count = 0
            for entry in feed.entries:
                if count >= max_items_per_source:
                    break

                title = clean_html(entry.get("title", ""))
                link = entry.get("link", "")

                if not link or link in seen_urls:
                    continue

                # フィルターキーワード（例: GIGAZINEでAI記事のみ抽出する等）
                filter_kw = src.get("filter_keyword")
                if filter_kw and filter_kw.lower() not in title.lower() and filter_kw.lower() not in entry.get("summary", "").lower():
                    continue

                # 日時パース
                pub_date = None
                if hasattr(entry, "published"):
                    try:
                        pub_date = date_parser.parse(entry.published)
                    except Exception:
                        pass
                elif hasattr(entry, "updated"):
                    try:
                        pub_date = date_parser.parse(entry.updated)
                    except Exception:
                        pass

                if pub_date:
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                    if pub_date < time_cutoff:
                        continue
                else:
                    pub_date = now

                # コンテンツ抽出
                summary_raw = entry.get("summary", "")
                if hasattr(entry, "content") and len(entry.content) > 0:
                    summary_raw = entry.content[0].value

                summary_clean = clean_html(summary_raw)[:1000] # 最大1000文字程度にトリム

                seen_urls.add(link)
                all_articles.append({
                    "id": f"{src['id']}_{len(all_articles)}",
                    "source_name": src["name"],
                    "category": src.get("category", "ニュース"),
                    "title": title,
                    "url": link,
                    "raw_summary": summary_clean,
                    "published_at": pub_date.isoformat(),
                    "lang": src.get("lang", "ja")
                })
                count += 1

        except Exception as e:
            print(f"   [警告] {src['name']} の取得に失敗しました: {e}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 合計 {len(all_articles)} 件の最新記事を取得しました。")
    return all_articles

if __name__ == "__main__":
    articles = fetch_latest_news(hours_limit=48)
    for a in articles[:3]:
        print(f"- [{a['source_name']}] {a['title']} ({a['url']})")
