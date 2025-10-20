from asyncio import gather, run
from environment import Environment
from request import Request

async def main():
    requests = Environment.analyze_env()

    tasks = []
    for request in requests:
        request = Request(request['name'], request['url'], request['method'], request['content_type'], request['headers'], request['body'])
        tasks.append(request.perform())

    results = await gather(*tasks)

    for i, res in enumerate(results):
        print(f"Response {i}: {res['headers'], res['body']}")

if __name__ == '__main__':
    run(main())
