from components.personal_info import PersonalInfo
from components.cover_letter import CoverLetterContents


class Template:
    """
    Holds the contents of a template file and can populate it with the contents of a cover letter and personal info.
    """

    # Eventually, if I want to make this general for nearly any template, I will
    # need to use an LLM preprocess step to replace the example text with the
    # appropriate variables.
    def __init__(self, filepath: str) -> None:
        if filepath:
            with open(filepath, "r") as f:
                self.contents = f.read()

    def populate(self, cv: CoverLetterContents, pi: PersonalInfo) -> None:
        """
        Populates the template with the contents of a cover letter and personal info.
        """
        for attr in dir(pi):
            if not attr.startswith("_"):
                self.contents = self.contents.replace(
                    attr.upper(), str(getattr(pi, attr))
                )

        paragraphs = ""
        for paragraph in cv.contents:
            paragraphs += f"\\lettercontent{{{paragraph}}}\n\n"

        self.contents = self.contents.replace("LETTER_CONTENT", paragraphs)

    def __str__(self):
        return self.contents

    def save(self, filename: str) -> None:
        """
        Saves the template to a tex file.
        """
        if not filename.endswith(".tex"):
            raise ValueError("Filename must end with .tex")

        with open(filename, "w") as f:
            f.write(self.contents)
