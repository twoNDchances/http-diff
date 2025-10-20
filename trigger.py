from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart
from logging              import info, error
from re                   import findall
from smtplib              import SMTP

class Email:
    def __init__(self, username: str, password: str, receivers: list[str], subject: str, body: str, server: str = 'smtp.gmail.com', port: int = 587, is_html: str = 'false'):
        self.username    = username
        self.password    = password
        self.receivers   = receivers
        self.subject     = subject
        self.body        = body
        self.server      = server
        self.port        = port
        self.is_html     = is_html

    def perform(self, information: dict):
        try:
            message            = MIMEMultipart()
            message['From']    = self.username
            message['To']      = ', '.join(self.receivers)
            message['Subject'] = self.__translate_text(self.subject, information)
            message.attach(MIMEText(self.__translate_text(self.body, information), 'html' if self.is_html == 'true' else 'plain'))
            with SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, self.receivers, message.as_string())
            info(f'Sent Email to {', '.join(self.receivers)}')
        except Exception as exception:
            error(f'Error when sending email, {exception}')
    
    def __translate_text(self, text: str, information: dict):
        matches = findall(r"\$(.*?)\$", text)
        for match in matches:
            if match in information:
                text = text.replace(f'${match}$', information[match])
        return text

class Request:
    def __init__(self):
        pass

    def perform(self, information: dict):
        pass

    def __translate_text(self, text: str, information: dict):
        matches = findall(r"\$(.*?)\$", text)
        for match in matches:
            if match in information:
                text = text.replace(f'${match}$', information[match])
        return text

class Trigger:
    def __init__(self, action: str, email: Email, request: Request):
        self.action  = action
        self.email   = email
        self.request = request

    def perform(self, information: dict):
        match self.action:
            case 'none':
                return
            case 'email':
                self.email.perform(information)
            case 'request':
                self.request.perform(information)
