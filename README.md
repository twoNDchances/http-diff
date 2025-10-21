# HttpDiff - 🌐 A Response Different Tracker

HttpDiff is a tool written for Kubernetes CronJob with the purpose of continuously monitoring whether the response of requests has changed or not. If they change, it will perform trigger actions such as sending an email or a simple HTTP request.

## Installation

```bash
git clone https://github.com/twoNDchances/http-diff.git
cd http-diff
```

## Guideline

### 1. Configuration

Because this tool written for container, so we will use Environment variables for main configuration.

You need to register your request by name to `HTTP_DIFF_AVAILABLE_REQUEST_NAMES`, seperator by comma (`,`). After that, `HTTP_DIFF_$name$_REQUEST_URL`, ... must exists with your name registed

```bash
# required string, seperator by comma, no whitespace, uppercase
HTTP_DIFF_AVAILABLE_REQUEST_NAMES=DEFAULT

# optional string, 'history' (default)
HTTP_DIFF_RESULT_DIRECTORY=history

# required string
HTTP_DIFF_DEFAULT_REQUEST_URL=http://localhost

# post (default), get, put, patch, delete
HTTP_DIFF_DEFAULT_REQUEST_METHOD=post

# option integer, seconds
HTTP_DIFF_DEFAULT_REQUEST_TIMEOUT=5

# application/json (default), application/x-www-form-urlencoded
HTTP_DIFF_DEFAULT_REQUEST_CONTENT_TYPE=application/json

# optional string, json format (1 level)
HTTP_DIFF_DEFAULT_REQUEST_HEADERS='{"User-Agent": "HTTP-Diff"}'

# optional string, json format (N level)
HTTP_DIFF_DEFAULT_REQUEST_BODY='{"message": "Hello from HttpDiff"}'

# required string, json format (2 level)
HTTP_DIFF_DEFAULT_RULE_SCHEMA='{"status": {"source": "[current_status]", "operator": "similar", "destination": 200}}'

# or (default), and
HTTP_DIFF_DEFAULT_RULE_LOGIC=or

# none (default), email, request
HTTP_DIFF_DEFAULT_TRIGGER_ACTION=none

# required string if trigger_action=email
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_USERNAME=

# required string if trigger_action=email
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_PASSWORD=

# required string if trigger_action=email, seperator by comma
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_RECEIVERS=

# required string if trigger_action=email
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_SUBJECT='[HttpDiff] Alerting from $request.name$'

# required string if trigger_action=email
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_BODY='Your rule is firing because it matches when fetching $request.url$ using $request.method$ method'

# required string if trigger_action=email, smtp.gmail.com (default)
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_SERVER='smtp.gmail.com'

# required string if trigger_action=email, 587 (default)
HTTP_DIFF_DEFAULT_TRIGGER_EMAIL_PORT=587

# required string if trigger_action=request
HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_URL='http://localhost'

# required string if trigger_action=request, post (default), get, put, patch, delete
HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_METHOD=post

# optional string, only used when trigger_action=request, json format (1 level)
HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_HEADERS='{"User-Agent": "HttpDiff/Action"}'

# optional string, only used when trigger_action=request, json format (N level)
HTTP_DIFF_DEFAULT_TRIGGER_REQUEST_BODY='{"message": "$rule.status.source$ $rule.status.operator$ $rule.status.destination$ => $rule.status.source.value$ $rule.status.operator.value$ $rule.status.destination.value$"}'
```

### 2. Usage

- a. Docker

    This option is for testing purpose, or you can use crontab of Linux to perform interval action.

    ```bash
    docker compose up -d
    ```

- b. Kubernetes

    ```bash
    kubectl apply -f kubernetes-manifest.yaml
    ```

HttpDiff also provide some Virtual variables to get more information about the result after the main request.

You just only need to type with syntax `$request.name$` in the content you want to send to when the rule trigger.

```json
"request.name"                    : "get the name of request",
"request.url"                     : "get the URL of request",
"request.method"                  : "get the method of request",
"request.timeout"                 : "get timeout of request",
"request.content_type"            : "get Content-Type of request",

"rule.logic"                      : "get the logic bitwise of rule",
"rule.result_file"                : "get the location of result file of request",

"rule.status.source"              : "get the value of source setted by you",
"rule.status.source.value"        : "get the value of source setted by request",
"rule.status.destination"         : "get the value of destination setted by you",
"rule.status.destination.value"   : "get the value of destination setted by request",
"rule.status.operator"            : "get the value of operator setted by you",
"rule.status.operator.value"      : "get the value of operator setted by request",

"rule.headers.logic"              : "get the logic bitwise of the rule of headers",
"rule.headers.0.source"           : "get the value of source setted by you",
"rule.headers.0.source.value"     : "get the value of source setted by request",
"rule.headers.0.destination"      : "get the value of destination setted by you",
"rule.headers.0.destination.value": "get the value of destination setted by request",
"rule.headers.0.operator"         : "get the value of operator setted by you",
"rule.headers.0.operator.value"   : "get the value of operator setted by request",
"rule.headers.final"              : "get the result after process by logic bitwise of headers"

"rule.body.logic"                 : "get the logic bitwise of the rule of body",
"rule.body.0.source"              : "get the value of source setted by you",
"rule.body.0.source.value"        : "get the value of source setted by request",
"rule.body.0.destination"         : "get the value of destination setted by you",
"rule.body.0.destination.value"   : "get the value of destination setted by request",
"rule.body.0.operator"            : "get the value of operator setted by you",
"rule.body.0.operator.value"      : "get the value of operator setted by request",
"rule.body.final"                 : "get the result after process by logic bitwise of body",
```
