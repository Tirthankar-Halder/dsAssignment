Implimenting a Customizable Load Balancer

## Assignment - I

<p align="center">
      <img src="assets/assign_1.png" width="70%"/>
</p>

## Assignment - II

<p align="center">
      <img src="assets/assign_2.png" width="70%"/>
</p>

# Design

This repository implements a loadbalancer system which uses Consistent Hashmaping technnique for the the allocation of servers and client requests simulteniously further it uses the concept of virtual server of better performence. 

We use Python as a programming language and<strong> Flask </strong>module for http endpoints for the interaction over the network.For the generation of asynchronous requests <strong>asyncio aiohttp </strong> libraries are used.


<ol type="1">
 <li><strong>Load-balancer</strong> is mainly responsible for accepting asynchronous http requests from client and distributes among the servers.</li>
 
 <li><strong>Consistent Hashmap </strong> Consistent hashing has a unique hashing structure that is circular instead of linear to avoid many shifts of data in
the event of the addition of resources to the system. Load Balancer uses consistent hashing to distribute client requests
evenly among the server instances (i.e., balancing the system load). Moreover, consistent hashing technique is also used in
distributed caching systems for better utilization of resources.</li>

<li><strong>Server</strong> has two endpoints "/home" endpoint returns a unique identifier to distinguish among the replicas and "/heartbeat" this endpoint sends heartbeat responses upon request. The load balancer further
uses the heartbeat endpoint to identify failures in the set of containers maintained by it.</li>

<li><strong>Shard</strong> has two endpoints "/home" endpoint returns a unique identifier to distinguish among the replicas and "/heartbeat" this endpoint sends heartbeat responses upon request. The load balancer further
uses the heartbeat endpoint to identify failures in the set of containers maintained by it.</li>

</ol>

# Assumptions
## Assignment - I

+ For the server ids we have use six digit random numbers which servers the purpose of non cluster allocation of virtual servers.
+ For removing servers, if the no.of servers are more than the length of Hostname then random servers are chosen and removed.
+ For analisys part when servers are increasing, we put a 10 second halt.
+ Statistically, K = log (M) (K = no. of virtual server, M = no. of slots.) virtual servers work best to distribute the load across the
physical server instances equally.
+ In case of faliure of server, we have manually down the server.

## Assignment - II



# Challenges

## Assignment - I

+ Sending the request to the load-balancer and tracking the server load was quite challenging.
+ However we have noticed that a large number of server container allocation might affect the performence of the system.
+ In real case scenario servers may get down for various reasons but in our case servers are running on docker container it is challenging to down them automatically. 

## Assignment - II



# Prerequisites

### 1. Docker: latest [version 20.10.23, build 7155243]

    sudo apt-get update

    sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io
    

### 2. Docker-compose standalone [version v2.15.1]
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

### 3. MYSQL:8.0
    FROM mysql:8.0-debian
    COPY deploy.sh /always-initdb.d/ #here the flask app deploy script is copied
    COPY . /bkr
    WORKDIR /bkr

    RUN apt-get update
    RUN apt-get install -y python3
    RUN apt-get install -y python3-pip

    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt

    ENV MYSQL_ROOT_PASSWORD="abc" #host=’localhost’, user=’root’,password=’abc’

    EXPOSE 5000

# Installation Steps
### Deploy Sever
#### Build the Server Docker Image

    cd ./server/ && sudo docker build -t server .

### Deploy Loadbalancer
#### Build the LoadBalancer Docker Image
    make build
#### Run the LoadBalancer Docker Image
    make up


### Remove/Stop Loadbalancer/Server
    make down



# Testing
## Assignment - I
Initially, 10,000 asynchronous requests were sent to the load balancer, which distributed them among the existing three servers. Subsequently, the number of servers was increased by one, and for each iteration, another 10,000 asynchronous requests were sent to the load balancer. Upon analyzing the load balancer's performance, it was observed that it efficiently distributed the requests, effectively managing the network load. 
+ ### Increasing no of Servers by one:
The bar plot visually depicts the average number of requests handled by each server.
Test results are as follows:
<p align="center">
      <img src="results/AnalysisServerRemove.jpg" width="50%"/>
</p>

+ ### Decreasing no of Servers by one:
<p align="center">
      <img src="results/AnalysisServerAddition.jpg" width="50%"/>
</p>

## Assignment - II

# Edge-Cases
## Assignment - II

# Contact Me

This is Assignment 1 & 2 of CS60002: Distributed Systems course in IIT Kharagpur, taught by [Dr. Sandip Chakraborty](https://cse.iitkgp.ac.in/~sandipc/).