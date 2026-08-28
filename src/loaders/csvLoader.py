import pandas as pd
from langchain_core.documents import Document

def loadCSV(path : str):
    df = pd.read_csv(path)
    # print(df)
    docs = []
    for i, row in df.iterrows():
        content = ", ".join(f"{col}: {row[col]}" for col in df.columns)
        docs.append(Document(page_content=content, metadata={"source": path, "row": i}))
        
    # print(docs)
    return docs
    
# loadCSV("data/raw/verano_assets_Q3_SALES.csv")
