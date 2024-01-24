Implimenting a Customizable Load Balancer

   ![image](https://github.com/Tirthankar-Halder/dsAssignment/assets/64760892/f8df9a7b-1fe3-4dcf-8dfb-45c7c33e1a71)

# Design

This repository implements a loadbalancer system which uses Consistent Hashmaping technnique for the the allocation of servers and client requests simulteniously further it uses the concept of virtual server of better performence. 

We use Python as a programming language and<strong> Flask </strong>module for http endpoints for the interaction over the network.For the generation of asynchronous requests <strong>asyncio aiohttp </strong> libraries are used.


<ol type="1">
 <li><strong>Load-balancer</strong> is mainly responsible for accepting asynchronous http requests from client and distributes among the servers.</li>
 <li><strong>Consistent Hashmap </strong> Consistent hashing has a unique hashing structure that is circular instead of linear to avoid many shifts of data in
the event of the addition of resources to the system. Load Balancer uses consistent hashing to distribute client requests
evenly among the server instances (i.e., balancing the system load). Moreover, consistent hashing technique is also used in
distributed caching systems for better utilization of resources.</li><li><strong>Server</strong> has two endpoints "/home" endpoint returns a unique identifier to distinguish among the replicas and "/heartbeat" this endpoint sends heartbeat responses upon request. The load balancer further
uses the heartbeat endpoint to identify failures in the set of containers maintained by it.
</ol>

# Assumptions




# Challenges






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
