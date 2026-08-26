# LocalLLM_with_RAG

Wikipediaのデータから作成したローカルRAGを検索し、その検索結果をOllama上のローカルLLMへ渡して回答を生成するWeb
UIです。

このリポジトリは **RAGを実際に検索してLLMを動かす部分**
を担当します。Wikipediaダンプの変換や、FAISS /
SQLiteインデックスの生成は別プロジェクトで行います。

``` text
Wikipedia XML dump
        │
        ▼
wikipediadump_xml-to-jsonl
        │
        │ JSONL (.bz2)
        ▼
generate-RAG-from-jsonl
        │
        │ FAISS + SQLite + vector data
        ▼
LocalLLM_with_RAG
        │
        ├─ RAG検索
        ├─ Ollamaで回答生成
        └─ 参照したWikipedia記事をViewerで表示
```

------------------------------------------------------------------------

## 1. セットアップ

### 必要なもの

このシステムはWindows上での利用を前提にしています。

最低限、次の環境が必要です。

-   Python
-   Ollama
-   Pythonから利用できる `ollama`
-   NumPy
-   FAISS
-   `generate-RAG-from-jsonl` で生成済みのRAGデータ
-   Ollamaに登録済みのEmbeddingモデル
-   回答生成に使用するOllamaモデル

現在のRAGは `ruri-v3`
系のEmbedding設定で生成したデータを前提としています。検索時にも、インデックス生成時と同じEmbeddingモデル・次元数・query
prefixを使用する必要があります。

回答生成用モデルはWeb UIから選択できます。

> **注意**
>
> このリポジトリだけではWikipediaデータからRAGを生成できません。
> RAGデータの作成には `generate-RAG-from-jsonl` を使用してください。

### 基本的なディレクトリ構成

3つのリポジトリ、生成データ、外部Viewerを次のように並べる構成を想定しています。

``` text
RAG/
├─ wikipediadump_xml-to-jsonl/
├─ generate-RAG-from-jsonl/
├─ LocalLLM_with_RAG/
│  ├─ webui.py
│  ├─ start-rag.cmd
│  ├─ start-rag-kiwix.cmd
│  ├─ prompts/
│  ├─ static/
│  ├─ templates/
│  ├─ wikirag/
│  └─ docs/
│
├─ data/
│  ├─ index/
│  ├─ wikipedia_viewer/
│  │  └─ wikipedia_articles.sqlite3
│  └─ kiwix/
│     └─ wikipedia_ja_all_nopic_YYYY-MM.zim
│
└─ tools/
   ├─ wikipedia_viewer/
   │  └─ wikipedia_jsonl_viewer.py
   └─ kiwix/
      ├─ kiwix-serve.exe
      └─ Kiwix Toolsの関連ファイル
```

`LocalLLM_with_RAG` から見ると、

``` text
../data/index
../data/wikipedia_viewer
../data/kiwix
../tools/wikipedia_viewer
../tools/kiwix
```

を参照します。

------------------------------------------------------------------------

## 2. RAGデータを配置する

`generate-RAG-from-jsonl` で生成したproduction indexを、

``` text
RAG/data/index/
```

へ配置します。

`LocalLLM_with_RAG/webui.py` はデフォルトで、

``` text
../data/index
```

を検索インデックスとして読み込みます。

このフォルダには少なくとも、生成処理によって作られた
`config.json`、`metadata.sqlite`、FAISS shard、shard
manifest、および設定に応じたvectorデータが存在する構成になります。

ファイルを個別に手作業で作るのではなく、`generate-RAG-from-jsonl`
の出力一式をそのまま使用することを想定しています。

------------------------------------------------------------------------

## 3. Ollamaを準備する

Ollamaを起動し、次の2種類のモデルを利用できる状態にします。

### Embeddingモデル

RAG生成時に使用したものと同じEmbeddingモデルが必要です。

検索質問は実行時にEmbeddingされ、そのベクトルをFAISS
indexと比較します。そのため、RAG生成時と検索時でEmbedding設定を変えることはできません。

### 回答生成用LLM

回答生成用モデルはWeb UIの **Model** から選択します。

UIはOllamaに登録されているモデル一覧を取得し、Embedding用と思われるモデルを除いて表示します。

デフォルトモデルは `webui.py`
で指定されていますが、UI上で別のモデルを選択できます。

------------------------------------------------------------------------

## 4. 起動する

### 通常起動

JSONL Viewerを記事Viewerとして使う場合は、

``` cmd
start-rag.cmd
```

を実行します。

直接Pythonから起動する場合は、

``` cmd
python webui.py --viewer jsonl --open-browser
```

です。

デフォルトでは、

``` text
http://127.0.0.1:8765
```

でWeb UIが起動し、ブラウザが開きます。

### Kiwixを使う場合

Kiwix Viewerを使う場合は、

``` cmd
start-rag-kiwix.cmd
```

または、

``` cmd
python webui.py --viewer kiwix
```

で起動します。

Kiwixを使うには、後述する `tools/kiwix` と `data/kiwix`
の準備が必要です。

------------------------------------------------------------------------

## 5. 基本的な使い方

Web UIを開くと、質問入力欄と検索・生成パラメータが表示されます。

基本的には、

1.  **Question** に質問を書く
2.  **Model** で回答に使うOllamaモデルを選ぶ
3.  必要なら **Search mode** を変更する
4.  **Ask** を押す

だけで使用できます。

回答の下には、検索時間、生成時間、コンテキスト文字数、token数などの情報が表示されます。

### Referenced articles

回答下部の **Referenced articles**
を開くと、RAG検索で参照したWikipedia記事が記事単位で表示されます。

記事タイトルをクリックすると、選択しているArticle
Viewerで元記事を開きます。

RAGのチャンクを無理に結合して「元記事らしいもの」を作るのではなく、元データ側の記事を別Viewerで表示する設計です。

### 終了

Web UIの **Quit** ボタンで終了できます。

通常起動では、Web
UIを表示しているブラウザページが閉じられたことも監視しており、ブラウザセッションが終了するとWebサーバーも終了します。

------------------------------------------------------------------------

## 6. Search mode

通常は `article_focus` または `auto` を使用します。

  モード            用途
  ----------------- ----------------------------------------------------
  `article_focus`   質問先頭から記事を特定し、その記事内を重点的に検索
  `auto`            記事特定とWikipedia全体検索を自動的に組み合わせる
  `legacy_auto`     旧auto方式との比較・検証
  `strict`          対応する記事を確定できた場合だけ検索
  `balanced`        本命記事と関連する別記事を組み合わせる
  `discovery`       Wikipedia全体を横断して関連情報を探す

検索方法を詳しく知りたい場合は、

``` text
docs/SEARCH_MODES.md
docs/SEARCH_DESIGN.md
```

を参照してください。

------------------------------------------------------------------------

# data フォルダ

`data` はGitリポジトリの外に置く、大容量データ用のフォルダです。

``` text
data/
├─ index/
├─ wikipedia_viewer/
│  └─ wikipedia_articles.sqlite3
└─ kiwix/
   └─ wikipedia_ja_all_nopic_YYYY-MM.zim
```

## `data/index/`

RAG検索本体が使用するデータです。

`generate-RAG-from-jsonl` が生成したFAISS
index、検索用SQLite、vectorデータ、設定ファイルなどをまとめて配置します。

`webui.py` → `wikirag/search_engine.py` がこのフォルダを読み込みます。

## `data/wikipedia_viewer/`

JSONL Viewer専用のデータです。

``` text
wikipedia_articles.sqlite3
```

は、Wikipediaの元JSONLを記事単位で閲覧するためのSQLiteデータベースです。

これはRAG検索用の、

``` text
data/index/metadata.sqlite
```

とは別物です。

-   `metadata.sqlite` : RAG検索用
-   `wikipedia_articles.sqlite3` : 元記事閲覧用

という役割分担です。

## `data/kiwix/`

Kiwixで使用するZIMファイルを置きます。

例:

``` text
wikipedia_ja_all_nopic_2026-06.zim
```

Kiwixを使わない場合は不要です。

------------------------------------------------------------------------

# tools フォルダ

`tools` には、本体とは独立した補助プログラムを置きます。

``` text
tools/
├─ wikipedia_viewer/
└─ kiwix/
```

## `tools/wikipedia_viewer/`

Wikipedia JSONLから作成した記事データベースを表示する専用Viewerです。

中心となるスクリプトは、

``` text
wikipedia_jsonl_viewer.py
```

です。

RAG本体は記事タイトルをこのViewerへ渡します。

概念的には次のように呼び出しています。

``` cmd
py wikipedia_jsonl_viewer.py --db <database> --title "<記事タイトル>"
```

Viewer自身がSQLiteから記事を検索し、全文を表示します。

## `tools/kiwix/`

KiwixをArticle Viewerとして使う場合のKiwix Toolsを置きます。

``` text
kiwix-serve.exe
```

と、その実行に必要な関連ファイルを同じフォルダへ配置します。

ZIM本体は `tools` ではなく、

``` text
data/kiwix/
```

へ置きます。

Kiwixの詳細は、

``` text
docs/KIWIX_SETUP.md
```

を参照してください。

------------------------------------------------------------------------

# LocalLLM_with_RAG の各フォルダ

## `wikirag/`

RAG検索とArticle Viewer連携のPythonコードです。

### `search_engine.py`

検索処理の中心です。

主に、

-   `config.json` の読み込み
-   `metadata.sqlite` の読み込み
-   FAISS indexの読み込み
-   質問Embedding
-   タイトル一致判定
-   article focus
-   記事内検索
-   vector / lexical情報を使ったランキング
-   検索結果の生成

を担当します。

Wikipediaでは記事タイトルそのものがEmbeddingへ強く影響するため、単純に「質問に近いチャンク」を探すだけではなく、

``` text
どの記事か
    ↓
記事内のどこか
```

という二段階の考え方を取り入れています。

詳しくは `docs/SEARCH_DESIGN.md` を参照してください。

### `embedding.py`

検索質問をEmbedding vectorへ変換します。

RAG生成側にもEmbedding処理がありますが、本体でも検索時に質問をベクトル化する必要があるため、このファイルが必要です。

`config.json` に記録されたEmbeddingモデル、次元数、query
prefixなどを利用します。

### `models.py`

`BuildConfig`
やチャンクなど、RAGデータの構造を表すPythonのデータクラスを定義しています。

名前に `BuildConfig` が含まれていますが、本体でも生成済みindexの
`config.json` を正しく解釈するために使用します。

### `article_viewers.py`

RAG本体と記事Viewerの間をつなぎます。

現在は、

``` text
jsonl
kiwix
```

の2種類のbackendがあります。

JSONL Viewerの場合は外部Pythonスクリプトを起動し、Kiwixの場合は
`kiwix-serve` を管理してブラウザで記事を開きます。

### `viewer_config.py`

Article Viewerが使う外部ファイルの場所をまとめています。

主に、

``` text
RAG/tools/wikipedia_viewer
RAG/data/wikipedia_viewer
RAG/tools/kiwix
RAG/data/kiwix
```

へのパスを定義します。

Viewer関連の配置を変える場合は、まずこのファイルを確認してください。

### `utils.py`

JSON読み込み、ログ設定、Wikipediaタイトルの正規化など、複数の処理から使う小さな共通関数をまとめています。

------------------------------------------------------------------------

## `prompts/`

検索結果をLLMへ渡す際のpromptをSearch modeごとに保存しています。

``` text
prompts/
├─ article_focus/
├─ auto/
├─ balanced/
├─ discovery/
├─ legacy_auto/
└─ strict/
```

各モードには、

``` text
system.txt
user.txt
```

があります。

検索アルゴリズムとLLMへの指示を分離するため、promptはPythonコードへ直接書き込まず、このフォルダから読み込む構成です。

回答の仕方を調整したい場合はここを変更できますが、検索結果そのものが悪い場合はpromptより先に
`search_engine.py` 側の検索結果を確認する方が切り分けやすくなります。

------------------------------------------------------------------------

## `templates/`

Web UIのHTMLを置きます。

中心となるファイルは、

``` text
templates/index.html
```

です。

質問欄、モデル選択、Search
mode、各種パラメータ、回答表示欄など、画面の基本構造を定義しています。

------------------------------------------------------------------------

## `static/`

ブラウザ側で使うJavaScript、CSSなどを置きます。

### `app.js`

Web UIとPython側APIの通信を担当します。

主な処理は、

-   Ollamaモデル一覧の取得
-   質問の送信
-   回答の表示
-   Markdownのレンダリング
-   検索・生成metricsの表示
-   Referenced articlesの表示
-   記事Viewerを開く
-   Quit
-   ブラウザ終了監視用heartbeat

です。

### `style.css`

Web UIのレイアウトや表示スタイルを定義します。

### `marked.umd.min.js`

LLMが返したMarkdown形式の回答をブラウザ上でHTMLとして表示するためのMarkdown
rendererです。

------------------------------------------------------------------------

## `docs/`

システムの設計や、通常利用より詳しい情報を置きます。

``` text
docs/
├─ ARCHITECTURE.md
├─ SEARCH_DESIGN.md
├─ SEARCH_MODES.md
├─ VIEWER_CONFIGURATION.md
└─ KIWIX_SETUP.md
```

### `ARCHITECTURE.md`

3プロジェクトの関係、本体の責務、データフロー、Viewerとの役割分担など、システム全体の構造を説明します。

### `SEARCH_DESIGN.md`

現在の検索方式になった理由と、検索アルゴリズムの設計を説明します。

検索精度を改良するときは、まずこのファイルを読むことを想定しています。

### `SEARCH_MODES.md`

各Search modeの違いと使い分けを説明します。

### `VIEWER_CONFIGURATION.md`

JSONL Viewer / Kiwix Viewerの切り替えと配置について説明します。

### `KIWIX_SETUP.md`

Kiwix ToolsとZIMファイルの配置、Kiwix backendの使い方を説明します。

------------------------------------------------------------------------

# ルートにある主なファイル

## `webui.py`

アプリケーションの入口です。

主に、

-   コマンドライン引数の処理
-   HTTPサーバー
-   Web API
-   RAG検索の呼び出し
-   Ollamaへのchat request
-   コンテキスト構築
-   Article Viewerの呼び出し
-   ブラウザセッションの監視
-   終了処理

を担当します。

デフォルトでは、

``` text
Host: 127.0.0.1
Port: 8765
Index: ../data/index
Viewer: jsonl
```

で動作します。

主な起動オプションは、

``` text
--host
--port
--index
--prompts
--model
--context-chars
--viewer
--open-browser / --no-open-browser
```

です。

通常利用では `.cmd`
から起動すればよいため、これらを指定する必要はありません。

## `start-rag.cmd`

通常起動用です。

JSONL Viewerを使用して `webui.py` を起動します。

## `start-rag-kiwix.cmd`

Kiwix Viewerを使用する場合の起動用です。

------------------------------------------------------------------------

# リポジトリを変更するときの目安

どこを変更すればよいか迷った場合は、次を目安にできます。

  変更したいもの             主に見る場所
  -------------------------- -----------------------------------
  検索結果がおかしい         `wikirag/search_engine.py`
  Embedding処理              `wikirag/embedding.py`
  回答の指示                 `prompts/`
  Web画面                    `templates/index.html`, `static/`
  Ollamaへの問い合わせ       `webui.py`
  JSONL Viewer / Kiwix連携   `wikirag/article_viewers.py`
  Viewerやdataの配置         `wikirag/viewer_config.py`
  Search modeの意味          `docs/SEARCH_MODES.md`
  検索方式そのもの           `docs/SEARCH_DESIGN.md`

特に検索精度の問題では、

``` text
LLMの回答が悪い
```

のか、

``` text
LLMへ渡す前の検索結果が悪い
```

のかを分けて考えると原因を追いやすくなります。

------------------------------------------------------------------------

# 関連プロジェクト

このシステムは、Wikipediaデータ処理を3段階に分離しています。

### `wikipediadump_xml-to-jsonl`

WikipediaからダウンロードしたXML dumpをJSONL形式へ変換します。

### `generate-RAG-from-jsonl`

変換済みJSONLをチャンク化・Embeddingし、FAISS
indexとSQLiteデータベースを生成します。

### `LocalLLM_with_RAG`

生成済みRAGを検索し、OllamaのローカルLLMで回答を生成します。

この分離により、Wikipedia
dumpの更新、RAGの再生成、日常的な検索・LLM利用をそれぞれ独立して扱えるようにしています。
