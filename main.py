from asyncio     import gather, run
from environment import Environment
from logging     import basicConfig, DEBUG
from request     import Request
from rule        import Rule
from trigger     import Trigger, Email as EmailAction, Request as RequestAction

basicConfig(
    level=DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

async def main():
    configs = Environment.analyze_env()

    tasks = []
    for config in configs:
        request = Request(
            config['name'],
            config['url'],
            config['method'],
            config['timeout'],
            config['content_type'],
            config['headers'],
            config['body'],
        )
        trigger = Trigger(
            config['trigger']['action'],
            EmailAction(
                config['trigger']['email']['username'],
                config['trigger']['email']['password'],
                config['trigger']['email']['receivers'],
                config['trigger']['email']['subject'],
                config['trigger']['email']['body'],
                config['trigger']['email']['server'],
                config['trigger']['email']['port'],
            ),
            RequestAction(
                config['trigger']['request']['url'],
                config['trigger']['request']['method'],
                config['trigger']['request']['headers'],
                config['trigger']['request']['body'],
            ),
        )
        rule = Rule(
            config['rule']['schema'],
            config['rule']['logic'],
            f'{config['result_dir']}/{config['name']}.json',
            request,
            trigger,
        )
        tasks.append(rule.perform())

    await gather(*tasks)

if __name__ == '__main__':
    run(main())
