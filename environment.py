from dotenv  import load_dotenv
from json    import loads
from pathlib import Path
from os      import getenv

class Environment:

    __default_env_path = '.env'

    __default_env_requirement = [
        'HTTP_DIFF_@>@_REQUEST_URL',
        'HTTP_DIFF_@>@_REQUEST_METHOD',
        'HTTP_DIFF_@>@_REQUEST_TIMEOUT',
        'HTTP_DIFF_@>@_REQUEST_CONTENT_TYPE',
        'HTTP_DIFF_@>@_REQUEST_HEADERS',
        'HTTP_DIFF_@>@_REQUEST_BODY',
        'HTTP_DIFF_@>@_RULE_SCHEMA',
        'HTTP_DIFF_@>@_RULE_LOGIC',
        'HTTP_DIFF_@>@_TRIGGER_ACTION',

        'HTTP_DIFF_@>@_TRIGGER_EMAIL_USERNAME',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_PASSWORD',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_RECEIVERS',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_SUBJECT',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_BODY',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_SERVER',
        'HTTP_DIFF_@>@_TRIGGER_EMAIL_PORT',

        'HTTP_DIFF_@>@_TRIGGER_REQUEST_URL',
        'HTTP_DIFF_@>@_TRIGGER_REQUEST_METHOD',
        'HTTP_DIFF_@>@_TRIGGER_REQUEST_HEADERS',
        'HTTP_DIFF_@>@_TRIGGER_REQUEST_BODY',
    ]

    @staticmethod
    def __load_env():
        env_file = Path(Environment.__default_env_path)
        if not env_file.exists():
            request_names = getenv('HTTP_DIFF_AVAILABLE_REQUEST_NAMES')
            if request_names is None:
                raise KeyError(f'Missing HTTP_DIFF_AVAILABLE_REQUEST_NAMES key in env')
            result_directory = getenv('HTTP_DIFF_RESULT_DIRECTORY')
            if result_directory is None:
                result_directory = 'history'
            env_dict: dict[str, str] = {
                'HTTP_DIFF_AVAILABLE_REQUEST_NAMES': request_names,
                'HTTP_DIFF_RESULT_DIRECTORY':        result_directory,
            }
            request_names = env_dict['HTTP_DIFF_AVAILABLE_REQUEST_NAMES'].split(',')
            for name in request_names:
                for requirement in Environment.__default_env_requirement:
                    key = requirement.replace('@>@', name.upper())
                    env_dict[key] = getenv(key)
            return env_dict
        ok = load_dotenv(dotenv_path=env_file)
        if not ok:
            raise Exception("Can't load env file")
        keys = []
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key = line.split("=", 1)[0].strip()
                    keys.append(key)
        return {key: getenv(key) for key in keys}

    @staticmethod
    def __validate_env(env_dict: dict[str, str]):
        required_envs = ['HTTP_DIFF_AVAILABLE_REQUEST_NAMES']
        for required_env in required_envs:
            if required_env not in env_dict:
                raise KeyError(f'Missing {required_env} key in env')
            else:
                break

    @staticmethod
    def __validate_dict(env_dict: dict[str, str]):
        request_names = set(env_dict['HTTP_DIFF_AVAILABLE_REQUEST_NAMES'].replace(' ', '').split(','))
        for name in request_names:
            if name != name.upper():
                raise KeyError(f"{name} must be uppercase")
        for name in request_names:
            required_envs = ['REQUEST_URL', 'RULE_SCHEMA']
            for required_env in required_envs:
                env = f'HTTP_DIFF_{name}_{required_env}'
                if env not in env_dict:
                    raise KeyError(f'{env} required')

    @staticmethod
    def __get_env(env_dict: dict[str, str], key: str, fallback = None, options: list[str] = []):
        if key not in env_dict or env_dict[key] is None:
            return fallback
        value = env_dict[key]
        if len(options) > 0:
            if value not in options:
                raise ValueError(f"{key}={value} isn't supported, must in {options}")
        return value

    @staticmethod
    def __build_dict(env_dict: dict[str, str]):
        request_names = set(env_dict['HTTP_DIFF_AVAILABLE_REQUEST_NAMES'].replace(' ', '').split(','))
        requests = []
        for name in request_names:
            request_builder = {}
            for _ in env_dict:
                env = f'HTTP_DIFF_{name}'
                request_builder = {
                    'name':         name,
                    'result_dir':   Environment.__get_env(env_dict, 'HTTP_DIFF_RESULT_DIRECTORY', 'history'),
                    'url':          Environment.__get_env(env_dict, f'{env}_REQUEST_URL'),
                    'method':       Environment.__get_env(env_dict, f'{env}_REQUEST_METHOD', 'post', ['post', 'get', 'put', 'patch', 'delete']).lower(),
                    'timeout':      int(Environment.__get_env(env_dict, f'{env}_REQUEST_TIMEOUT', 5)),
                    'content_type': Environment.__get_env(env_dict, f'{env}_REQUEST_CONTENT_TYPE', 'application/json', ['application/json', 'application/x-www-form-urlencoded']).lower(),
                    'headers':      loads(Environment.__get_env(env_dict, f'{env}_REQUEST_HEADERS', '{"User-Agent": "HttpDiff"}')),
                    'body':         loads(Environment.__get_env(env_dict, f'{env}_REQUEST_BODY', '{}')),
                    'rule': {
                        'schema': loads(Environment.__get_env(env_dict, f'{env}_RULE_SCHEMA')),
                        'logic':  Environment.__get_env(env_dict, f'{env}_RULE_LOGIC', 'or', ['or','and']).lower(),
                    },
                    'trigger': {
                        'action': Environment.__get_env(env_dict, f'{env}_TRIGGER_ACTION', 'none', ['none', 'email', 'request']).lower(),
                        'email': {
                            'username':  Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_USERNAME'),
                            'password':  Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_PASSWORD'),
                            'receivers': Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_RECEIVERS', '').split(','),
                            'subject':   Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_SUBJECT', 'HttpDiff alerting'),
                            'body':      Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_BODY', ''),
                            'server':    Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_SERVER', 'smtp.gmail.com'),
                            'port':      Environment.__get_env(env_dict, f'{env}_TRIGGER_EMAIL_PORT', 587),
                        },
                        'request': {
                            'url':     Environment.__get_env(env_dict, f'{env}_TRIGGER_REQUEST_URL'),
                            'method':  Environment.__get_env(env_dict, f'{env}_TRIGGER_REQUEST_METHOD', 'post', ['post', 'get', 'put', 'patch', 'delete']),
                            'headers': loads(Environment.__get_env(env_dict, f'{env}_TRIGGER_REQUEST_HEADERS', '{"User-Agent": "HttpDiff"}')),
                            'body':    loads(Environment.__get_env(env_dict, f'{env}_TRIGGER_REQUEST_BODY', '{}')),
                        },
                    },
                }
            requests.append(request_builder)
        return requests

    @staticmethod
    def analyze_env():
        env_dict = Environment.__load_env()
        Environment.__validate_env(env_dict)
        Environment.__validate_dict(env_dict)
        return Environment.__build_dict(env_dict)
