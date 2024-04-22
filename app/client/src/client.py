import asyncio
import urllib3

import aiohttp

urllib3.disable_warnings()


async def main():
    tasks = []
    sessions = []
    for _ in range(1, 1000):
        session = aiohttp.ClientSession()
        sessions.append(session)
        await_resp = session.post("https://158.160.156.231", ssl=False)
        tasks.append(await_resp)

    for task, session in zip(tasks, sessions):
        t = await task
        print(await t.text())
        await session.close()


if __name__ == '__main__':
    asyncio.run(main())
