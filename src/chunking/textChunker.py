import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
encoding = tiktoken.get_encoding("cl100k_base")

def _lengthFunction(text):
    return len(encoding.encode(text))


def chunkText(documents : list):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,          # now measured in TOKENS, not characters
        chunk_overlap=30,
        length_function=_lengthFunction
    )
    
    return splitter.split_documents(documents)



