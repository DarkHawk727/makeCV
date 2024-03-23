from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer

loader = WebBaseLoader(
    web_path="https://web.archive.org/web/20070613184827/http://yudkowsky.net/singularity.html"
)
doc = loader.load()
html2text = Html2TextTransformer()


with open("yudkowsky_singularity.md", "w") as f:
    f.write(html2text.transform_documents(documents=doc)[0].page_content)
