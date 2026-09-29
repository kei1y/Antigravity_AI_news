import os
import requests
from datetime import datetime, timezone, timedelta

def send_discord_notification(articles: list, webhook_url: str = None, web_app_url: str = None):
    """
    Discord Webhook に要約ハイライトとWebアプリURLを通知
    """
    if not webhook_url:
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print(" [通知スキップ] DISCORD_WEBHOOK_URL が設定されていないため、Discord通知をスキップします。")
        return

    if not web_app_url:
        web_app_url = os.environ.get("WEB_APP_URL", "https://your-username.github.io/Antigravity_AI_news/")

    jst = timezone(timedelta(hours=9))
    date_str = datetime.now(jst).strftime("%m/%d(%a)")

    # インパクトの高い順にソートしてTOP 3抽出
    top_articles = sorted(articles, key=lambda x: x.get("impact_score", 1), reverse=True)[:3]

    embed_fields = []
    for item in top_articles:
        stars = "★" * item.get("impact_score", 1)
        first_bullet = item["bullets"][0] if item.get("bullets") else ""
        embed_fields.append({
            "name": f"{stars} {item['japanese_title']}",
            "value": f"{first_bullet}\n[原文記事を読む]({item['url']})",
            "inline": False
        })

    payload = {
        "content": f"🌅 **【朝のAIニュース要約】{date_str}**\n今朝の注目AIトピックをお届けします！\n📲 [全件をWebアプリで開く]({web_app_url})",
        "embeds": [
            {
                "title": f"⚡ 今朝のピックアップ TOP {len(top_articles)}",
                "url": web_app_url,
                "color": 9125878, # パープルカラー (0x8B5CF6)
                "fields": embed_fields,
                "footer": {
                    "text": "AI News Digest • 毎朝自動配信"
                }
            }
        ]
    }

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        print(" [Discord通知] メッセージの送信に成功しました。")
    except Exception as e:
        print(f" [Discord通知エラー] 送信に失敗しました: {e}")

if __name__ == "__main__":
    test_articles = [
        {
            "japanese_title": "OpenAIがGPT-5のプレビュー版を発表",
            "impact_score": 3,
            "bullets": ["📌 人間レベルの推論能力を達成したと主張"],
            "url": "https://example.com"
        }
    ]
    send_discord_notification(test_articles)
