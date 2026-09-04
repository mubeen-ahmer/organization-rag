from bs4 import BeautifulSoup
from langchain_core.documents import Document

def loadHtml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    docs = []
    for section in soup.find_all("h2"):
        section_title = section.get_text(strip=True)
        container = section.find_next_sibling("div", class_="faq-item")
        # walk forward through faq-items until the next h2
        node = section.find_next_sibling()
        while node and node.name != "h2":
            if node.name == "div" and "faq-item" in node.get("class", []):
                question = node.find("div", class_="question").get_text(strip=True)
                answer = node.find("div", class_="answer").get_text(strip=True)
                docs.append(Document(
                    page_content=f"{question}\n{answer}",
                    metadata={"source": path, "section": section_title}
                ))
            node = node.find_next_sibling()

    return docs