import chromadb
import uuid
from typing import List, Optional, Dict, Any
from schemas.memory import NewMemory


class MemoryStore:
    def __init__(self, db_path: str = "./vivarium_storage"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="agent_long_term_memory"
        )

    def add_memory(self, agent_name: str, memory: NewMemory):
        """Stores a specific structured memory."""
        self.collection.add(
            documents=[memory.content],
            metadatas=[
                {
                    "agent": agent_name,
                    "type": "fact",
                    "category": memory.category,
                    "subject": memory.subject,
                }
            ],
            ids=[str(uuid.uuid4())],
        )

    def add_memories(self, agent_name: str, memories: List[NewMemory]):
        """Batch stores multiple structured memories."""
        if not memories:
            return

        ids = [str(uuid.uuid4()) for _ in memories]
        documents = [m.content for m in memories]
        metadatas = [
            {
                "agent": agent_name,
                "type": "fact",
                "category": m.category,
                "subject": m.subject,
            }
            for m in memories
        ]

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)  # type: ignore

    def retrieve_relevant_memories(
        self, agent_name: str, query_text: str, limit: int = 5
    ) -> List[str]:
        """
        Semantic Search for context injection.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=limit,
            where={"agent": agent_name},
        )

        if results["documents"] and results["documents"][0]:
            return results["documents"][0]

        return []

    def retrieve_nearest_memory(
        self, agent_name: str, query_text: str, threshold_distance: float = 0.4
    ) -> Optional[Dict[str, Any]]:
        """
        Finds the single closest memory to check for duplicates.
        Returns details if closer than threshold, else None.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=1,
            where={"agent": agent_name},
        )

        if not results["ids"] or not results["ids"][0]:
            return None

        distance = results["distances"][0][0]  # type: ignore

        # ChromaDB Default: L2 distance (Lower is closer).
        # 0.0 = Identical. ~0.3-0.5 = Semantically similar. > 1.0 = Unrelated.
        if distance < threshold_distance:
            return {
                "id": results["ids"][0][0],
                "text": results["documents"][0][0],  # type: ignore
                "metadata": results["metadatas"][0][0],  # type: ignore
                "distance": distance,
            }
        return None

    def delete_memory(self, memory_id: str):
        self.collection.delete(ids=[memory_id])

    def reset_db(self):
        """Utility to clear database for testing."""
        self.client.delete_collection("agent_long_term_memory")
        self.collection = self.client.get_or_create_collection(
            name="agent_long_term_memory"
        )
