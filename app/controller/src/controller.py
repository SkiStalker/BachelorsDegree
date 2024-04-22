import asyncio

import prometheus_api_client


async def main():
    prom = prometheus_api_client.PrometheusConnect("http://localhost:8080", disable_ssl=True)
    resp = prom.all_metrics()

    increase = 'irate(aiohttp_request_duration_seconds_count{path_template = "/"}[1m])'
    total_processor_time = 'process_cpu_seconds_total[1m]'

    kubectl_get_pods_count = "kubectl get pods -l=app=app -o jsonpath={.items[*].metadata.generateName}"

    


    a = 12


if __name__ == '__main__':
    asyncio.run(main())
