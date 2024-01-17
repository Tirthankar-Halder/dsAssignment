import asyncio
import aiohttp
import requests

url = "http://localhost:5000/"

async def make_request(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    
    num_requests = 10000
    results = {"Server 1": 0, "Server 2": 0, "Server 3": 0}

    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, url) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        server = response.split(":")[-1].strip()
        results[server] += 1

    print("Requests handled by each server instance:")
    print(results)

if __name__ == "__main__":

    ############# Test Analysis 1 ################

    asyncio.run(main())

    ############# Updating Replicas ###########

    # Endpoint 1: /rep
    response = requests.get(f"{url}/rep")
    print(response.json())

    # Endpoint 2: /add
    payload = {"n": 2, "hostnames": ["S5", "S4"]}
    response = requests.post(f"{url}/add", json=payload)
    print(response.json())

    # Endpoint 3: /rm
    payload = {"n": 2, "hostnames": ["S5", "S4"]}
    response = requests.delete(f"{url}/rm", json=payload)
    print(response.json())

    # Endpoint 4: /<path> (e.g., /home)
    response = requests.get(f"{url}/home")
    print(response.text)

    ############# Test Analysis 2 ################

    asyncio.run(main())