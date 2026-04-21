# akinguyen90.github.io

Aki Nguyen の個人サイト（CV兼ブログ）。

公開URL: https://akinguyen90.github.io/

## 構成

- `index.html` — トップページ
- `cv.html` — CV
- `blog.html` — ブログ記事一覧
- `posts/` — 各ブログ記事
- `assets/css/style.css` — スタイル

静的HTML/CSSのみで構築。ビルド不要で GitHub Pages にそのまま配信されます。

## 新しい記事を追加する

1. `posts/` 配下に新しい HTML ファイルを作成（`posts/hello-world.html` をテンプレートに）
2. `blog.html` と `index.html` の記事リストにリンクを追加
3. コミットしてプッシュ

## ローカル確認

```sh
python3 -m http.server 8000
```

`http://localhost:8000/` にアクセス。
