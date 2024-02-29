import os
import subprocess
import sys

from langchain_community.document_loaders import (
    WebBaseLoader,
    PDFMinerLoader,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from pydantic.v1 import SecretStr
from operator import itemgetter


def generate_cover_letter(text: str) -> None:
    with open(file="cov.md", mode="w") as f:
        f.write(text)

    subprocess.run(
        [
            "mdpdf",
            "-o",
            "Arjun_Sarao_Cover_Letter.pdf",
            "--header",
            "{date},{heading},{page}",
            "--footer",
            ",Arjun Sarao,",
            f.name,
            "-a",
            "Arjun Sarao",
            "-t",
            "Cover Letter",
        ]
    )
    os.remove(path="cov.md")


# TODO: Add some progress bars to the code/ completion checks for each step.
# TODO: Make this a CLI tool
def main() -> None:
    API_KEY: SecretStr = SecretStr(
        os.getenv(
            "OPENAI_API_KEY",
            default="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        )
    )

    compress_newlines: RunnableLambda = RunnableLambda(
        lambda text: "\n".join(filter(None, text.split("\n")))
    )

    get_job_listing: RunnableLambda = RunnableLambda(
        lambda url: WebBaseLoader(web_path=url).load()[0].page_content
    )
    get_resume_content: RunnableLambda = RunnableLambda(
        lambda filepath: PDFMinerLoader(file_path=filepath).load()[0].page_content
    )

    llm = ChatOpenAI(
        model="gpt-4-0613", api_key=API_KEY, max_tokens=1000
    )  # Change model later

    prompt = PromptTemplate(
        input_variables=["job_listing_text", "resume_text"],
        template="""
            Please write a cover letter formatted in markdown for the following job listing and resume. \
            Start the cover letter with an H1 header of the form "# *Company Name* Cover Letter". \
            Give me only the letter, no preamble nor any other text. Enclose any library/developer tool in single backicks. \
            Make any project name italicized. \
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

    save_pdf = RunnableLambda(
        lambda cover_letter: generate_cover_letter(text=cover_letter)
    )
    chain = (
        RunnableMap(
            {
                "job_listing_text": itemgetter("url")
                | get_job_listing
                | compress_newlines,
                "resume_text": itemgetter("filepath") | get_resume_content,
            }
        )
        | prompt
        | llm
        | StrOutputParser()
        | save_pdf
    )

    if len(sys.argv) != 2:
        print("Usage: python makecv.py <job_listing_url> <resume_pdf_path>")
        sys.exit(1)
    elif len(sys.argv) == 2:
        url = sys.argv[1]
        fp = "resume.pdf"
    else:
        url = sys.argv[1]
        fp = sys.argv[2]

    chain.invoke(
        {
            "url": url,
            "filepath": fp,
        }
    )
    print("Cover letter generated successfully")


if __name__ == "__main__":
    main()
