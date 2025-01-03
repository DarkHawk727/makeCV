# makeCV

CLI tool to generate a cover letter based off a resume pdf and job description link. It uses `langchain` to scrape the job listing website pass the description and resume contents to an LLM, and return a cover letter. Finally, it uses `mdpdf` to convert the markdown file to a PDF.

## Installation

```sh
git clone https://github.com/DarkHawk727/makeCV
cd makeCV
python -m virtualenv venv
```

 `.\venv\Scripts\activate` or  `source venv/bin/activate` depending on OS.

```sh
pip install -r requirements.txt
```

You will then need to populate the `.env` file with your OpenAI API key.

## Usage

```sh
makecv https://www.example.com/link/to/job-posting --resume path/to/resume  --destination path/to/destination
```

## Next Steps

- General Code cleanup
- ~~Add status indicators (using the `logging` module?)~~
- ~~Better web scraping, headless?~~
- Ability to go through a list of links provided and generate cover letters for them
- ~~Maybe add the option to be able to edit a coverletter first (this would mean it outputs latex which would then have to be bulk converted afterwards.)~~
- Compile the LaTeX file into a pdf

## Credits

All credits for the templates to their respective creators.
