# ⚡ AI News Digest (完全無料・毎朝全自動)

毎朝7:00(JST)にAIの最新ニュースを自動収集し、Google Gemini APIで日本語要約。
スマホ最適化Webアプリ（GitHub Pages）を自動更新し、Discordにピックアップ通知を配信する**完全無料（0円）システム**です。

---

## 📱 スマホ（iPhone）での表示イメージ & アプリ化
- **Webアプリ**: Safariで開いて「共有」アイコン ➔ **「ホーム画面に追加」** を選択すると、専用アプリのように全画面で起動できます。
- **Discord通知**: 毎朝7時に今朝のハイライトTOP3とWebアプリへのリンクがDiscordに届きます。

---

## 🚀 5分でできるセットアップ手順

### 1. 無料APIキー・URLの取得

1. **Google Gemini APIキー (無料)**
   - [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス。
   - 「Create API key」をクリックしてキーをコピー。

2. **Discord Webhook URL (無料)**
   - Discordの任意のチャンネル設定 ➔ **「連携サービス」** ➔ **「ウェブフック」** を作成し、WebフックURLをコピー。

---

### 2. GitHub Secrets の設定

作成したGitHubリポジトリの **[Settings]** ➔ **[Secrets and variables]** ➔ **[Actions]** ➔ **[New repository secret]** から以下の3つを登録します。

| Secret名 | 設定する値 |
| :--- | :--- |
| `GEMINI_API_KEY` | 取得した Google Gemini APIキー |
| `DISCORD_WEBHOOK_URL` | 取得した Discord Webhook URL |
| `WEB_APP_URL` | あなたのGitHub PagesのURL（例: `https://<ユーザー名>.github.io/Antigravity_AI_news/`） |

---

### 3. GitHub Pages の有効化

1. 初回ワークフロー実行後（または手動実行後）、リポジトリの **[Settings]** ➔ **[Pages]** を開く。
2. **Source** を `Deploy from a branch` に設定。
3. ブランチを **`gh-pages`** / **`/(root)`** に設定して保存。

---

### 4. 手動テスト実行

リポジトリの **[Actions]** タブ ➔ **[Daily AI News Digest]** ➔ **[Run workflow]** をクリックすると、すぐに手動で収集・要約・Web更新・通知テストが実行できます。

---

## ⚙️ ニュース取得サイトの変更・追加方法

`sources.json` を編集してコミットするだけで、取得元サイトを自由にカスタマイズできます。

```json
[
  {
    "id": "itmedia_ai",
    "name": "ITmedia AI+",
    "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "category": "国内ニュース",
    "lang": "ja"
  }
]
```

---

## 🛠️ 技術スタック
- **Automation**: GitHub Actions (Cron: `0 22 * * *`)
- **AI Summary**: Google Gemini API (`gemini-1.5-flash` / `gemini-2.5-flash`)
- **Frontend**: HTML5, CSS3 (Glassmorphism Dark UI), PWA
- **Notification**: Discord Webhooks
