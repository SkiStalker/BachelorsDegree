import asyncio
import datetime
import json
import logging
import os
import sys
import time
import typing
from contextvars import ContextVar
from functools import wraps, partial
import re
import statistics

import asyncpg
import kubernetes
from kubernetes import client, config

import prometheus_api_client
from aiohttp import web


def ignore_exception(ignored_exception: typing.Type[Exception] = Exception, default_value: typing.Any | None = None):
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except ignored_exception:
                return default_value

        return _dec

    return dec


def to_json_serializable(obj: typing.Any) -> typing.Any | str:
    if ignore_exception(TypeError)(json.dumps)(obj) is None:
        return str(obj)
    return obj


def try_parse_int(s: str) -> int | None:
    return ignore_exception(ValueError)(int)(s)


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        p_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, p_func)

    return run


class ValueWrapper:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


is_config_changed = ContextVar('is_config_changed', default=ValueWrapper(True))
is_alive = ContextVar('is_alive', default=ValueWrapper(True))

routes = web.RouteTableDef()


@routes.post('/api/v1/config')
async def post_config(request: web.Request) -> web.Response:
    with open("./config.json", "w") as cfg_f:
        cfg_f.write(await request.text())
    is_config_changed.get().value = True
    return web.json_response({"message": "ok"})


@routes.get('/api/v1/config')
async def get_config(request: web.Request):
    if not os.path.isfile("./config.json"):
        return web.Response(status=404)

    with open("./config.json", "r") as cfg_f:
        cfg = cfg_f.read()

    return web.json_response(cfg)


@routes.get('/api/v1/requests_stat')
async def get_requests_stat(request: web.Request):
    prom = app[prom_api_client]

    res = prom.custom_query(
        'increase(aiohttp_requests_total{path_template="/"}[1m])')

    return web.json_response({"values": res})


@routes.get('/api/v1/cpu_stat')
async def get_cpu_stat(request: web.Request):
    prom = app[prom_api_client]

    res = prom.custom_query('increase(process_cpu_seconds_total[1m])')

    return web.json_response({"values": res})


@routes.get("/api/v1/auto_info")
async def get_auto_info(request: web.Request):
    query = request.query
    offset = query.get('offset', 0)

    if (offset := try_parse_int(offset)) is None:
        return web.json_response({"error": f"Incorrect offset value `{offset}`"}, status=400)

    limit = query.get('limit', 10)

    if (limit := try_parse_int(limit)) is None:
        return web.json_response({"error": f"Incorrect limit value `{limit}`"}, status=400)

    order_field = query.get('order_field', "created_at")
    if order_field not in app[available_order_fields]:
        return web.json_response({"error": f"Incorrect order field `{order_field}`"}, status=400)

    order_direction = query.get('order_direction', 'desc')
    if order_direction not in app[available_order_directions]:
        return web.json_response({"error": f"Incorrect order direction `{order_direction}`"}, status=400)

    filter_field = query.get('filter_field', None)

    if filter_field is not None:
        if filter_field not in app[available_order_fields]:
            return web.json_response({"error": f"Incorrect filer value `{filter_field}`"}, status=400)

    filter_value = query.get('filter_value', None)

    if filter_value is None and filter_field is not None:
        return web.json_response({"error": f"Filter field `{filter_field}` passed, but no value was provided"},
                                 status=400)
    elif filter_value is not None and filter_field is None:
        return web.json_response({"error": f"Filter value `{filter_value}` passed, but no field was provided"},
                                 status=400)

    async with app[pg_db_pool].acquire() as conn:
        conn: asyncpg.Connection = conn

        fetch_str = f'SELECT *, COUNT(*) as count FROM auto_info WHERE 1=1 '

        where_str = f" AND CAST ({filter_field} AS TEXT) LIKE '%{filter_value}%' " if filter_field is not None else " "

        group_by_str = " GROUP BY id, auto_id, driver_id, positiony, positionx, fuel, balance, velocity, created_at "

        off_limit_order_srt = f" ORDER BY {order_field} {order_direction.upper()} OFFSET {offset} LIMIT {limit}"

        resp = await conn.fetch(fetch_str + where_str + group_by_str+  off_limit_order_srt)

    return web.json_response(
        {"data": [dict({key: to_json_serializable(value) for key, value in row.items()}) for row in resp]})


@routes.get("/api/v1/pods_count")
async def get_pods_count(request: web.Request):
    return web.json_response({"pods_count": kubectl_get_pods_count()})


def read_cfg():
    with open("./config.json", "r") as cfg_f:
        cfg = json.loads(cfg_f.read())

    if "one_time_change" in cfg:
        step = cfg["one_time_change"]["step"]
        change_delay = cfg["one_time_change"]["step"]
    else:
        step = None
        change_delay = None

    date_rules = {}

    cpu_rules: list | None = None

    requests_rules: list | None = None

    for rule in cfg["rules"]:
        if rule["type"] == "date":
            rule["values"].sort(key=lambda x: len(x["value"]), reverse=True)
            date_rules.update({
                f"{obj['value'].get('year', '(.*?)')}-{obj['value'].get('month', '(.*?)')}"
                f"-{obj['value'].get('day', '(.*?)')} {obj['value'].get('hour', '(.*?)')}"
                f":{obj['value'].get('minute', '(.*?)')}:(.*?)[.](.*)":
                    obj["replicas"] for obj in rule["values"]})

        elif rule["type"] == "workload":
            if rule["metric"] == "request_per_second":
                rule["values"].sort(key=lambda x: x["value"])
                requests_rules = rule["values"]
            elif rule["metric"] == "total_cpu":
                rule["values"].sort(key=lambda x: x["value"])
                cpu_rules = rule["values"]
            else:
                logger.warning(f"Unknown workload rule type '{rule['metric']}'")
        else:
            logger.warning(f"Unknown rule type '{rule['type']}'")

    return cfg, step, change_delay, date_rules, cpu_rules, requests_rules


def kubectl_get_pods_count():
    res: kubernetes.client.models.v1_pod_list.V1PodList = app[kube_core_api_client].list_namespaced_pod(
        namespace="default", label_selector="app=app")
    return len(res.items)


@async_wrap
def listen_prometheus(cur_app: web.Application):
    prom = cur_app[prom_api_client]

    cfg, step, change_delay, date_rules, cpu_rules, requests_rules = read_cfg()

    is_config_changed.get().value = False

    while True:
        try:

            if is_alive.get().value is False:
                break

            if is_config_changed.get().value is True:
                cfg, step, change_delay, date_rules, cpu_rules, requests_rules = read_cfg()
                is_config_changed.get().value = False

            cur_pods_count = kubectl_get_pods_count()

            logger.info(f"Current pods count {cur_pods_count}")

            dt_nec_pods_count = None

            dt_now = str(datetime.datetime.now())
            for dt in date_rules:
                if re.search(dt, dt_now) is not None:
                    dt_nec_pods_count = date_rules[dt]
                    break

            logger.info(f"Date rule selected: {dt_nec_pods_count}")

            cp_vals = [(float(i["value"][1]) / 60000) * cfg["iteration_delay"] for i in
                       prom.custom_query("increase(process_cpu_seconds_total[1m])")]

            if len(cp_vals) == 0:
                cp_vals.append(0)

            cp_cur_val = statistics.fmean(cp_vals)

            logger.info(f"CPU current: {cp_cur_val}")

            req_vals = [(float(i["value"][1]) / 60000 * cfg["iteration_delay"]) for i in prom.custom_query(
                'increase(aiohttp_requests_total{path_template="/"}[1m])')]

            if len(req_vals) == 0:
                req_vals.append(0)

            req_cur_val = sum(req_vals)

            logger.info(f"Requests current: {req_cur_val}")

            cp_nec_pods_count = None
            req_nec_pods_count = None

            for cp in cpu_rules:
                if cp["value"] <= cp_cur_val:
                    cp_nec_pods_count = cp["replicas"]
                else:
                    break

            logger.info(f"CPU rule selected: {cp_nec_pods_count}")

            for req in requests_rules:
                if req["value"] <= req_cur_val:
                    req_nec_pods_count = req["replicas"]
                else:
                    break

            logger.info(f"Requests rule selected: {cp_nec_pods_count}")

            match cfg["change_policy"]:
                case "max":
                    res_nec_pods_count = max(dt_nec_pods_count or 0, req_nec_pods_count or 0, cp_nec_pods_count or 0)
                case "min":
                    res_nec_pods_count = min(dt_nec_pods_count or float("inf"), req_nec_pods_count or float("inf"),
                                             cp_nec_pods_count or float("inf"))
                case "avg":
                    avg_list = []
                    if dt_nec_pods_count:
                        avg_list.append(dt_nec_pods_count)
                    if req_nec_pods_count:
                        avg_list.append(req_nec_pods_count)
                    if cp_nec_pods_count:
                        avg_list.append(cp_nec_pods_count)

                    if len(avg_list) == 0:
                        res_nec_pods_count = cur_pods_count
                    else:
                        res_nec_pods_count = round(statistics.fmean(avg_list))
                case _:
                    res_nec_pods_count = cur_pods_count

            logger.info(f"Selected pods count {res_nec_pods_count}")

            if step is not None and change_delay is not None:
                if cur_pods_count < res_nec_pods_count:
                    cur_pods_count = max(min(cur_pods_count + step, res_nec_pods_count), 1)
                    logger.info(f"Pods count reduced to {cur_pods_count}")
                    app[kube_apps_api_client].patch_namespaced_deployment_scale("app-deployment", "default",
                                                                                {'spec': {'replicas': cur_pods_count}})
                elif cur_pods_count > res_nec_pods_count:
                    cur_pods_count = max(max(cur_pods_count - step, res_nec_pods_count), 1)
                    logger.info(f"Pods count increased to {cur_pods_count}")
                    app[kube_apps_api_client].patch_namespaced_deployment_scale("app-deployment", "default",
                                                                                {'spec': {'replicas': cur_pods_count}})

            time.sleep(cfg["iteration_delay"] / 1000.0)
        except Exception as e:
            logger.error(e)


async def config_app(cur_app: web.Application):
    cur_app[available_order_fields] = ["id", "auto_id", "positionx", "positiony", "fuel", "balance", "velocity",
                                       "created_at", "driver_id"]
    cur_app[available_order_directions] = ["asc", "desc"]

    yield


async def background_tasks(cur_app: web.Application):
    cur_app[prom_api_client] = prometheus_api_client.PrometheusConnect(
        os.environ.get("PROMETHEUS_HOST", "http://localhost:8080"), disable_ssl=True)

    cur_app[prometheus_listener] = asyncio.create_task(listen_prometheus(cur_app))

    config.load_config()

    cur_app[kube_apps_api_client] = client.AppsV1Api()
    cur_app[kube_core_api_client] = client.CoreV1Api()

    cur_app[pg_db_pool] = await asyncpg.create_pool(host=os.environ.get('PG_HOST', "localhost"),
                                                    port=os.environ.get('PG_PORT', 5432),
                                                    user=os.environ.get('PG_USER', "postgres"),
                                                    password=os.environ.get('PG_PASSWORD', "pgpass"),
                                                    database=os.environ.get('PG_DATABASE', "postgres"))

    yield

    is_alive.get().value = False

    cur_app[prometheus_listener].cancel()

    await cur_app[prometheus_listener]

    cur_app[kube_apps_api_client].api_client.close()
    cur_app[kube_core_api_client].api_client.close()

    await cur_app[pg_db_pool].close()


if __name__ == '__main__':

    logger = logging.Logger(__name__)

    cli_handler = logging.StreamHandler(sys.stdout)
    cli_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s"))
    cli_handler.setLevel(logging.INFO)
    logger.addHandler(cli_handler)

    if not os.path.isfile("./config.json"):
        with open("./config.json", "w") as f:
            f.write(json.dumps({"delay": 1000, "rules": []}))

    app = web.Application()

    prometheus_listener = web.AppKey("prometheus_listener", asyncio.Task[None])
    prom_api_client = web.AppKey("prom_api_client", prometheus_api_client.PrometheusConnect)

    kube_apps_api_client = web.AppKey("kube_apps_api_client", client.AppsV1Api)
    kube_core_api_client = web.AppKey("kube_core_api_client", client.CoreV1Api)

    available_order_fields = web.AppKey("available_order_fields", list[str])
    available_order_directions = web.AppKey("available_order_directions", list[str])

    pg_db_pool = web.AppKey("pg_db_pool", asyncpg.Pool)

    app.cleanup_ctx.append(background_tasks)
    app.cleanup_ctx.append(config_app)

    app.add_routes(routes)

    web.run_app(app, host=os.environ.get("CONTROLLER_HOST", 'localhost'),
                port=int(os.environ.get("CONTROLLER_PORT", 8000)))
