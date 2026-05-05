import logging
import os
from typing import Any, Dict, List, Tuple

os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document
from langchain_chroma import Chroma

# 🌟 更新：從專屬的 langchain_ollama 套件中引入 Ollama 模組
from langchain_ollama import OllamaEmbeddings, ChatOllama

# ----------------------------------------------------------------------------
# retrieve.py 功能說明
#
# 1. 初始化本地 Chroma 向量資料庫，persist_directory 指向 db/。
# 2. 使用 nomic-embed-text 嵌入模型將 query 轉成 embedding。
# 3. 透過 similarity_search_with_score 依 topK 取回相關文件及分數。
# 4. 將檢索到的 document 內容合併成 context，並套入 prompt template。
# 5. 使用 ChatOllama 連到 llama3 取得回答，temperature 設為 0 以提高穩定性。
# 6. 回傳 output 與 metadata，metadata 含 context 與 retrievedDocs 供 promptfoo assert 使用。
# ----------------------------------------------------------------------------

# Constants
CHROMA_PATH: str = "db"
OLLAMA_MODEL: str = "llama3"
OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

# Initialize embeddings and load the Chroma database
embeddings: OllamaEmbeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
db_chroma: Chroma = Chroma(
    collection_name="rag_collection",
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings,
)

PROMPT_TEMPLATE: str = """
Answer the question based only on the following context:
{context}
Answer the question based on the above context: {question}.
Provide a detailed answer.
Don't justify your answers.
Don't give information not mentioned in the CONTEXT INFORMATION.
Do not say "according to the context" or "mentioned in the context" or similar.
"""

def call_api(
    prompt: str, options: Dict[str, Any], context: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        k: int = options.get("config", {}).get("topK", 5)
        docs_chroma: List[Tuple[Document, float]] = (
            db_chroma.similarity_search_with_score(prompt, k=k)
        )

        if not docs_chroma:
            context_text = "No relevant context found."
        else:
            context_text = "\n\n".join(
                [doc.page_content for doc, _score in docs_chroma]
            )

        prompt_template: ChatPromptTemplate = ChatPromptTemplate.from_template(
            PROMPT_TEMPLATE
        )
        final_prompt: str = prompt_template.format(
            context=context_text, question=prompt
        )

        # 🤖 這裡的語法保持不變，但底層已經採用更穩定、效能更好的新版套件
        chat: ChatOllama = ChatOllama(model=OLLAMA_MODEL, temperature=0)
        message: HumanMessage = HumanMessage(content=final_prompt)
        response: AIMessage = chat.invoke([message])

        return {
            "output": str(response.content),
            "metadata": {
                "context": str(context_text),
                "retrievedDocs": [
                    {
                        "content": doc.page_content,
                        "score": score,
                        "metadata": doc.metadata,
                    }
                    for doc, score in docs_chroma
                ],
            },
        }
    except Exception as e:
        logging.error(f"Error in call_api: {str(e)}")
        raise