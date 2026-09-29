import os
import json
import time
import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def summarize_article_with_gemini(article: dict, api_key: str) -> dict:
    """
    1件の記事をGemini APIで日本語翻訳＆要約＋属性分類
    """
    url = f"{GEMINI_API_URL}?key={api_key}"

    is_english = article.get("lang") == "en"
    source_type_hint = "海外の英語ニュース" if is_english else "日本のニュース"

    prompt = f"""
以下のAI・IT関連の記事（{source_type_hint}）を読み、スマホでサクッと読める形式に【完全な日本語】に翻訳・要約し、属性を分類してください。

【元記事情報】
- 出典: {article['source_name']}
- 元タイトル: {article['title']}
- 本文/概要 snippet:
{article['raw_summary']}

【出力要求フォーマット】
以下のJSONフォーマットのみを出力してください。余計な解説文や```jsonマーカーは不要です。

{{
  "japanese_title": "読みやすく惹きのある自然な日本語タイトル（20〜35文字程度）",
  "bullets": [
    "📌 要約ポイント1（日本語、絵文字付き、要点をわかりやすく）",
    "💡 要約ポイント2（日本語、絵文字付き、技術や成果の詳細）",
    "🚀 要約ポイント3（日本語、絵文字付き、今後の影響や活用例）"
  ],
  "impact_score": 3,
  "genre": "先進技術",
  "tags": ["LLM", "OpenAI", "新機能"]
}}

注意:
- 元記事が英語の場合でも、japanese_title, bullets, tags はすべて自然で分かりやすい日本語に翻訳・生成してください。
- impact_score は 1（標準）, 2（注目）, 3（超重要・大ニュース）の3段階で評価してください。
- genre は以下の選択肢の中から最も適したものを1つ選んでください:
  - "先進技術" (AIの技術革新、新モデル発表、マルチモーダル等)
  - "論文・研究" (ArXiv、研究成果、学術論文等)
  - "ビジネス・活用" (企業導入、決算、投資、スタートアップ等)
  - "製品・アップデート" (アプリの新機能、アップデート、新ツール等)
  - "社会・規制" (著作権、法律、AI倫理、ガイドライン等)
- tags は 1〜3個の短い日本語キーワードを設定してください。
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        text_response = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        if text_response.startswith("```"):
            text_response = text_response.split("\n", 1)[-1]
            if text_response.endswith("```"):
                text_response = text_response.rsplit("```", 1)[0]
            text_response = text_response.strip()

        result = json.loads(text_response)

        article["japanese_title"] = result.get("japanese_title", article["title"])
        article["bullets"] = result.get("bullets", [article["raw_summary"][:100]])
        article["impact_score"] = result.get("impact_score", 2)
        article["genre"] = result.get("genre", "先進技術")
        article["tags"] = result.get("tags", [article["category"]])

        return article

    except Exception as e:
        print(f"   [Gemini APIエラー] '{article['title'][:20]}...' の要約に失敗: {e}")
        article["japanese_title"] = article["title"]
        article["bullets"] = [
            f"📌 {article['raw_summary'][:120]}...",
            "🔗 原文リンクから詳細をご確認ください。"
        ]
        article["impact_score"] = 2
        article["genre"] = "先進技術"
        article["tags"] = [article["category"]]
        return article


def batch_summarize(articles: list, api_key: str = None) -> list:
    """
    記事リスト全体を要約
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print(" [警告] GEMINI_API_KEY が設定されていません。AI要約をスキップしフォールバック表示を使用します。")
        for a in articles:
            a["japanese_title"] = a["title"]
            a["bullets"] = [f"📌 {a['raw_summary'][:150]}..."]
            a["impact_score"] = 2
            a["genre"] = "先進技術"
            a["tags"] = [a["category"]]
        return articles

    print(f"[{time.strftime('%H:%M:%S')}] Gemini APIで {len(articles)} 件の記事を要約・翻訳中...")
    summarized = []

    for i, article in enumerate(articles):
        print(f" ({i+1}/{len(articles)}) 処理中: [{article['lang']}] {article['title'][:30]}...")
        res = summarize_article_with_gemini(article, api_key)
        summarized.append(res)
        time.sleep(2)

    return summarized
