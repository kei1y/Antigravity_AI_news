import os
import json
import html
from datetime import datetime, timezone, timedelta

# アクセス暗証番号
PASSCODE = "000011"

def build_web_site(articles: list, output_dir: str = "dist"):
    """
    HTMLおよび静的データを生成
    - 上部メインナビ: 「🔥 注目 TOP10」「📨 未読」「✅ 既読」
    - サブナビ: サイト毎（PIVOT, ITmedia, OpenAI等）の横スクロールタブ
    - 暗証番号保護機能 (パスコード: 000011)
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)

    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    
    updated_date_str = now_jst.strftime("%Y年%m月%d日 (%a)")
    updated_time_str = now_jst.strftime("%H:%M")

    # 1. 星（impact_score）の多い順 ➔ 発行日時の新しい順 にソート
    sorted_articles = sorted(
        articles,
        key=lambda x: (x.get("impact_score", 1), x.get("published_at", "")),
        reverse=True
    )

    # 上位10件のIDを記録（TOP10バッジ用）
    top10_ids = set(a.get("id", "") for a in sorted_articles[:10])

    # 記事カードのHTML生成
    cards_html_list = []
    for item in sorted_articles:
        article_id = item.get("id", f"art_{hash(item.get('url', ''))}")
        source_name = item.get("source_name", "その他")
        impact = item.get("impact_score", 1)
        stars_str = "★★★ 大注目" if impact == 3 else ("★★☆ 注目" if impact == 2 else "★☆☆ トピック")
        is_top10 = article_id in top10_ids
        
        # 国内/海外バッジ
        is_en = item.get("lang") == "en"
        region_badge = '<span class="region-badge region-overseas">🌍 海外</span>' if is_en else '<span class="region-badge region-japan">🇯🇵 国内</span>'

        # ジャンルバッジ
        genre = item.get("genre", "先進技術")
        genre_icons = {
            "先進技術": "🚀 先進技術",
            "論文・研究": "📄 論文",
            "ビジネス・活用": "💼 ビジネス",
            "製品・アップデート": "📱 製品",
            "社会・規制": "⚖️ 倫理・規制"
        }
        genre_label = genre_icons.get(genre, f"💡 {genre}")
        genre_badge = f'<span class="genre-badge">{html.escape(genre_label)}</span>'

        # TOP10バッジ
        top10_badge = '<span class="top10-badge">🔥 TOP 10</span>' if is_top10 else ''

        # Bullets
        bullets_html = ""
        for bullet in item.get("bullets", []):
            bullets_html += f"<li>{html.escape(bullet)}</li>\n"

        # Tags
        tags_html = ""
        for tag in item.get("tags", []):
            tags_html += f'<span class="tag-pill">#{html.escape(tag)}</span>\n'

        card_html = f"""
            <article class="card impact-{impact}" data-article-id="{html.escape(article_id)}" data-source-name="{html.escape(source_name)}" data-is-top10="{ 'true' if is_top10 else 'false' }">
                <div class="card-header-badges">
                    <div class="badge-group">
                        {top10_badge}
                        {region_badge}
                        {genre_badge}
                        <span class="source-tag">{html.escape(source_name)}</span>
                    </div>
                    <span class="impact-stars">{stars_str}</span>
                </div>

                <h2 class="card-title">{html.escape(item.get('japanese_title', item.get('title', '')))}</h2>

                <ul class="bullets-list">
                    {bullets_html}
                </ul>

                <div class="card-footer">
                    <div class="tags-container">
                        {tags_html}
                    </div>
                    <div class="action-buttons">
                        <button class="mark-read-btn" onclick="toggleReadState('{html.escape(article_id)}')">
                            <span class="btn-icon">✓</span> <span class="btn-text">既読にする</span>
                        </button>
                        <a href="{html.escape(item.get('url', '#'))}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
                            原文 ➔
                        </a>
                    </div>
                </div>
            </article>
        """
        cards_html_list.append(card_html)

    cards_combined_html = "\n".join(cards_html_list)

    full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI News Digest | 毎朝の最新AIニュース要約</title>
    
    <!-- PWA Settings -->
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0f172a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="AI Digest">

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            --card-bg: rgba(30, 41, 59, 0.75);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --star-color: #fbbf24;
            --accent-purple: #8b5cf6;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            font-family: 'Noto Sans JP', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            padding-bottom: 40px;
        }}

        /* Lock Screen Overlay */
        .lock-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }}

        .lock-box {{
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 32px 24px;
            width: 100%;
            max-width: 360px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }}

        .lock-icon {{
            font-size: 3rem;
            margin-bottom: 12px;
        }}

        .lock-title {{
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 6px;
            color: #ffffff;
        }}

        .lock-desc {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }}

        .pass-input {{
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(15, 23, 42, 0.8);
            color: #ffffff;
            font-size: 1.2rem;
            text-align: center;
            letter-spacing: 4px;
            outline: none;
            margin-bottom: 16px;
        }}

        .pass-input:focus {{
            border-color: #8b5cf6;
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
        }}

        .unlock-btn {{
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
            color: #ffffff;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
        }}

        .unlock-btn:active {{
            opacity: 0.85;
        }}

        .error-msg {{
            color: #f87171;
            font-size: 0.8rem;
            margin-top: 10px;
            display: none;
        }}

        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--card-border);
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 900;
            font-size: 1.25rem;
            background: linear-gradient(to right, #c084fc, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .logo-icon {{
            font-size: 1.4rem;
            -webkit-text-fill-color: initial;
        }}

        .update-badge {{
            font-size: 0.75rem;
            background: rgba(139, 92, 246, 0.2);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 500;
        }}

        .container {{
            max-width: 640px;
            margin: 0 auto;
            padding: 16px;
        }}

        .date-banner {{
            margin-bottom: 16px;
        }}

        .date-banner h1 {{
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 2px;
        }}

        .date-banner p {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        /* Upper Main Navigation Tabs */
        .main-tab-nav {{
            display: flex;
            background: rgba(15, 23, 42, 0.6);
            padding: 4px;
            border-radius: 14px;
            border: 1px solid var(--card-border);
            margin-bottom: 12px;
        }}

        .main-tab-btn {{
            flex: 1;
            padding: 10px 4px;
            text-align: center;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }}

        .main-tab-btn.active {{
            background: #334155;
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .main-tab-btn.active#tab-top10 {{
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.25) 0%, rgba(245, 158, 11, 0.25) 100%);
            color: #fef08a;
            border: 1px solid rgba(251, 191, 36, 0.4);
        }}

        .tab-count {{
            background: rgba(255, 255, 255, 0.15);
            padding: 2px 7px;
            border-radius: 10px;
            font-size: 0.72rem;
        }}

        /* Source Filter Tabs (Sub Nav - Horizontally Scrollable) */
        .source-filter-container {{
            margin-bottom: 20px;
        }}

        .source-filter-title {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 6px;
            font-weight: 600;
        }}

        .source-filter-bar {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 6px;
            scrollbar-width: none;
        }}

        .source-filter-bar::-webkit-scrollbar {{
            display: none;
        }}

        .source-chip {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--card-border);
            color: var(--text-secondary);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .source-chip.active {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(59, 130, 246, 0.3) 100%);
            color: #ffffff;
            border-color: rgba(168, 85, 247, 0.5);
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
        }}

        /* News Cards */
        .news-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 18px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            transition: opacity 0.3s ease, transform 0.3s ease;
        }}

        .card.impact-3 {{
            border-color: rgba(251, 191, 36, 0.4);
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.85) 0%, rgba(45, 34, 15, 0.45) 100%);
        }}

        .card.impact-3::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #fbbf24, #f59e0b);
        }}

        .card-header-badges {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 8px;
        }}

        .badge-group {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .top10-badge {{
            font-size: 0.7rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            color: #1e1b4b;
            padding: 2px 8px;
            border-radius: 6px;
        }}

        .region-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
        }}

        .region-japan {{
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .region-overseas {{
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}

        .genre-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            background: rgba(168, 85, 247, 0.2);
            color: #e9d5ff;
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 2px 8px;
            border-radius: 6px;
        }}

        .source-tag {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 8px;
            border-radius: 6px;
        }}

        .impact-stars {{
            color: var(--star-color);
            font-size: 0.85rem;
            font-weight: 700;
            white-space: nowrap;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.45;
            margin-bottom: 12px;
            color: #ffffff;
        }}

        .bullets-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
            background: rgba(15, 23, 42, 0.45);
            padding: 12px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .bullets-list li {{
            font-size: 0.88rem;
            color: #cbd5e1;
            line-height: 1.5;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .tags-container {{
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}

        .tag-pill {{
            font-size: 0.68rem;
            color: #94a3b8;
            background: rgba(148, 163, 184, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .action-buttons {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .mark-read-btn {{
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s ease;
        }}

        .mark-read-btn:active {{
            background: rgba(34, 197, 94, 0.3);
        }}

        .read-more-btn {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            color: #60a5fa;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 8px;
            background: rgba(59, 130, 246, 0.12);
        }}

        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-secondary);
            background: var(--card-bg);
            border-radius: 18px;
            border: 1px dashed var(--card-border);
        }}

        footer {{
            text-align: center;
            margin-top: 36px;
            color: var(--text-muted);
            font-size: 0.78rem;
        }}
    </style>
</head>
<body>

    <!-- Lock Screen Overlay -->
    <div id="lock-overlay" class="lock-overlay">
        <div class="lock-box">
            <div class="lock-icon">🔒</div>
            <div class="lock-title">プライベートアクセス</div>
            <div class="lock-desc">暗証番号を入力してください</div>
            <input type="password" id="pass-input" class="pass-input" placeholder="••••••" maxlength="6" pattern="[0-9]*" inputmode="numeric">
            <button class="unlock-btn" onclick="checkPasscode()">ロック解除 ➔</button>
            <div id="error-msg" class="error-msg">暗証番号が正しくありません</div>
        </div>
    </div>

    <header>
        <div class="logo">
            <span class="logo-icon">⚡</span>
            <span>AI News Digest</span>
        </div>
        <div class="update-badge">毎朝7時自動更新</div>
    </header>

    <div class="container">
        <div class="date-banner">
            <h1>{updated_date_str}</h1>
            <p>Gemini AIが要約した最新AIトピックス</p>
        </div>

        <!-- Upper Main Navigation Tabs -->
        <nav class="main-tab-nav">
            <button class="main-tab-btn active" id="tab-top10" onclick="switchMainTab('top10')">
                <span>🔥 注目 TOP10</span>
                <span class="tab-count" id="top10-count">0</span>
            </button>
            <button class="main-tab-btn" id="tab-unread" onclick="switchMainTab('unread')">
                <span>📨 未読</span>
                <span class="tab-count" id="unread-count">0</span>
            </button>
            <button class="main-tab-btn" id="tab-read" onclick="switchMainTab('read')">
                <span>✅ 既読</span>
                <span class="tab-count" id="read-count">0</span>
            </button>
        </nav>

        <!-- Sub Source Filter Bar -->
        <div class="source-filter-container">
            <div class="source-filter-title">サイトで絞り込み</div>
            <div class="source-filter-bar" id="source-filter-bar">
            </div>
        </div>

        <main class="news-list" id="news-container">
            {cards_combined_html}
        </main>

        <div id="empty-state" class="empty-state" style="display: none;">
            <p id="empty-msg">記事はありません🎉</p>
        </div>

        <footer>
            <p>Powered by GitHub Actions & Google Gemini API</p>
            <p style="margin-top: 4px;">Updated at {updated_time_str} JST</p>
        </footer>
    </div>

    <script>
        const CORRECT_PASSCODE = "{PASSCODE}";
        const AUTH_STORAGE_KEY = 'ai_digest_auth_passed_v1';
        const STORAGE_KEY = 'ai_digest_read_ids_v1';
        
        let currentMainTab = 'top10';
        let currentSource = 'ALL';

        function checkPasscode() {{
            const input = document.getElementById('pass-input').value;
            const errorMsg = document.getElementById('error-msg');
            if (input === CORRECT_PASSCODE) {{
                localStorage.setItem(AUTH_STORAGE_KEY, 'true');
                document.getElementById('lock-overlay').style.display = 'none';
                errorMsg.style.display = 'none';
            }} else {{
                errorMsg.style.display = 'block';
                document.getElementById('pass-input').value = '';
            }}
        }}

        // Enterキーで解除
        document.getElementById('pass-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                checkPasscode();
            }}
        }});

        function initAuth() {{
            const passed = localStorage.getItem(AUTH_STORAGE_KEY);
            if (passed === 'true') {{
                document.getElementById('lock-overlay').style.display = 'none';
            }} else {{
                document.getElementById('lock-overlay').style.display = 'flex';
            }}
        }}

        function getReadIds() {{
            try {{
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            }} catch (e) {{
                return [];
            }}
        }}

        function saveReadIds(ids) {{
            localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
        }}

        function toggleReadState(articleId) {{
            let readIds = getReadIds();
            if (readIds.includes(articleId)) {{
                readIds = readIds.filter(id => id !== articleId);
            }} else {{
                readIds.push(articleId);
            }}
            saveReadIds(readIds);
            renderUI();
        }}

        function switchMainTab(tab) {{
            currentMainTab = tab;
            document.getElementById('tab-top10').classList.toggle('active', tab === 'top10');
            document.getElementById('tab-unread').classList.toggle('active', tab === 'unread');
            document.getElementById('tab-read').classList.toggle('active', tab === 'read');
            renderUI();
        }}

        function switchSourceFilter(sourceName) {{
            currentSource = sourceName;
            document.querySelectorAll('.source-chip').forEach(chip => {{
                chip.classList.toggle('active', chip.getAttribute('data-source') === sourceName);
            }});
            renderUI();
        }}

        function initSourceFilterChips() {{
            const cards = document.querySelectorAll('.card');
            const sources = new Set();
            cards.forEach(c => {{
                const src = c.getAttribute('data-source-name');
                if (src) sources.add(src);
            }});

            const filterBar = document.getElementById('source-filter-bar');
            let html = '<button class="source-chip active" data-source="ALL" onclick="switchSourceFilter(\\'ALL\\')">✨ すべて</button>';
            
            sources.forEach(src => {{
                html += `<button class="source-chip" data-source="${{src}}" onclick="switchSourceFilter('${{src}}')">${{src}}</button>`;
            }});

            filterBar.innerHTML = html;
        }}

        function renderUI() {{
            const readIds = getReadIds();
            const cards = document.querySelectorAll('.card');
            
            let top10VisibleCount = 0;
            let unreadVisibleCount = 0;
            let readVisibleCount = 0;

            cards.forEach(card => {{
                const id = card.getAttribute('data-article-id');
                const srcName = card.getAttribute('data-source-name');
                const isTop10 = card.getAttribute('data-is-top10') === 'true';
                const isRead = readIds.includes(id);

                const btnText = card.querySelector('.btn-text');
                const btnIcon = card.querySelector('.btn-icon');
                const btn = card.querySelector('.mark-read-btn');

                if (isRead) {{
                    readVisibleCount++;
                    if (btnText) btnText.textContent = '未読に戻す';
                    if (btnIcon) btnIcon.textContent = '↩';
                    if (btn) btn.style.background = 'rgba(148, 163, 184, 0.15)';
                    if (btn) btn.style.color = '#94a3b8';
                }} else {{
                    unreadVisibleCount++;
                    if (btnText) btnText.textContent = '既読にする';
                    if (btnIcon) btnIcon.textContent = '✓';
                    if (btn) btn.style.background = 'rgba(34, 197, 94, 0.15)';
                    if (btn) btn.style.color = '#4ade80';
                }}

                if (isTop10 && !isRead) {{
                    top10VisibleCount++;
                }}

                let matchesMainTab = false;
                if (currentMainTab === 'top10') {{
                    matchesMainTab = isTop10;
                }} else if (currentMainTab === 'unread') {{
                    matchesMainTab = !isRead;
                }} else if (currentMainTab === 'read') {{
                    matchesMainTab = isRead;
                }}

                const matchesSource = (currentSource === 'ALL') || (srcName === currentSource);

                if (matchesMainTab && matchesSource) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            document.getElementById('top10-count').textContent = top10VisibleCount;
            document.getElementById('unread-count').textContent = unreadVisibleCount;
            document.getElementById('read-count').textContent = readVisibleCount;

            const visibleCards = Array.from(cards).filter(c => c.style.display !== 'none');
            const emptyState = document.getElementById('empty-state');
            const emptyMsg = document.getElementById('empty-msg');

            if (visibleCards.length === 0) {{
                emptyState.style.display = 'block';
                if (currentMainTab === 'top10') {{
                    emptyMsg.textContent = '注目TOP10の未読ニュースはありません！🎉';
                }} else if (currentMainTab === 'unread') {{
                    emptyMsg.textContent = currentSource === 'ALL' 
                        ? 'すべての未読ニュースを読み終えました！🎉' 
                        : `「${{currentSource}}」の未読ニュースはありません🎉`;
                }} else {{
                    emptyMsg.textContent = '既読の記事はありません。';
                }}
            }} else {{
                emptyState.style.display = 'none';
            }}
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            initAuth();
            initSourceFilterChips();
            renderUI();
        }});
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(full_html)

    # JSONデータ保存
    latest_data = {
        "updated_at": now_jst.isoformat(),
        "articles": sorted_articles
    }
    with open(os.path.join(output_dir, "data", "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest_data, f, ensure_ascii=False, indent=2)

    # Manifest 保存
    manifest_data = {
        "name": "AI News Digest",
        "short_name": "AI Digest",
        "description": "毎朝更新される最新AIニュース日本語要約アプリ",
        "start_url": "index.html",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a"
    }
    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Webアプリのビルド完了 (暗証番号保護機能: 000011)")
