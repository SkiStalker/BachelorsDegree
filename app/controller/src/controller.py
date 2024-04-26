import asyncio
import datetime
import json
import logging
import os
import subprocess
import sys
import time
from contextvars import ContextVar
from functools import wraps, partial
import re
import statistics

import prometheus_api_client
from aiohttp import web


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        p_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, p_func)

    return run


is_config_changed = ContextVar('is_config_changed', default=True)

routes = web.RouteTableDef()


@routes.post('/api/v1/config')
async def post_config(request: web.Request) -> web.Response:
    with open("./config.json", "w") as cfg_f:
        cfg_f.write(await request.text())
    is_config_changed.set(True)
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
        f'increase(aiohttp_request_duration_seconds_count{{path_template = "/"}}[{request.query["interval"]}])')

    return web.json_response({"values": res})


@routes.get('/api/v1/cpu_stat')
async def get_cpu_stat(request: web.Request):
    prom = app[prom_api_client]

    res = prom.custom_query(f'process_cpu_seconds_total[{request.query["interval"]}]')

    return web.json_response({"values": res})


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
    proc_res = subprocess.run("kubectl get pods -l=app=app -o jsonpath={.items[*].metadata.generateName}",
                              capture_output=True)

    proc_resp = proc_res.stdout.decode()

    return len(proc_resp.split(" "))


@async_wrap
def listen_prometheus(cur_app: web.Application):
    prom = cur_app[prom_api_client]

    cfg, step, change_delay, date_rules, cpu_rules, requests_rules = read_cfg()
    is_config_changed.set(False)

    while True:
        try:
            if is_config_changed.get() is True:
                cfg, step, change_delay, date_rules, cpu_rules, requests_rules = read_cfg()
                is_config_changed.set(False)

            cur_pods_count = kubectl_get_pods_count()

            dt_nec_pods_count = None

            dt_now = str(datetime.datetime.now())
            for dt in date_rules:
                if re.search(dt, dt_now) is not None:
                    dt_nec_pods_count = date_rules[dt]
                    break

            logger.info(f"Date rule selected: {dt_nec_pods_count}")

            cp_vals = [float(i["values"][-1][1]) for i in
                       prom.custom_query(f"process_cpu_seconds_total[{cfg['iteration_delay']}ms]")]

            if len(cp_vals) == 0:
                cp_vals.append(0)

            cp_cur_val = statistics.fmean(cp_vals)

            req_vals = [float(i["values"][-1][1]) for i in prom.custom_query(
                f'increase(aiohttp_request_duration_seconds_count{{path_template = "/"}}[{cfg["iteration_delay"]}ms])')]

            if len(req_vals) == 0:
                req_vals.append(0)

            req_cur_val = statistics.fmean(req_vals)

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
                        res_nec_pods_count = statistics.fmean(avg_list)
                case _:
                    res_nec_pods_count = cur_pods_count

            logger.info(f"Selected pods count {res_nec_pods_count}")

            if step is not None and change_delay is not None:
                if cur_pods_count < res_nec_pods_count:
                    cur_pods_count = min(cur_pods_count + step, res_nec_pods_count)
                    logger.info(f"Pods count reduced to {cur_pods_count}")
                    # subprocess.run(f"kubectl scale deployment app-deployment --replicas={cur_pods_count}")
                else:
                    cur_pods_count = max(cur_pods_count - step, res_nec_pods_count)
                    logger.info(f"Pods count increased to {cur_pods_count}")
                    # subprocess.run(f"kubectl scale deployment app-deployment --replicas={cur_pods_count}")

            time.sleep(cfg["iteration_delay"] / 1000.0)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(e)


async def background_tasks(cur_app: web.Application):
    app[prom_api_client] = prometheus_api_client.PrometheusConnect(
        os.environ.get("PROMETHEUS_HOST", "http://localhost:8080"), disable_ssl=True, )
    app[prometheus_listener] = asyncio.create_task(listen_prometheus(cur_app))

    yield

    app[prometheus_listener].cancel()
    await app[prometheus_listener]


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

    app.cleanup_ctx.append(background_tasks)

    app.add_routes(routes)

    web.run_app(app, host='localhost', port=8000)
