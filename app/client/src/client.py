import asyncio
import dataclasses
import math
import os
import uuid
import random
from asyncio import Future

import urllib3

import aiohttp

urllib3.disable_warnings()


@dataclasses.dataclass
class Automobile:
    auto_id: str = str(uuid.uuid4())
    fuel: float = 100
    balance: float = 10000
    velocity: float = 0
    position: tuple[float, float] = (random.randint(-180, 180), random.randint(-85, 85))


async def process():
    async with aiohttp.ClientSession() as session:
        a = Automobile()
        while True:
            try:
                if a.balance <= 0:
                    a.balance = 10000

                if a.fuel <= 0:
                    a.fuel = 100
                    a.velocity = 0
                    a.balance -= 2000
                # https://158.160.156.231
                resp = await session.post(os.environ.get("SERVER_HOST", 'https://localhost'), json=dataclasses.asdict(a), ssl=False)

                print(await resp.text())

                a.velocity += min(max(0.0, random.randint(-5, 5)), 200)

                a.fuel -= max(math.fabs(a.velocity) * 2, 0.0)

                new_pos_0 = a.position[0] + random.uniform(-0.1, 0.1)

                if new_pos_0 < -180:
                    new_pos_0 %= 180
                elif new_pos_0 > 180:
                    new_pos_0 %= -180

                new_pos_1 = a.position[1] + random.uniform(-0.1, 0.1)

                if new_pos_1 < -85:
                    new_pos_1 %= 85
                elif new_pos_1 > 85:
                    new_pos_1 %= -85

                a.position = new_pos_0, new_pos_1

                await asyncio.sleep(0.1)
                break
            except asyncio.CancelledError:
                break


async def main():
    global all_tasks
    try:
        tasks = []
        for _ in range(1):
            tasks.append(asyncio.create_task(process()))

        all_tasks = asyncio.gather(*tasks)
        await all_tasks

    except Exception as e:
        print(e)


if __name__ == '__main__':
    all_tasks: Future | None = None
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        all_tasks.cancel()
