class Email():
    def __init__(self, subject:str, **kwargs):
        self.subject = subject
        self.text_message = kwargs.get("text_message", None)
        self.html_message = kwargs.get("html_message", None)
        self.from_email = kwargs.get("from_email", None)
        self.to_email = kwargs.get("to_email", None)