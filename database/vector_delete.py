import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

load_dotenv()

wcd_url = os.getenv("WCD_URL")
wcd_api_key = os.getenv("WCD_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=Auth.api_key(wcd_api_key),
)

# Delete the existing collection if it exists
try:
    client.collections.delete("products")
    client.collections.delete("Laptops")
    client.collections.delete("Smartphones")
    client.collections.delete("Tablets")
    client.collections.delete("Smartwatches")
    client.collections.delete("Headphones")
    client.collections.delete("Monitors")
    print("Deleted existing 'Item' collection.")
except Exception as e:
    print(f"Error deleting collection: {e}")

client.close()