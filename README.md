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
2. 使用 `nomic-embed-text` 將 query 轉成 embedding。
3. 依照 `topK` 取回相關文件片段。
4. 將 context 與問題組成 prompt。
5. 使用 `llama3` 產生回答。
6. 回傳回答與檢索 context，供 promptfoo assert 使用。

> 為避免 README 與原始碼重複，完整實作請直接查看 `retrieve.py`。

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
