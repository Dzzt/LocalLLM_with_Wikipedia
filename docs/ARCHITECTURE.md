# LocalLLM_with_RAG Architecture

## 目的

`LocalLLM_with_RAG` は、事前生成済みのWikipedia
RAGデータを検索し、Ollama上のローカルLLMへ参考資料として渡して回答を生成する実行システムです。

Wikipediaダンプの変換やRAGインデックスの生成は本リポジトリの責務ではありません。

``` text
wikipediadump_xml-to-jsonl
        │
        │ ja_wiki.jsonl.bz2
        ▼
generate-RAG-from-jsonl
        │
        │ FAISS + metadata.sqlite + vector data
        ▼
LocalLLM_with_RAG
        │
        ├─ RAG検索
        ├─ Ollamaによる回答生成
        └─ 参照記事を外部Viewerで表示
```

## 基本構成

``` text
LocalLLM_with_RAG/
├─ webui.py
├─ start-rag.cmd
├─ start-rag-kiwix.cmd
├─ wikirag/
│  ├─ article_viewers.py
│  ├─ embedding.py
│  ├─ models.py
│  ├─ search_engine.py
│  ├─ utils.py
│  └─ viewer_config.py
├─ prompts/
├─ templates/
├─ static/
├─ log/
└─ docs/
```

大容量データと外部ツールはリポジトリ外に置きます。

``` text
RAG/
├─ LocalLLM_with_RAG/
├─ data/
│  ├─ index/
│  ├─ wikipedia_viewer/
│  │  └─ wikipedia_articles.sqlite3
│  └─ kiwix/
│     └─ wikipedia_ja_all_nopic_YYYY-MM.zim
└─ tools/
   ├─ wikipedia_viewer/
   └─ kiwix/
```

## 実行時のデータフロー

``` text
質問
  │
  ▼
webui.py
  │
  ▼
SearchEngine
  ├─ 質問Embedding
  ├─ FAISS検索
  ├─ タイトル一致判定
  ├─ 記事内検索
  └─ ランキング
  │
  ▼
コンテキスト生成
  │
  ▼
Ollama
  │
  ▼
回答 + Referenced Articles
```

検索エンジンは「どの記事か」「記事内のどこか」までを決定し、LLMは得られた資料から回答を生成する役割に集中させます。

## RAGデータ

検索対象は `generate-RAG-from-jsonl` で生成済みのインデックスです。

本体側はインデックスを生成しません。EmbeddingモデルやFAISS形式を変更する場合も、生成側リポジトリで再構築します。

実行時には同じEmbedding空間で質問をベクトル化する必要があるため、query
embedding用の `wikirag/embedding.py` は本体にも存在します。

## 記事全文表示

RAG側は記事全文を結合して表示しません。

回答に使用した記事タイトルを `POST /api/open_article`
で受け取り、選択されたArticle Viewerへタイトルを渡します。

### JSONL Viewer

JSONLから別途生成された `wikipedia_articles.sqlite3`
を使う専用Viewerを外部プロセスとして起動します。

``` text
webui.py
   │ title
   ▼
tools/wikipedia_viewer/
   wikipedia_jsonl_viewer.py
   │
   ▼
data/wikipedia_viewer/wikipedia_articles.sqlite3
```

RAG検索用 `metadata.sqlite` と、全文閲覧用 `wikipedia_articles.sqlite3`
は目的が異なるため統合しません。

### Kiwix

Kiwixを選択した場合は `kiwix-serve` を起動し、Referenced
Articlesから該当記事をブラウザで開きます。

Kiwixはオプション機能であり、JSONL Viewerと共通のArticle
Viewerインターフェースから選択します。

詳細は `VIEWER_CONFIGURATION.md` と `KIWIX_SETUP.md`
を参照してください。

## 責務分離

### 本体が担当するもの

-   Web UI
-   質問受付
-   query embedding
-   FAISS / SQLiteを使ったRAG検索
-   コンテキスト生成
-   Ollamaへの問い合わせ
-   参照記事一覧
-   外部Article Viewerの呼び出し

### 本体が担当しないもの

-   Wikipedia XML dumpの解析
-   JSONL生成
-   production RAG indexの生成
-   Viewer用SQLiteの生成
-   Wikipedia記事全文のRAG側での再構成

## 開発時の原則

検索精度の問題が起きた場合、まず検索手順・タイトル特定・記事内検索・ランキング・コンテキスト生成を確認します。

EmbeddingやFAISS形式の変更は、production
index全体の再生成につながるため、改善効果が明確な場合に生成側プロジェクトで検討します。

動作している版を土台に局所的に変更し、既存の検索フォールバックとArticle
Viewerの責務分離を維持する方針を基本とします。
