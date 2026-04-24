# Promptfoo Config 快速指南

## Config 結構一覽

| 必填 | 欄位 | 說明 |
|:--:|------|------|
| ✓ | `prompts` | 測試的 Prompt 模板 |
| ✓ | `providers` | 要測試的 LLM 模型 |
| ✓ | `tests` | 測試案例清單 |
| - | `defaultTest` | 預設選項 |
| - | `assertionTemplates` | 可重用的斷言模板 |
| - | `derivedMetrics` | 衍生複合分數 |

---

## 最小 Config 示例

```yaml
description: 'RAG 評估測試'

prompts:
  - '{{question}}'

providers:
  - openai:gpt-4
  - ollama:chat:llama3

defaultTest:
  options:
    provider: openai:gpt-4-mini

tests:
  - vars:
      question: '台北是哪個國家的首都？'
    threshold: 0.8
    assert:
      - type: contains
        value: '台灣'
        metric: accuracy
      - type: llm-rubric
        value: '回應語氣友善'
        metric: tone
```

---

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

- [ASSERTION_TYPES.md](./ASSERTION_TYPES.md) - 完整的斷言類型說明
- `promptfooconfig.yaml` - 實際配置檔案範例
- `promptfooconfig.with-asserts.yaml` - 進階範例


