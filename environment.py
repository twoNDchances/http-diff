from dotenv import load_dotenv
from json import loads
from pathlib import Path
from os import getenv

class Environment:

    __default_env_path = '.env'

    __default_env_bone = {
        'HTTP_DIFF_AVAILABLE_REQUEST_NAMES': 'DEFAULT',

        # required string
        'HTTP_DIFF_DEFAULT_REQUEST_URL': 'https://example.com/path',

        # post (default), get, put, patch, delete
        'HTTP_DIFF_DEFAULT_REQUEST_METHOD': 'post',

        # application/json (default), application/x-www-form-urlencoded
        'HTTP_DIFF_DEFAULT_REQUEST_CONTENT_TYPE': 'application/json',

        # optional string
        'HTTP_DIFF_DEFAULT_REQUEST_HEADERS': '{"User-Agent": "HTTP-Diff"}',

        # optional string
        'HTTP_DIFF_DEFAULT_REQUEST_BODY': '{"message": "Hello from HttpDiff"}',

        # required string
        'HTTP_DIFF_DEFAULT_RULE_SCHEMA': '{"status": {"equal": 200}}',

        # or (default), and
        'HTTP_DIFF_DEFAULT_RULE_LOGIC': 'or',

        # none (default), mail, request
        'HTTP_DIFF_DEFAULT_TRIGGER_ACTION': 'none',
    }

    @staticmethod
    def __load_env():
        env_file = Path(Environment.__default_env_path)
        if not env_file.exists():
            with env_file.open("w", encoding="utf-8") as f:
                for key, value in Environment.__default_env_bone.items():
                    f.write(f"{key}={value}\n")
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
        if key not in env_dict:
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
                    'url':          Environment.__get_env(env_dict, f'{env}_REQUEST_URL'),
                    'method':       Environment.__get_env(env_dict, f'{env}_REQUEST_METHOD', 'post', ['post','get','put','patch','delete']).lower(),
                    'content_type': Environment.__get_env(env_dict, f'{env}_REQUEST_CONTENT_TYPE', 'application/json', ['application/json', 'application/x-www-form-urlencoded']).lower(),
                    'headers':      loads(Environment.__get_env(env_dict, f'{env}_REQUEST_HEADERS', '{}')),
                    'body':         loads(Environment.__get_env(env_dict, f'{env}_REQUEST_BODY', '{}')),
                    'rule': {
                        'schema': loads(Environment.__get_env(env_dict, f'{env}_RULE_SCHEMA')),
                        'logic':  Environment.__get_env(env_dict, f'{env}_RULE_LOGIC', 'or', ['or','and']).lower(),
                    },
                    'trigger': {
                        'action': Environment.__get_env(env_dict, f'{env}_TRIGGER_ACTION', 'none', ['none','mail','request']).lower(),
                        'mail': {},
                        'request': {},
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
