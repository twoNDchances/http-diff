from json    import dumps, loads
from logging import info, warning
from pathlib import Path
from request import Request
from trigger import Trigger

class Rule:

    __information = {}

    def __init__(self, schema: dict, logic: str, result_file: str, request: Request, trigger: Trigger):
        self.schema      = schema
        self.logic       = logic
        self.result_file = result_file
        self.request     = request
        self.trigger     = trigger

        self.__information['request.name']         = self.request.name
        self.__information['request.url']          = self.request.url
        self.__information['request.method']       = self.request.method
        self.__information['request.timeout']      = self.request.timeout
        self.__information['request.content_type'] = self.request.content_type
        self.__information['rule.logic']           = self.logic
        self.__information['rule.result_file']     = self.result_file

    async def perform(self):
        result = await self.request.perform()
        condition = self.__orchestrate(result)
        if not self.__determine_result(condition, self.logic):
            info(f'Request {self.request.name} does not satisfy the condition, trigger aborted')
        else:
            warning(f'Request {self.request.name} satisfy the condition')
            self.trigger.perform(self.__information)
        self.__save_result_file(result)

    def __orchestrate(self, result: dict):
        condition = []
        if 'status' in self.schema:
            status_result = self.__information['rule.status.final'] = self.__scan_status(self.schema['status'], result)
            condition.append(status_result)
        if 'headers' in self.schema:
            headers_result = self.__information['rule.headers.final'] = self.__scan_key_value(self.schema['headers'], result, 'headers')
            condition.append(headers_result)
        if 'body' in self.schema:
            body_result = self.__information['rule.body.final'] = self.__scan_key_value(self.schema['body'], result, 'body')
            condition.append(body_result)
        return condition
    
    def __scan_operator(self, config: dict):
        if 'source' not in config and 'operator' not in config and 'destination' not in config:
            raise KeyError(f"Config {config} type doesn't have 'source', 'operator' or 'destination', can't perform comparation")

    def __scan_status(self, config: dict, result: dict):
        self.__scan_operator(config)
        source = self.__information['rule.status.source'] = config['source']
        if source == '[current_status]':
            source = self.__information['rule.status.source.value'] = result['status']
        elif source == '[previous_status]':
            if not self.__check_result_file():
                self.__save_result_file(result)
                return 'skip'
            source = self.__information['rule.status.source.value']= self.__load_result_file()['status']
        elif not isinstance(source, int):
            raise ValueError(f'Source {source} of {self.request.name} request must be an integer')

        destination = self.__information['rule.status.destination'] = config['destination']
        if destination == '[current_status]':
            destination = self.__information['rule.status.destination.value'] = result['status']
        elif destination == '[previous_status]':
            if not self.__check_result_file():
                self.__save_result_file(result)
                return 'skip'
            destination = self.__information['rule.status.destination.value'] = self.__load_result_file()['status']
        elif not isinstance(source, int):
            raise ValueError(f'Destination {destination} of {self.request.name} request must be an integer')
        operator = self.__information['rule.status.operator'] = config['operator']
        if operator == 'similar':
            similar_result = self.__information['rule.status.operator.value'] = source == destination
            return similar_result
        elif operator == 'different':
            different_result = self.__information['rule.status.operator.value'] = source != destination
            return different_result
        return False

    def __scan_key_value(self, config: dict[str, str | list[dict]], result: dict, type: str):
        final_condition = []
        self.__information[f'rule.{type}.logic'] = config['logic']
        for index, condition in enumerate(config['conditions']):
            self.__scan_operator(condition)
            source = condition['source'].split('@', 1)
            self.__information[f'rule.{type}.{index}.source'] = source[0]
            tmp_source = None
            if source[0] == f'[previous_{type}]':
                if not self.__check_result_file():
                    self.__save_result_file(result)
                    return 'skip'
                tmp_source = self.__load_result_file()[type]
            elif source[0] == f'[current_{type}]':
                tmp_source = result[type]
            else:
                raise ValueError(f"Config {config} of source at {index} must be in ['previous_{type}', 'current_{type}']")
            if len(source) == 2 and source[1] in tmp_source:
                tmp_source = tmp_source[source[1]]
            source = self.__information[f'rule.{type}.{index}.source.value'] = tmp_source

            destination = condition['destination'].split('@', 1)
            self.__information[f'rule.{type}.{index}.destination'] = destination[0]
            tmp_destination = None
            if destination[0] == f'[previous_{type}]':
                if not self.__check_result_file():
                    self.__save_result_file(result)
                    return 'skip'
                tmp_destination = self.__load_result_file()[type]
            elif destination[0] == f'[current_{type}]':
                tmp_destination = result[type]
            else:
                raise ValueError(f"Config {config} of destination at {index} must be in ['previous_{type}', 'current_{type}']")
            if len(destination) == 2 and destination[1] in tmp_destination:
                tmp_destination = tmp_destination[destination[1]]
            destination = self.__information[f'rule.{type}.{index}.destination.value'] = tmp_destination

            operator = self.__information[f'rule.{type}.{index}.operator'] = condition['operator']
            if operator == 'similar':
                similar_result = self.__information[f'rule.{type}.{index}.operator.value'] = source == destination
                final_condition.append(similar_result)
            elif operator == 'different':
                different_result = self.__information[f'rule.{type}.{index}.operator.value'] = source != destination
                final_condition.append(different_result)
            else:
                final_condition.append(False)

        return self.__determine_result(final_condition, config['logic'])

    def __check_result_file(self):
        return Path(self.result_file).exists()

    def __save_result_file(self, data: dict):
        file_path = Path(self.result_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(dumps(data, indent=4, ensure_ascii=True))

    def __load_result_file(self):
        return loads(Path(self.result_file).read_text())

    def __determine_result(self, result: list[str | bool], logic: str):
        if 'skip' in result:
            return False
        match logic:
            case 'and':
                return False if False in result else True
            case 'or':
                return True if True in result else False
        return False
