import datetime
import logging
import os
import sys
import ssl
import asyncpg

from aiohttp import web
from aiohttp_prometheus_exporter.handler import metrics

from aiohttp_prometheus_exporter.middleware import prometheus_middleware_factory

routes = web.RouteTableDef()


@routes.post('/')
async def write_auto_info(request: web.Request):
    if request.body_exists:
        json_data = await request.json()
        async with app[pg_db_pool].acquire() as conn:
            exec_str = (
                f'INSERT INTO auto_info (auto_id, driver_id, fuel, balance, velocity, positionx, positiony, created_at) '
                f'VALUES (\'{json_data["auto_id"]}\', \'{json_data["driver_id"]}\', {json_data["fuel"]}, '
                f'{json_data["balance"]}, '
                f'{json_data["velocity"]}, {json_data["position"][0]}, {json_data["position"][1]}, '
                f'\'{datetime.datetime.now()}\')')

            res = await conn.execute(exec_str)

        logger.info(res)

        return web.json_response({"message": "OK"})

    else:
        return web.json_response({"error": "Request body is missing"}, status=400)


async def background_tasks(cur_app: web.Application):
    cur_app[pg_db_pool] = await asyncpg.create_pool(host=os.environ.get('PG_HOST', "localhost"),
                                                    port=os.environ.get('PG_PORT', 5432),
                                                    user=os.environ.get('PG_USER', "postgres"),
                                                    password=os.environ.get('PG_PASSWORD', "pgpass"),
                                                    database=os.environ.get('PG_DATABASE', "postgres"))

    yield

    await cur_app[pg_db_pool].close()


if __name__ == '__main__':
    logger = logging.Logger(__name__)
    cli_handler = logging.StreamHandler(sys.stdout)
    cli_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s"))
    cli_handler.setLevel(logging.INFO)
    logger.addHandler(cli_handler)

    app = web.Application()
    app.add_routes(routes)

    app.middlewares.append(prometheus_middleware_factory())
    app.router.add_get('/metrics', metrics())

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(os.environ.get("HOST_CERT_PATH", "./domain.crt"),
                                os.environ.get("HOST_KEY_PATH", "./domain.key"))

    pg_db_pool = web.AppKey("pg_db_pool", asyncpg.Pool)

    app.cleanup_ctx.append(background_tasks)

    port = os.environ.get('HOST_PORT', '443')

    host = os.environ.get("HOST_IP", "localhost")

    web.run_app(app, host=host, port=int(port), ssl_context=ssl_context)
