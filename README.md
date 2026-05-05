# RAG SEC 操作指南

本專案示範一個以 SEC 10-Q PDF 為資料來源的本地 RAG 流程，使用 Ollama 提供 LLM 與 embedding model，ChromaDB 作為向量資料庫，並透過 promptfoo 進行自動化品質測試。

## 架構總覽

```text
PDF (AAPL/MSFT 10-Q)
  → ingest.py        # 下載 PDF、切塊、存入 ChromaDB
  → db/              # Chroma 向量資料庫（本地）
  → retrieve.py      # 接收查詢、向量搜尋、LLM 回答
  → promptfoo eval   # 自動化測試 RAG 品質
```

## 第一步：安裝 Ollama

macOS：

```bash
brew install ollama
```

Linux：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

啟動 Ollama（背景執行）：

```bash
ollama serve &
```

下載本專案需要的模型：

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

確認模型已下載：

```bash
ollama list
```

## 第二步：建立 Conda 環境

```bash
conda create -n rag-sec python=3.11 -y
conda activate rag-sec
```

## 第三步：安裝 Python 套件

請確認 `requirements.txt` 已包含本專案需要的 LangChain、ChromaDB、Ollama、PDF parser 與環境變數套件，並直接安裝：

```bash
pip install -r requirements.txt
```


## 第四步：確認 RAG Provider

`retrieve.py` 是 promptfoo 會呼叫的 Python provider，負責：

1. 載入本地 `db/` Chroma collection。
2. 使用 `langchain_ollama.OllamaEmbeddings` 和 `nomic-embed-text` 轉換 query 成 embedding。
3. 依照 `topK` 取回最相關的文件片段。
4. 將文件片段組成 `context`，並透過 `ChatPromptTemplate` 產生最終 prompt。
5. 使用 `langchain_ollama.ChatOllama` 連到本地 `llama3` 模型產生回答。
6. 回傳 `output` 與 `metadata`，包含檢索到的 `context` 和 `retrievedDocs`，供 promptfoo assert 使用。

### `retrieve.py` 說明

`retrieve.py` 的主要流程如下：

- 初始化 `Chroma` 資料庫，並設定 `persist_directory` 為 `db`。
- 執行 `similarity_search_with_score` 取得最相關 `topK` 文件。
- 將結果合併成一段字串 `context_text`，作為 prompt 的檢索內容。
- 使用 `ChatOllama` 呼叫 `llama3` 模型產生回答，溫度設為 `0` 以提高穩定性。
- 回傳字典格式的結果：
  - `output`: 模型回答文字
  - `metadata.context`: 使用到的檢索內容
  - `metadata.retrievedDocs`: 每筆文件內容、分數、metadata

> 這樣設計可以讓 `promptfoo` 直接斷言回答內容與檢索來源，並且保留檢索結果供後續分析。

## 第五步：建立向量資料庫

```bash
python ingest.py
```

執行完成後會產生 `db/` 資料夾。

若需要重新建立資料庫，請先刪除舊資料後再重跑 ingestion：

```bash
rm -rf db/
python ingest.py
```

## 第六步：安裝 promptfoo

先用 Conda 安裝 Node.js：

```bash
conda install -c conda-forge nodejs -y
```

再安裝 promptfoo：

```bash
npm install -g promptfoo
```

## 第七步：執行測試

```bash
promptfoo eval -c promptfooconfig.with-asserts.yaml
```

查看測試結果：

```bash
promptfoo view
```

## 完成後的目錄結構
```text
專案目錄/
├── ingest.py
├── retrieve.py
├── requirements.txt
├── promptfooconfig.with-asserts.yaml
└── db/                   # ingest.py 執行後產生
    └── chroma.sqlite3
```

## 注意事項

- 執行 `python ingest.py` 前，請確認 Ollama 已啟動，且 `nomic-embed-text` 已下載。
- 執行 promptfoo 測試前，請確認 `db/` 已存在，否則 `retrieve.py` 無法檢索資料。
- 本專案使用本地模型與本地向量資料庫，不需要額外設定雲端 API key。
- 若修改 `retrieve.py` 的輸出格式，需同步確認 `promptfooconfig.with-asserts.yaml` 中的 `transform` 與 `contextTransform` 設定。
