from __future__ import annotations
import yaml


class PersonalInfo:
    """
    A class to represent a person's personal information.
    """

    def __init__(self, **kwargs: str) -> None:
        self.first_name = kwargs.get("first_name", "John")
        self.last_name = kwargs.get("last_name", "Doe")
        self.email = kwargs.get("email", "email@email.com")
        self.linkedin = kwargs.get("linkedin", "https://www.linkedin.com/in/johndoe")
        self.github = kwargs.get("github", "https://www.github.com/johndoe")
        self.website = kwargs.get("website", "https://www.johndoe.com")

    def __str__(self) -> str:
        output = "PersonalInfo("
        for key, value in self.__dict__.items():
            if value:
                output += f"{key}={value}, "
        output = output[:-2] + ")"
        return output

    @classmethod
    def from_yaml(self, fp: str) -> PersonalInfo:
        """
        Creates a PersonalInfo object from a YAML file.
        """
        with open(fp, "r") as f:
            data = yaml.safe_load(f)

        return PersonalInfo(**data)
