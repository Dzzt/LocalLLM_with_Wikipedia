# Kiwix Setup

## 概要

KiwixをArticle Viewerとして選択すると、`LocalLLM_with_RAG`
の起動時に `kiwix-serve` を起動し、回答のReferenced
Articlesから記事をブラウザで開けます。

Kiwixは通常のWikipedia
Viewerとして、その後のリンク移動や検索にも利用できます。

## 想定配置

Kiwix本体とZIMはリポジトリ外へ置きます。

``` text
RAG/
├─ LocalLLM_with_RAG/
│  ├─ webui.py
│  ├─ start-rag-kiwix.cmd
│  └─ wikirag/
│     ├─ article_viewers.py
│     └─ viewer_config.py
├─ tools/
│  └─ kiwix/
│     ├─ kiwix-serve.exe
│     └─ Kiwix Tools付属DLL
└─ data/
   └─ kiwix/
      └─ wikipedia_ja_all_nopic_2026-06.zim
```

Kiwix Toolsに同梱されるDLL類は `kiwix-serve.exe`
と同じディレクトリに置きます。

## 起動

通常はKiwix用起動スクリプトを使用します。

``` cmd
start-rag-kiwix.cmd
```

または直接:

``` cmd
python webui.py --viewer kiwix --open-browser
```

現在の構成では、Kiwix関連のパス解決やbackend生成は
`wikirag/article_viewers.py` と `wikirag/viewer_config.py`
側へ分離し、`webui.py` にKiwix固有処理を散在させない設計です。

## ZIM

例:

``` text
data\kiwix\wikipedia_ja_all_nopic_2026-06.zim
```

記事を開く際は、Wikipedia記事タイトルの空白を `_` に正規化しURL
encodeしたうえでKiwix Viewerへ渡します。

Kiwix側で使用するbook名は、URL上では例えば次のようになります。

``` text
wikipedia_ja_all
```

実際のZIMファイル名には `_nopic_2026-06`
のようなvariantや日付が含まれる場合があるため、ファイル名全体をそのままURL上のbook名とみなさない点に注意してください。

## 動作

``` text
Referenced Articles
      │ click
      ▼
ArticleViewer
      │
      ▼
Kiwix Server
      │
      ▼
既定ブラウザの新しいタブ
```

Kiwix backendでは `kiwix-serve`
の実行ファイルとZIMファイルが存在することを起動時に確認します。

RAG本体終了時には、Article Viewerが所有するKiwix Serverも終了させます。

## JSONL Viewerとの関係

KiwixはJSONL Viewerの代替backendです。

``` text
--viewer jsonl
--viewer kiwix
```

のどちらを使っても、RAG検索側は記事タイトルをArticle
Viewerへ渡すだけです。

そのため、Kiwix連携の変更が検索アルゴリズムへ入り込まない構造を維持します。
