from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import Html2TextTransformer
import tiktoken


class JobListing:
    """Scrapes a link to a job listing and transforms it to text. It uses a
    headless browser to load the page and then converts the HTML to text. It
    also calculates the compression ratio of the text."""

    encoding = tiktoken.get_encoding(encoding_name="cl100k_base")
    html2text = Html2TextTransformer()

    def __init__(self, link: str) -> None:
        """Load the job listing from the given link and transform it to text."""
        loader = AsyncChromiumLoader(urls=[link])
        raw_content = loader.load()

        self.text = JobListing.html2text.transform_documents(documents=raw_content)[
            0
        ].page_content
        self.compression_ratio = 1 - (
            len(JobListing.encoding.encode(text=self.text))
            / len(JobListing.encoding.encode(text=raw_content[0].page_content))
        )

    def __str__(self) -> str:
        return self.text
