from langchain_community.document_loaders import TextLoader

def loadTxt(filePath : str):
    loader = TextLoader(filePath,encoding="utf-8")
    return loader.load()
