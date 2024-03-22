import re
import  random
class ConsistentHashMap:
    def __init__(self, num_containers, total_slots, num_virtual_servers):
        self.num_containers = num_containers
        self.total_slots = total_slots
        self.num_virtual_servers = num_virtual_servers
        self.hash_map = [None] * total_slots

    def hash_function(self, i):
        return (i**2 + 4*i + 17) % self.total_slots

    def virtual_server_hash_function(self, i, j):
        return ((i**2) + (j**2) + (2 * j) + 25) % self.total_slots

    def add_server_container(self, server_container_Name_id):
        for _ in range(self.num_virtual_servers):
            j =  random.randint(100000,999999)
            virtual_server_id = f"{server_container_Name_id}-{j}"
            #regular expression is used to find the id in diverse user input of the server name
            server_container_id = ''.join(re.findall(r'\d',server_container_Name_id))
            slot = self.virtual_server_hash_function(int(server_container_id), j)
            #Linear Probing
            # while self.hash_map[slot] is not None:
            #     slot = (slot + 1) % self.total_slots  # Linear probing
            ### Quadratic Probing
            i=1
            while self.hash_map[slot] is not None:
                slot = (slot +i**2) % self.total_slots  #  probing
                i+=1#random.randint(1,1000)

            self.hash_map[slot] = virtual_server_id
    def remove_server_container(self, server_container_Name_id):
        for j in range(self.num_virtual_servers):
            #regular expression is used to find the id in diverse user input of the server name
            for slot in range(0,512):
                if self.hash_map[slot] is not None:
                    if server_container_Name_id in self.hash_map[slot]:
                        self.hash_map[slot]=None

            # Remove the virtual server from the hash map
        # return self.hash_map[slot].split("-")[0]

    def get_server_container(self, request_id):
        slot = self.hash_function(request_id)
        while self.hash_map[slot] is None:
            slot = (slot + 1) % self.total_slots  # Linear probing
        return self.hash_map[slot].split("-")[0]  # Extracting the server container ID
    
# Example usage
# consistent_hash_map = ConsistentHashMap(3, 512, 9)

# Adding server containers as integer
# for i in range(consistent_hash_map.num_containers):
#     consistent_hash_map.add_server_container(i)

# # Adding server containers as full name
# replicas = ["server 1","server 2","server 3"]
# for replica in replicas:
#     consistent_hash_map.add_server_container(replica)


# print(consistent_hash_map.hash_map)
# Mapping requests to server containers
# for i in range(5):
#     req_id=random.randint(100000,999999)
#     server_container_id = consistent_hash_map.get_server_container(req_id)
#     print(f"Request {req_id} is mapped to Server Container {server_container_id}")
