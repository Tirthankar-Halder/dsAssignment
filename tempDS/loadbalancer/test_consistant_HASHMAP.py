import unittest
from consistant_HASHMAP import ConsistentHashMap

class TestConsistentHashMap(unittest.TestCase):

    def setUp(self):
        print("\nRunning setUp method...")
        self.consistent_hash_map = ConsistentHashMap(3, 512, 9)

    def tearDown(self):
        print("Running tearDown method...")
        
    def test_hash_function(self):
        self.assertEqual(self.consistent_hash_map.hash_function(1012),137)
        self.assertEqual(self.consistent_hash_map.hash_function(234280),161)
        self.assertEqual(self.consistent_hash_map.hash_function(234),457)
        self.assertEqual(self.consistent_hash_map.hash_function(12),185)
        self.assertEqual(self.consistent_hash_map.hash_function(12798),17)
        self.assertEqual(self.consistent_hash_map.hash_function(12800),17)
    def test_virtual_server_hash_function(self):
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,0),474)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,1),477)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,2),482)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,3),489)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,4),498)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,5),509)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,6),10)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,7),25)
        self.assertEqual(self.consistent_hash_map.virtual_server_hash_function(4321,8),42)

    def test_add_server_container(self):
        self.consistent_hash_map.add_server_container("server 4321")
        self.assertEqual(self.consistent_hash_map.hash_map.count(None), 503)  # 512 total slots - 1 occupied slot
    
    def test_remove_server_container(self):
        # Add a server container
        self.consistent_hash_map.add_server_container("server 1")

        # Remove the server container
        self.consistent_hash_map.remove_server_container("server 1")
        self.assertEqual(self.consistent_hash_map.hash_map.count(None), 512)  # All slots should be empty
    
    # def test_get_server_container(self):
    #     # Add server containers
    #     for i in range(self.consistent_hash_map.num_containers):
    #         self.consistent_hash_map.add_server_container(i+1)

    #     # Map requests to server containers and check if the result is as expected
    #     requests = [5, 12, 25, 37, 50]
    #     expected_mappings = ['2', '1', '1', '1', '3']

    #     for i, request_id in enumerate(requests):
    #         with self.subTest(request_id=request_id):
    #             server_container_id = self.consistent_hash_map.get_server_container(request_id)
    #             self.assertEqual(server_container_id, expected_mappings[i])
                
if __name__=='__main__':
	unittest.main()