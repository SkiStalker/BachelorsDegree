import asyncio

import prometheus_api_client


async def main():
    prom = prometheus_api_client.PrometheusConnect("http://localhost:8080", disable_ssl=True)


if __name__ == '__main__':
    asyncio.run(main())
