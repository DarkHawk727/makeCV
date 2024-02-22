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


def extract_text(url: str) -> str:
    """Extract text from the given URL."""
    return (
        Html2TextTransformer()
        .transform_documents(documents=HtmlLoader(web_path=url).load())[0]
        .page_content
    )


def save_pdf(text: str, filename: str) -> None:
    """Save the given text to a PDF file."""
    subprocess.run(
        ["pandoc", "-o", filename, "--pdf-engine=xelatex"], input=text, text=True
    )


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")

    # I think we can get it to: chain = get_html | prompt | llm | StrOutputParser() | save_pdf using the LCEL
    get_job_listing: RunnableLambda = RunnableLambda(lambda x: extract_text(url=x))
    llm = OpenAI(model="gpt-4", api_key=api_key, max_tokens=1000)
    prompt = PromptTemplate(
        input_variables=["job_listing_text", "resume_text"],
        template="""
            Please write a cover letter formatted in markdown for the following job listing and resume. \
            Give me only the letter, no preamble nor any other text. DO NOT format the markdown within triple backticks. \
            Use only experiences, projects, and skills that are directly contained in the resume. \
            The general format is as follows:
            1. A few (1-3) sentences summarizing what the company does.
            2. A paragraph about how my experience/projects/skills would be an asset to the company.
            3 [Optional]. A paragraph about how my ClifftonStrengths would be an asset to the company, write this paragraph only if the job listing mentions the company's values or culture.
            The overall length should not exceed 500 words. DO NOT include any information like my email or address in the header of the letter.

            Job Listing:
            {job_listing_text}\n

            Resume:
            {resume_text}
            """,
    )
    save_pdf = RunnableLambda(lambda x: save_pdf(text=x, filename="cover_letter.pdf"))

    chain = get_job_listing | prompt | llm | StrOutputParser() | save_pdf
    chain.invoke({"url": "https://www.indeed.com/"})


if __name__ == "__main__":
    main()
