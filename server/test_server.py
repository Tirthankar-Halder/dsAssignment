import unittest
import json
from server import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Welcome to HELLO WORLD")

    
    def test_home_route(self):
        response = self.app.get('/home')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data.decode())
        self.assertEqual(response_json["status"], "successful")

    def test_heartbeat_route(self):
        response = self.app.get('/heartbeat')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data.decode())
        self.assertEqual(response_json["Response"], " ")

if __name__ == '__main__':
    unittest.main()