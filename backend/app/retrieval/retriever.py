"""Semantic retriever: embed query -> vector search -> top-k chunks."""
from app.core.config import settings
from app.embeddings.sentence_transformer import get_embedding_service
from app.vectorstore.chroma_store import get_vector_store


class Retriever:
    def retrieve(
        self, question: str, top_k: int | None = None,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        k = top_k or settings.TOP_K
        query_vector = get_embedding_service().embed_query(question)
        return get_vector_store().similarity_search(
            query_vector, top_k=k, document_ids=document_ids or None
        )


def get_retriever() -> Retriever:
    return Retriever()
