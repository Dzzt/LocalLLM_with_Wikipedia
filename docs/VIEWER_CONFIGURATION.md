# Article Viewer Configuration

`LocalLLM_with_Wikipedia`
は、回答に使用したWikipedia記事を外部Viewerで開けます。

ViewerはRAG検索とは独立しており、Web
UIから渡す基本情報は記事タイトルです。

## Viewer backend

利用できるbackend:

``` text
jsonl
kiwix
```

通常はJSONL Viewerを使用し、必要に応じてKiwixへ切り替えます。

## 想定配置

``` text
RAG/
├─ LocalLLM_with_Wikipedia/
│  ├─ webui.py
│  └─ wikirag/
│     ├─ article_viewers.py
│     └─ viewer_config.py
├─ tools/
│  ├─ wikipedia_viewer/
│  │  ├─ wikipedia_jsonl_viewer.py
│  │  └─ ...
│  └─ kiwix/
│     ├─ kiwix-serve.exe
│     └─ ...
└─ data/
   ├─ wikipedia_viewer/
   │  └─ wikipedia_articles.sqlite3
   └─ kiwix/
      └─ wikipedia_ja_all_nopic_YYYY-MM.zim
```

## JSONL Viewer

JSONL
Viewerは、RAGのチャンクを結合するのではなく、別途構築した記事単位SQLiteから元記事全文を表示します。

概念上の呼び出しは次の形です。

``` text
py wikipedia_jsonl_viewer.py
    --db <wikipedia_articles.sqlite3>
    --title <article title>
```

記事本文の取得・タイトル検索・表示UIはViewer側の責務です。

本体側は記事タイトルを渡すだけで、Viewer用SQLiteを直接検索しません。

## Kiwix Viewer

Kiwix backendを選択すると、`kiwix-serve`
を起動し、記事タイトルからKiwixのURLを生成して既定ブラウザで開きます。

``` cmd
python webui.py --viewer kiwix --open-browser
```

Kiwix固有の配置と動作については `KIWIX_SETUP.md` を参照してください。

## Viewerの切り替え

デフォルト:

``` cmd
python webui.py
```

Kiwix:

``` cmd
python webui.py --viewer kiwix --open-browser
```

起動スクリプトを使用する場合は、

``` text
start-rag.cmd
start-rag-kiwix.cmd
```

を用途に応じて使用します。

## 設計上の注意

-   RAG検索用 `metadata.sqlite` とViewer用 `wikipedia_articles.sqlite3`
    は別物です。
-   RAG側で記事全文を再構成しません。
-   Viewerの内部機能をRAG本体へ戻さないことを基本とします。
-   Kiwixはオプションであり、通常のJSONL
    Viewerを使う構成から独立させます。
