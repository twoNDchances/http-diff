FROM python:3.13-slim

WORKDIR /http-diff

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HTTP_DIFF_AVAILABLE_REQUEST_NAMES=DEFAULT \
    HTTP_DIFF_RESULT_DIRECTORY=history \
    HTTP_DIFF_DEFAULT_REQUEST_URL='http://localhost' \
    HTTP_DIFF_DEFAULT_REQUEST_METHOD=get \
    HTTP_DIFF_DEFAULT_REQUEST_TIMEOUT=5 \
    HTTP_DIFF_DEFAULT_REQUEST_CONTENT_TYPE='application/json' \
    HTTP_DIFF_DEFAULT_REQUEST_HEADERS='{"User-Agent": "HttpDiff/MainCore"}' \
    HTTP_DIFF_DEFAULT_REQUEST_BODY='{}' \
    HTTP_DIFF_DEFAULT_RULE_SCHEMA='{"status": {"source": "[previous_status]", "operator": "similar", "destination": "[current_status]"}}' \
    HTTP_DIFF_DEFAULT_RULE_LOGIC=and \
    HTTP_DIFF_DEFAULT_TRIGGER_ACTION=none \
    \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_USERNAME= \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_PASSWORD= \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_RECEIVERS= \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_SUBJECT='[HttpDiff] Alerting from $request.name$' \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_BODY='Your rule is firing because it matches when fetching $request.url$ using $request.method$ method' \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_SERVER='smtp.gmail.com' \
    HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_PORT=587 \
    \
    HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_URL='http://localhost' \
    HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_METHOD=post \
    HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_HEADERS='{"User-Agent": "HttpDiff/Action"}' \
    HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_BODY='{"message": "$rule.status.source$ $rule.status.operator$ $rule.status.destination$ => $rule.status.source.value$ $rule.status.operator.value$ $rule.status.destination.value$"}'

ENTRYPOINT [ "python", "main.py" ]