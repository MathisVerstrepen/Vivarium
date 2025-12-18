import chromadb
import uuid
from typing import List


class MemoryStore:
    def __init__(self, db_path: str = "./vivarium_storage"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="agent_long_term_memory"
        )

    def add_memory(self, agent_name: str, text: str):
        """Stores a specific fact/memory for an agent."""
        self.collection.add(
            documents=[text],
            metadatas=[{"agent": agent_name, "type": "fact"}],
            ids=[str(uuid.uuid4())],
        )

    def add_memories(self, agent_name: str, texts: List[str]):
        """Batch stores multiple facts."""
        if not texts:
            return

        ids = [str(uuid.uuid4()) for _ in texts]
        metadatas = [{"agent": agent_name, "type": "fact"} for _ in texts]

        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)  # type: ignore

    def retrieve_relevant_memories(
        self, agent_name: str, query_text: str, limit: int = 5
    ) -> List[str]:
        """
        Semantic Search: Finds memories belonging to 'agent_name' that are
        semantically similar to 'query_text'.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=limit,
            where={"agent": agent_name},
        )

        if results["documents"] and results["documents"][0]:
            return results["documents"][0]

        return []

    def reset_db(self):
        """Utility to clear database for testing."""
        self.client.delete_collection("agent_long_term_memory")
        self.collection = self.client.get_or_create_collection(
            name="agent_long_term_memory"
        )
