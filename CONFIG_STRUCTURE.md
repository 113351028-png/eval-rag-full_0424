# Promptfoo Config 快速指南

## 最小 Config 示例

```yaml
# description：本次評估任務的名稱或說明，會顯示在 promptfoo 報告中
description: 'RAG 評估測試'

# prompts：定義要送給模型的 prompt 模板
# '{{question}}' 代表會從 tests.vars.question 取值後代入
prompts:
  - '{{question}}'

# providers：定義要被測試的模型或服務
# 每個 provider 都會跑同一組 prompts 和 tests，用來比較不同模型表現
providers:
  - openai:gpt-4              # 使用 OpenAI GPT-4 作為被測模型
  - ollama:chat:llama3        # 使用本地 Ollama llama3 作為被測模型

# defaultTest：所有 tests 的預設設定
# 若單一 test 沒有另外指定 options，就會使用這裡的設定
defaultTest:
  options:
    provider: openai:gpt-4-mini   # 指定預設的評分模型，常用於 llm-rubric 等 LLM 評分型 assertion

# tests：測試案例清單
# 每一個 test 代表一個問題、輸入情境或驗證任務
tests:
  - vars:
      # vars：定義要代入 prompt 模板的變數
      # 這裡的 question 會對應到 prompts 裡的 {{question}}
      question: '台北是哪個國家的首都？'

    # threshold：此測試案例的通過門檻
    # 0.8 代表整體 assertion 分數至少要達到 80% 才算通過
    threshold: 0.8

    # assert：驗證規則清單
    # 用來判斷模型輸出是否符合期待
    assert:
      - type: contains          # contains：檢查模型回答是否包含指定字串
        value: '台灣'           # value：期望在模型輸出中出現的內容
        metric: accuracy        # metric：此 assertion 歸類到哪個評估指標，方便報告統計

      - type: llm-rubric        # llm-rubric：使用 LLM 判斷回答是否符合描述性標準
        value: '回應語氣友善'    # value：給評分模型的判斷標準
        metric: tone            # metric：將此 assertion 歸類為 tone 指標

## 核心欄位說明

### Prompts（模板）
- 支援檔案引入：`file://prompt.txt`
- 支援內聯：`'{{question}}'`
- 支援多個模板

### Providers（模型）
```
openai:gpt-4, openai:gpt-3.5-turbo
ollama:chat:llama3, ollama:chat:mistral
http://localhost:8000/v1/completions（自訂）
```

### Tests 結構
- `vars`: 測試變數（必填）
- `threshold`: 通過門檻（0.8 = 80%）
- `assert`: 驗證規則清單

### Assert 常用類型
- `contains`: 檢查是否包含字串
- `icontains`: 忽略大小寫的包含
- `llm-rubric`: LLM 評分判斷
- `context-faithfulness`: 上下文一致性檢查
- 詳見 [ASSERTION_TYPES.md](./ASSERTION_TYPES.md)

---

## 執行命令

```bash
# 執行評估
promptfoo eval -c promptfooconfig.yaml

# 檢視結果
promptfoo view

# 只測試特定提示
promptfoo eval -c promptfooconfig.yaml --prompt 0

# 詳細模式
promptfoo eval -c promptfooconfig.yaml --verbose
```

---

## 工作流程

```
config → 遍歷每個 test → 填入 vars → 選擇 provider 
  ↓
發送給 LLM → 接收回應 → 執行 assert 驗證 → 計算 threshold
  ↓
輸出測試報告
```

---

## 常用設定

### 多模型比較
```yaml
providers:
  - ollama:chat:llama3
  - openai:gpt-4
  - openai:gpt-3.5-turbo
```
同一測試用多個模型執行，可比較結果品質

### 覆蓋預設 Provider
```yaml
tests:
  - vars:
      question: '複雜問題'
    options:
      provider: openai:gpt-4  # 只有此測試用 GPT-4
    assert:
      - type: llm-rubric
        value: '回答邏輯清晰'
```

---

## 詳細資源
- `promptfooconfig.with-asserts.yaml` - 進階範例


