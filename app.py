from flask import  (Flask,request,jsonify,render_template,abort,url_for,json)
import asyncio  # pip install the packages
import aiohttp 
import random
import requests
from collections import defaultdict

app=Flask(__name__)
# testing <paths>
""" def requested(req):
    url = "http://10.171.9.221:5000/{}".format(req)
    response=requests.get(url)
    try:
        if response.status_code==200:
            response_data = response.json()
            print('Received from server:',data['message'])
            return data['message']
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {e}")
        print(f"API Response Content: {response.text}")
        return None """
    	
      
    
async def make_request(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    endpoint=random.choice(['home','heartbeat','path']) #implimented to check diffrent endpoints
    url = "http://10.171.9.221:5000/{}".format(endpoint)
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

    #for i in range(5):
        #endpoint=random.choice(['home','heartbeat','path'])
        #data=requested(endpoint)
        #print(data)
    	
    #asyncio.run(main())
# Additional routes and configurations can be added here



