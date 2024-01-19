import unittest
from consistant_HASHMAP import ConsistentHashMap

class TestConsistentHashMap(unittest.TestCase):

    def setUp(self):
        print("\nRunning setUp method...")
        self.hasher = ConsistentHashMap(3, 512, 9)

    def tearDown(self):
        print("Running tearDown method...")
        
    def test_hash_function(self):
        self.assertEquals(1,1)
    def test_virtual_server_hash_function(self):
        self.assertEquals(1,1)
    def test_add_server_container(self):
        self.assertEquals(1,1)
    def test_remove_server_container(self):
        self.assertEquals(1,1)
    def test_get_server_container(self):
        self.assertEquals(1,1)
    
if __name__=='__main__':
	unittest.main()