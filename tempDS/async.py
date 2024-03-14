import asyncio
import aiohttp
import requests
import json
import matplotlib.pyplot as plt
from collections import defaultdict


async def make_request(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    url = "http://10.171.9.221:5000/home"
    num_requests = 10000
    results = defaultdict(lambda :0)

    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, url) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        # print(response)
        server = json.loads(response)["message"].split(":")[-1].strip()
        results[server] += 1

    print("Requests handled by each server instance:")
    return results

l=[]
if __name__ == "__main__":
    res=asyncio.run(main())
    print(res)