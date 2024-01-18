class ConsistentHashMap:
    def __init__(self, num_containers, total_slots, num_virtual_servers):
        self.num_containers = num_containers
        self.total_slots = total_slots
        self.num_virtual_servers = num_virtual_servers
        self.hash_map = [None] * total_slots

    def hash_function(self, i):
        return (i**2 + 2 * i + 17) % self.total_slots

    def virtual_server_hash_function(self, i, j):
        return ((i**2) + (j**2) + (2 * j) + 25) % self.total_slots

    def add_server_container(self, server_container_id):
        for j in range(self.num_virtual_servers):
            virtual_server_id = f"{server_container_id}-{j}"
            slot = self.virtual_server_hash_function(server_container_id, j)
            while self.hash_map[slot] is not None:
                slot = (slot + 1) % self.total_slots  # Linear probing
            self.hash_map[slot] = virtual_server_id
    def remove_server_container(self, server_container_id):
        for j in range(self.num_virtual_servers):
            virtual_server_id = f"{server_container_id}-{j}"
            slot = self.virtual_server_hash_function(server_container_id, j)
            
            while self.hash_map[slot] != virtual_server_id:
                slot = (slot + 1) % self.total_slots  # Find the slot

            # Remove the virtual server from the hash map
            self.hash_map[slot] = None
        # return self.hash_map[slot].split("-")[0]

    def get_server_container(self, request_id):
        slot = self.hash_function(request_id)
        while self.hash_map[slot] is None:
            slot = (slot + 1) % self.total_slots  # Linear probing
        return self.hash_map[slot].split("-")[0]  # Extracting the server container ID
    
# Example usage
# consistent_hash_map = ConsistentHashMap(3, 512, 9)

# # # Adding server containers
# for i in range(consistent_hash_map.num_containers):
#     consistent_hash_map.add_server_container(i)
# replicas = ["server 1","server 2","server 3"]
# for replica in replicas:
#     consistent_hash_map.add_server_container(int(replica[7]))
# # Mapping requests to server containers
# requests = [5, 12, 25, 37, 50]
# for request_id in requests:
#     server_container_id = consistent_hash_map.get_server_container(request_id)
#     print(f"Request {request_id} is mapped to Server Container {server_container_id}")
