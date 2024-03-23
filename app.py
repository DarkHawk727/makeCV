import streamlit as st
from components.job_listing import JobListing, CloudflareBlockedException
from components.template import Template


def main() -> None:
    st.title("makeCV")
    st.markdown("make*C*over*L*etter")

    resume = st.file_uploader(label="Upload your resume", type=["pdf"])

    job_listing_url = st.text_input(
        label="Enter the job listing URL", placeholder="https://link.to.job"
    )

    job_listing_content = st.text_area(
        label="Job listing content", placeholder="Enter the job listing content here."
    )

    if resume:
        # I think i need to make this a tempfile and then read from it...
        st.toast("Resume Uploaded Successfully", icon="✅")
        if job_listing_url:
            try:
                j = JobListing(link=job_listing_url)
                st.toast("Scraped job listing", icon="✅")
                st.write(j.text)
            except CloudflareBlockedException as e:
                st.toast(
                    "Could not scrape job listing, please paste contents in the textbox.",
                    icon="❌",
                )
        elif job_listing_content:
            j = JobListing(content=job_listing_content)
            st.toast("Loaded job listing from textbox", icon="✅")
        t = Template("templates/deedy/deedy.tex")
        st.code(t.contents, language="latex", line_numbers=True)
        st.download_button(label="Generate Cover Letter", type="primary", data=resume)


if __name__ == "__main__":
    main()
