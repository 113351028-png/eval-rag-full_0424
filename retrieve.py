import logging
import os
from typing import Any, Dict, List, Tuple

os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage, Document
from langchain.vectorstores import Chroma
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama

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

        chat: ChatOllama = ChatOllama(model=OLLAMA_MODEL, temperature=0)
        message: HumanMessage = HumanMessage(content=final_prompt)
        response: AIMessage = chat.invoke([message])

        # IMPORTANT: Do not json.dumps this object.
        # promptfoo receives this as output, then:
        # - defaultTest.options.transform extracts output.answer for normal assertions
        # - contextTransform extracts output.context for context-faithfulness
        return {
            "output": {
                "answer": str(response.content),
                "context": str(context_text),
                "retrievedDocs": [
                    {
                        "content": doc.page_content,
                        "score": score,
                        "metadata": doc.metadata,
                    }
                    for doc, score in docs_chroma
                ],
            }
        }
    except Exception as e:
        logging.error(f"Error in call_api: {str(e)}")
        raise
