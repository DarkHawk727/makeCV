import os
import tiktoken
from pydantic.v1 import SecretStr
import logging
import sys


from components.personal_info import PersonalInfo
from components.cover_letter import CoverLetterContents
from components.template import Template
from components.job_listing import JobListing


from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PDFMinerLoader
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate


API_KEY: SecretStr = SecretStr(
    os.getenv(
        "OPENAI_API_KEY",
        default="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    )
)


def main() -> None:
    t = Template("templates/deedy/deedy.tex")

    encoding = tiktoken.get_encoding(encoding_name="cl100k_base")

    resume_content = PDFMinerLoader(file_path="resume.pdf").load()[0].page_content
    logging.info(f"Resume Length: {len(encoding.encode(text=resume_content))}")

    j = JobListing(sys.argv[1])
    print(j)

    llm = ChatOpenAI(
        model="gpt-3.5-turbo", api_key=API_KEY, max_tokens=1000
    )  # Change model to 4 later

    parser = PydanticOutputParser(pydantic_object=CoverLetterContents)
    prompt = PromptTemplate(
        input_variables=["job_listing_text", "resume_text"],
        template=r"""
            Please write the paragraphs of a cover letter formatted in plaintext for the following job listing and resume. \
            Give me only the letter, no preamble nor any other text. Enclose any library/developer tool in \emph{{}}. \
            Use only experiences, projects, and skills that are directly contained in the resume. \
            The general format is as follows:
            1. The first paragraph should be a few (1-3) sentences summarizing what the company does.
            2. A paragraph about how my experience/projects/skills would be an asset to the company.
            # 3 [Optional]. A paragraph about how my ClifftonStrengths would be an asset to the company, write this paragraph only if the job listing mentions the company's values or culture.
            The overall length should be very close to, but not exceed, 500 words. DO NOT include any information like my email or address in the header of the letter. DO NOT end with a sign-off.
            Format Instructions:
            {format_instructions}

            Job Listing:
            {job_listing_text}\n

            Resume:
            {resume_text}
            """,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    logging.info(f"Prompt Length: {len(encoding.encode(text=prompt.template))}")
    total_length = len(encoding.encode(text=prompt.template + j.text + resume_content))
    logging.info(f"Total: {total_length}")

    chain = prompt | llm | parser

    out: CoverLetterContents = chain.invoke(
        {
            "job_listing_text": j.text,
            "resume_text": resume_content,
        }
    )
    x = len(encoding.encode(text="".join(out.contents)))
    logging.info(f"Generated {x} Tokens")

    t.populate(cv=out, pi=PersonalInfo().from_yaml(fp="personal_info.yaml"))
    t.save("output.tex")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
