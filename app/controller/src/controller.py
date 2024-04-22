import asyncio
import os

import prometheus_api_client
from aiohttp import web

routes = web.RouteTableDef()


@routes.post('/config')
async def post_config(request):
    with open("./config.json", "w") as f:
        f.write(request.body)
    return web.Response()


@routes.get('/config')
async def get_config(request):
    if not os.path.isfile("./config.json"):
        return web.Response(status=404)

    with open("./config.json", "r") as f:
        cfg = f.read()

    return web.json_response(cfg)


async def listen_prometheus(cur_app: web.Application):
    prom = prometheus_api_client.PrometheusConnect("http://localhost:8080", disable_ssl=True)

    while True:
        try:
            resp = prom.all_metrics()
        except asyncio.CancelledError:
            break

    increase = 'irate(aiohttp_request_duration_seconds_count{path_template = "/"}[1m])'
    total_processor_time = 'process_cpu_seconds_total[1m]'

    kubectl_get_pods_count = "kubectl get pods -l=app=app -o jsonpath={.items[*].metadata.generateName}"


async def background_tasks(cur_app: web.Application):
    app[prometheus_listener] = asyncio.create_task(listen_prometheus(cur_app))
    yield

    app[prometheus_listener].cancel()
    await app[prometheus_listener]


if __name__ == '__main__':
    app = web.Application()
    prometheus_listener = web.AppKey("prometheus_listener", asyncio.Task[None])

    app.cleanup_ctx.append(background_tasks)

    app.add_routes(routes)

    web.run_app(app, host='localhost', port=8000)
