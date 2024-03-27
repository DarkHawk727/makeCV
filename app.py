import streamlit as st
import os
from pydantic.v1 import SecretStr
from dotenv import load_dotenv

from components.template import Template
from components.cover_letter import CoverLetterContents
from components.personal_info import PersonalInfo

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import UnstructuredFileIOLoader
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

load_dotenv(dotenv_path=".env")


def main() -> None:
    API_KEY: SecretStr = SecretStr(os.getenv(key="OPENAI_API_KEY", default="BRUH"))
    st.title("makeCV")

    if "generated_cover_letter" not in st.session_state:
        st.session_state["generated_cover_letter"] = None

    resume = st.file_uploader(label="Upload your resume", type=["pdf"])

    job_listing_text = st.text_area(
        label="Job listing content", placeholder="Enter the job listing content here."
    )

    if resume and job_listing_text:
        # Load the resume
        loader = UnstructuredFileIOLoader(
            file=resume,
            mode="elements",
            strategy="fast",
            post_processors=[clean_extra_whitespace],
        )

        docs = loader.load()
        resume_text = "".join([doc.page_content for doc in docs])
        st.toast("Resume Uploaded Successfully", icon="✅")

        # Initialize LLM + Prompt + Parser

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

        t = Template("templates/deedy/deedy.tex")

        chain = prompt | llm | parser

        if not st.session_state["generated_cover_letter"]:
            out: CoverLetterContents = chain.invoke(
                {
                    "job_listing_text": job_listing_text,
                    "resume_text": resume_text,
                }
            )

        t.populate(cv=out, pi=PersonalInfo().from_yaml(fp="personal_info.yaml"))

        st.code(t.contents, language="latex", line_numbers=True)

        st.download_button(
            label="Download Cover Letter",
            type="primary",
            data=t.contents,
            file_name="cover_letter.tex",
        )


if __name__ == "__main__":
    main()
