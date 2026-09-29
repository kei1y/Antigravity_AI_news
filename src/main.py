import os
import sys
from datetime import datetime
from fetcher import fetch_latest_news
from summarizer import batch_summarize
from builder import build_web_site
from notifier import send_discord_notification

def run_pipeline():
    print(f"==========================================")
    print(f" AI News Digest パイプライン開始 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"==========================================")

    # 1. ニュース収集
    articles = fetch_latest_news(sources_path="sources.json", hours_limit=48)
    if not articles:
        print(" 最新の記事が見つかりませんでした。パイプラインを終了します。")
        return

    # 2. AI日本語要約 (Gemini)
    api_key = os.environ.get("GEMINI_API_KEY")
    summarized_articles = batch_summarize(articles, api_key=api_key)

    # 3. Webサイト (HTML/PWA) 生成
    output_dir = "dist"
    build_web_site(summarized_articles, output_dir=output_dir)

    # 4. Discord 通知送信
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    web_app_url = os.environ.get("WEB_APP_URL")
    send_discord_notification(summarized_articles, webhook_url=webhook_url, web_app_url=web_app_url)

    print(f"==========================================")
    print(f" パイプラインが正常終了しました！")
    print(f"==========================================")

if __name__ == "__main__":
    run_pipeline()
