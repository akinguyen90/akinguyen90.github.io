# akinguyen90.github.io

Aki Nguyen の個人サイト（CV兼ブログ）。

公開URL: https://akinguyen90.github.io/

## 構成

- `index.html` — トップページ
- `cv.html` — CV
- `blog.html` — ブログ記事一覧
- `weather.html` — ベトナム主要都市の天気（毎時自動更新）
- `posts/` — 各ブログ記事
- `assets/css/style.css` — スタイル
- `assets/js/weather.js` — 天気ページの描画ロジック
- `data/weather.json` — 天気データ（GitHub Actionsが自動更新）
- `scripts/fetch_weather.py` — Open-Meteo API から天気を取得するスクリプト
- `.github/workflows/weather.yml` — 毎時1回 `fetch_weather.py` を走らせるワークフロー

静的HTML/CSSのみで構築。ビルド不要で GitHub Pages にそのまま配信されます。

## 天気データの更新

`Update Vietnam weather` ワークフローが毎時（`cron: "5 * * * *"`）実行され、
`data/weather.json` を更新します。差分がある場合のみ自動コミットされます。
手動で走らせたいときは Actions タブから `Run workflow` を実行、
またはローカルで以下を実行してください。

```sh
python3 scripts/fetch_weather.py
```

## 新しい記事を追加する

1. `posts/` 配下に新しい HTML ファイルを作成（`posts/hello-world.html` をテンプレートに）
2. `blog.html` と `index.html` の記事リストにリンクを追加
3. コミットしてプッシュ

## ローカル確認

```sh
python3 -m http.server 8000
```

`http://localhost:8000/` にアクセス。

## テスト

`tests/` 以下のユニットテストは標準ライブラリの `unittest` で実行できます。

```sh
python3 -m unittest discover -s tests -v
```

`.github/workflows/test.yml` が PR ごとに自動実行します。
