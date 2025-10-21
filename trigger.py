from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart
from json                 import dumps, loads
from logging              import info, error
from re                   import findall
from requests             import request, RequestException
from smtplib              import SMTP

class Utility:

    def _translate_text(self, text: str, information: dict):
        matches = findall(r"\$(.*?)\$", text)
        for match in matches:
            if match in information:
                text = text.replace(f'${match}$', str(information[match]))
        return text


class Email (Utility):

    def __init__(self, username: str, password: str, receivers: list[str], subject: str, body: str, server: str = 'smtp.gmail.com', port: int = 587):
        self.username    = username
        self.password    = password
        self.receivers   = receivers
        self.subject     = subject
        self.body        = body
        self.server      = server
        self.port        = port

    def perform(self, information: dict):
        try:
            message            = MIMEMultipart()
            message['From']    = self.username
            message['To']      = ', '.join(self.receivers)
            message['Subject'] = super()._translate_text(self.subject, information)
            message.attach(MIMEText(super()._translate_text(self.body, information)))
            with SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, self.receivers, message.as_string())
            info(f'Sent Email to {', '.join(self.receivers)}')
        except Exception as exception:
            error(f'Error when sending email, {exception}')


class Request (Utility):

    def __init__(self, url: str, method: str, headers: dict[str, str], body: dict):
        self.url          = url
        self.method       = method.upper()
        self.headers      = headers
        self.body         = body

    def perform(self, information: dict):
        try:
            response = request(url=self.url, method=self.method, headers=self.__translate_json(self.headers, information), json=self.__translate_json(self.body, information))
            if response.status_code >= 400:
                raise RequestException(f'Request action unsucessful, status {response.status_code}')
            info(f'Sent Request to {self.url} using {self.method} method')
        except Exception as exception:
            error(f'Error when sending request, {exception}')

    def __translate_json(self, json: dict, information: dict):
        return loads(super()._translate_text(dumps(json), information))

class Trigger:

    def __init__(self, action: str, email: Email, request: Request):
        self.action  = action
        self.email   = email
        self.request = request

    def perform(self, information: dict):
        match self.action:
            case 'none':
                info("Trigger action is 'none', nothing performed")
                return
            case 'email':
                self.email.perform(information)
            case 'request':
                self.request.perform(information)

