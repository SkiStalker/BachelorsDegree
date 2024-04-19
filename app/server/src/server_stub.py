import asyncio
import os
import random
import sys
import ssl

from aiohttp import web
from aiohttp_prometheus_exporter.handler import metrics

from aiohttp_prometheus_exporter.middleware import prometheus_middleware_factory

routes = web.RouteTableDef()


@routes.post('/')
async def hello(request: web.Request):
    if request.body_exists:
        resp_body = await request.json()
        print(resp_body)

    rand = random.randint(0, 2)
    await asyncio.sleep(rand)
    return web.Response(text=f"Operation time {rand} sec")


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)

    app.middlewares.append(prometheus_middleware_factory())
    app.router.add_get('/metrics', metrics())

    port = os.environ.get('serverPort', '443')
    if port is None:
        print("Server port not defined")
        sys.exit(-1)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain("./domain.crt", "./domain.key")
    web.run_app(app, port=int(port), ssl_context=ssl_context)
