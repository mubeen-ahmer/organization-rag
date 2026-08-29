from src.retrieval.vector_retriever import get_vectorstore
from src.ingestion.ingest import ingestNewFiles
from src.generation.ragChain import route_and_ask

def main():
    print("Initializing Verano RAG...")
    vectorstore = get_vectorstore()

    print("Checking for new documents...")
    ingestNewFiles(vectorstore)

    print("\nReady! Ask questions about Verano Apparel. Type 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if not question:
            continue

        print("Thinking...")
        answer = route_and_ask(question)
        print(f"\nAssistant: {answer}\n")

if __name__ == "__main__":
    main()