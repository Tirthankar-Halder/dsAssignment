import requests


class ShardManager:
    def __init__(self, shard_table_url):
        self.shard_table_url = shard_table_url

    def detect_and_update_primary(self, down_server_id):
        # Example logic to detect down server and update primary server in metadata
        shard_table = requests.get(self.shard_table_url).json()
        for shard_entry in shard_table:
            if shard_entry['Primary'] == down_server_id:
                # Make one server as Primary (example logic)
                shard_entry['Primary'] = True
        # Update shard table
        response = requests.put(self.shard_table_url, json=shard_table)
        if response.status_code == 200:
            print("Primary server updated successfully.")
        else:
            print("Failed to update Primary server.")



