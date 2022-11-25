class BaseError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class GitlabCiBaseException(BaseError):
    pass


class FileNotFoundException(GitlabCiBaseException):
    def __init__(self, filename: str):
        super().__init__(message=f"File with name '{filename}' was not found")
