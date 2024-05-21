import asyncio
import dataclasses
import math
import os
import uuid
import random
from asyncio import Future
import datetime

import urllib3

import aiohttp

urllib3.disable_warnings()


@dataclasses.dataclass
class Automobile:
    auto_id: str
    driver_id: str
    position: tuple[float, float]
    fuel: float = 100
    balance: float = 10000
    velocity: float = 0


async def process(ind: int):
    r = random.Random(datetime.datetime.now().timestamp() + ind)
    async with aiohttp.ClientSession() as session:
        a = Automobile(auto_id=str(uuid.UUID(int=r.getrandbits(128), version=4)),
                       driver_id=str(uuid.UUID(int=r.getrandbits(128), version=4)),
                       position=(r.randint(-180, 180), r.randint(-90, 90)))
        while True:
            try:
                if a.balance <= 0:
                    a.balance = 10000

                if a.fuel <= 0:
                    a.fuel = 100
                    a.velocity = 0
                    a.balance -= 2000
                resp = await session.post(os.environ.get("SERVER_HOST", 'https://158.160.163.0'),
                                          json=dataclasses.asdict(a), ssl=False)

                print(await resp.text())

                a.velocity += min(max(0.0, r.randint(-5, 5)), 200)

                a.fuel -= max(math.fabs(a.velocity) * 2, 0.0)

                new_pos_0 = a.position[0] + r.uniform(-0.1, 0.1)

                if new_pos_0 < -180:
                    new_pos_0 %= 180
                elif new_pos_0 > 180:
                    new_pos_0 %= -180

                new_pos_1 = a.position[1] + r.uniform(-0.1, 0.1)

                if new_pos_1 < -90:
                    new_pos_1 %= 90
                elif new_pos_1 > 90:
                    new_pos_1 %= -90

                a.position = new_pos_0, new_pos_1

                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break


async def main():
    global all_tasks
    try:
        tasks = []
        for i in range(10):
            tasks.append(asyncio.create_task(process(i)))
            await asyncio.sleep(10)

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
