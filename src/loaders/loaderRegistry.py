import os
from src.loaders.txtLoader import loadTxt
from src.loaders.pdfLoader import loadPdf
from src.loaders.docxLoader import loadDocx

LOADER_MAP = {
    ".txt": loadTxt,
    ".pdf": loadPdf,
    ".docx": loadDocx
}

def loadFile(path : str):
    ext = os.path.splitext(path)[1].lower()
    loaderFunc = LOADER_MAP.get(ext)
    if loaderFunc is None :
        raise ValueError(f"No loader registered for extension: {ext}")
    return loaderFunc(path)