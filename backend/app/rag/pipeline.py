"""RAG pipeline orchestrator: embed -> retrieve -> rerank -> context -> LLM -> cite."""
from app.core.config import settings
from app.core.logging import get_logger
from app.generation.prompts import build_prompt
from app.generation.providers.factory import get_llm_provider
from app.rag.citations import build_citations
from app.rag.context_builder import build_context
from app.retrieval.reranker import rerank
from app.retrieval.retriever import get_retriever

log = get_logger(__name__)

NO_CONTEXT_MESSAGE = (
    "I couldn't find enough information in the provided documents "
    "to answer this question."
)


class RAGPipeline:
    def ask(
        self,
        question: str,
        document_ids: list[str] | None = None,
        top_k: int | None = None,
    ) -> dict:
        k = top_k or settings.TOP_K
        retriever = get_retriever()

        # 1-2. Embed query + retrieve top-k chunks.
        retrieved = retriever.retrieve(question, top_k=k, document_ids=document_ids)

        # 3. Rerank / threshold filter (never send unrelated chunks to the LLM).
        kept = rerank(question, retrieved, final_k=k, min_score=settings.MIN_RETRIEVAL_SCORE)

        avg_all = round(sum(r.get("score", 0.0) for r in retrieved) / len(retrieved), 4) if retrieved else 0.0

        # 4. Out-of-context handling: do not call the LLM with nothing useful.
        if not kept:
            return {
                "answer": NO_CONTEXT_MESSAGE,
                "sources": build_citations(retrieved[:k]),
                "retrieval_metadata": {
                    "top_k": k, "retrieved_count": len(retrieved), "average_score": avg_all,
                },
                "context": "",
                "provider": get_llm_provider().name,
                "abstained": True,
            }

        # 5-6. Build context + prompt, generate, attach citations.
        context = build_context(kept)
        prompt = build_prompt(question, context)
        provider = get_llm_provider()
        log.info("query -> top_k=%d kept=%d provider=%s", k, len(kept), provider.name)
        answer = provider.generate(prompt)

        avg_kept = round(sum(r.get("score", 0.0) for r in kept) / len(kept), 4)
        return {
            "answer": answer,
            "sources": build_citations(kept),
            "retrieval_metadata": {
                "top_k": k, "retrieved_count": len(retrieved), "average_score": avg_kept,
            },
            "context": context,
            "provider": provider.name,
            "abstained": False,
        }

    def ask_baseline(self, question: str) -> dict:
        """LLM-only baseline: question -> LLM -> answer (no retrieval)."""
        provider = get_llm_provider()
        answer = provider.generate(question)
        return {"answer": answer, "provider": provider.name}


def get_pipeline() -> RAGPipeline:
    return RAGPipeline()
