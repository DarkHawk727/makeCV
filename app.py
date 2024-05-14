import os

import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredFileIOLoader
from langchain_openai import ChatOpenAI
from unstructured.cleaners.core import clean_extra_whitespace


def main() -> None:
    API_KEY = "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"
    st.title("makeCV")

    if "generated_cover_letter" not in st.session_state:
        st.session_state["generated_cover_letter"] = None

    resume = st.file_uploader(label="Upload your resume", type=["pdf"])

    job_listing_text = st.text_area(
        label="Job listing content", placeholder="Enter the job listing content here."
    )

    if resume and job_listing_text:
        loader = UnstructuredFileIOLoader(
            file=resume,
            mode="elements",
            strategy="fast",
            post_processors=[clean_extra_whitespace],
        )

        docs = loader.load()
        resume_text = "".join([doc.page_content for doc in docs])
        st.toast("Resume Uploaded Successfully", icon="✅")


        llm = ChatOpenAI(model="gpt-4", api_key=API_KEY, max_tokens=2048)

        prompt = PromptTemplate(
            input_variables=["job_listing_text", "resume_text"],
            template=r"""
            Please write a cover letter formatted in markdown for the following job listing and resume. \
            Give me only the letter, no preamble nor any other text. \
            Use only experiences, projects, and skills that are directly contained in the resume. \
            The general format is as follows:
            1. The first paragraph should be a few (1-3) sentences summarizing what the company does.
            2. A paragraph about how my experience/projects/skills would be an asset to the company.
            The overall length should be very close to, but not exceed, 500 words. DO NOT include any information like my email or address in the header of the letter. DO NOT end with a sign-off.

            Job Listing:
            {job_listing_text}\n

            Resume:
            {resume_text}
            """,
        )

        chain = prompt | llm

        if not st.session_state["generated_cover_letter"]:
            out = chain.invoke(
                {
                    "job_listing_text": job_listing_text,
                    "resume_text": resume_text,
                }
            )
            st.session_state["generated_cover_letter"] = out

        st.markdown(st.session_state["generated_cover_letter"].content, unsafe_allow_html=True)

        # st.download_button(
        #     label="Download Cover Letter",
        #     type="primary",
        #     data=st.session_state["generated_cover_letter"],
        #     file_name="cover_letter.md",
        # )


if __name__ == "__main__":
    main()
