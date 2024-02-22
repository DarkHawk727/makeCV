import os

import pprint
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from pydantic.v1 import SecretStr
from operator import itemgetter


def save_pdf(text: str, filename: str) -> None:
    raise NotImplementedError


def main() -> None:
    API_KEY: SecretStr = SecretStr(
        os.getenv(
            "OPENAI_API_KEY",
            default="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        )
    )

    get_job_listing: RunnableLambda = RunnableLambda(
        lambda url: WebBaseLoader(web_path=url).load()[0].page_content
    )
    get_resume_content: RunnableLambda = RunnableLambda(
        lambda filepath: TextLoader(file_path=filepath).load()[0].page_content
    )

    llm = ChatOpenAI(model="gpt-4-0613", api_key=API_KEY, max_tokens=1000)  # Change model later

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
    chain: RunnableMap = RunnableMap({
        "job_listing_text": itemgetter("url") | get_job_listing,
        "resume_text":  itemgetter("filepath") | get_resume_content,
    }) | prompt | llm | StrOutputParser()

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(chain.invoke({"url": "https://github.com/DarkHawk727/ARM-LEG-Simulator/blob/main/readme.md", "filepath": "main.tex"}))


if __name__ == "__main__":
    main()