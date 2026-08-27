from langchain_community.document_loaders import PyMuPDFLoader

def loadPdf(path: str):
    loader = PyMuPDFLoader(path)
    docs = loader.load()

    for doc in docs:
        doc.metadata = {
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
        }

    return docs