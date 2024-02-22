import argparse
import asyncio
import logging
import os
import subprocess
import sys

from langchain_community.document_loaders import HtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_openai import OpenAI
from langchain.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompt = PromptTemplate(
    input_variables=["company_background_text", "job_listing_text", "resume_text"],
    template="""
Please write a cover letter formatted in markdown for the following job listing and resume. \
Give me only the letter, no preamble nor any other text. DO NOT format the markdown within triple backticks. \
Use only experiences, projects, and skills that are directly contained in the resume. \
The general format is as follows:
1. A few (1-3) sentences summarizing what the company does.
2. A paragraph about how my experience would be an asset to the company.
3 [Optional]. A paragraph about how my ClifftonStrengths would be an asset to the company, write this paragraph only if the job listing mentions the company's values or culture.
The overall length should not exceed 500 words. DO NOT include any information like my email or address in the header of the letter.

Company Background:
{company_background_text}\n

Job Listing:
{job_listing_text}\n

Resume:
{resume_text}
""",
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a cover letter from a job listing URL and a resume."
    )
    parser.add_argument("url", help="URL of the job listing")
    return parser.parse_args()


def extract_text(url: str) -> str:
    """Asynchronously extract text from the given URL.

    Args:
        url (str): URL to extract text from.

    Returns:
        str: Extracted text content.
    """
    try:
        loader = HtmlLoader(web_path=url)
        docs = loader.load()
        html2text = Html2TextTransformer()
        docs = html2text.transform_documents(documents=docs)
        return docs[0].page_content
    except Exception as e:
        logger.error(f"Failed to extract text from the URL: {e}")
        sys.exit(1)


async def main() -> None:
    """Main function to generate a cover letter from a job listing URL and a resume."""
    args = parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    try:
        with open("main.tex", "r") as f:
            resume_text = f.read()
    except Exception as e:
        logger.error(f"Failed to read resume file: {e}")
        sys.exit(1)

    job_listing_text = extract_text(args.url)

    llm = OpenAI(model="gpt-4", api_key=api_key, max_tokens=1000)

    chain = prompt | llm | StrOutputParser()
    chain.ainvoke()

    with open("coverletter.md", "w") as md_file:
        md_file.write(cover_letter)

    try:
        subprocess.run(
            ["pandoc", "coverletter.md", "-o", "coverletter.pdf"], check=True
        )
        print("Successfully converted Markdown to PDF.")
    except subprocess.CalledProcessError:
        print("Error occurred while converting Markdown to PDF.")


if __name__ == "__main__":
    asyncio.run(main())
