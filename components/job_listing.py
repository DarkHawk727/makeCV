from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer
import tiktoken
import logging


class CloudflareBlockedException(Exception):
    """Exception raised when the page is blocked by Cloudflare."""

    pass


class JobListing:
    encoding = tiktoken.get_encoding(encoding_name="cl100k_base")
    html2text = Html2TextTransformer()

    def __init__(self, link: str = "", content: str = "") -> None:
        loader = WebBaseLoader(web_path=link)
        self.link = link
        if content:
            self.text = content
        else:
            docs = loader.load()

        self.text = JobListing.html2text.transform_documents(documents=docs)

        self._check_for_cloudflare_blockage(self.text, self.link)
        token_count = len(JobListing.encoding.encode(text=self.text))
        logging.log(
            level=logging.INFO, msg=f"Scraped {token_count} tokens from {self.link}"
        )

    def _check_for_cloudflare_blockage(self, content: str, link: str) -> None:
        """Checks if the content indicates the page is blocked by Cloudflare."""
        cloudflare_indicators = [
            "Sorry, you have been blocked",
            "cf-browser-verification",
            "Attention Required! | Cloudflare",
            "Checking your browser before accessing",
        ]
        if any(indicator in content for indicator in cloudflare_indicators):
            raise CloudflareBlockedException(
                f"The page at {link} is blocked by Cloudflare."
            )

    def __str__(self) -> str:
        return self.text
