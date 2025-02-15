import weaviate
from weaviate.classes.init import Auth
import os
import json
from dotenv import load_dotenv

load_dotenv()

def connect_to_weaviate():
    """Connect to Weaviate and return the client."""
    wcd_url = os.getenv("WCD_URL")
    wcd_api_key = os.getenv("WCD_API_KEY")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=wcd_url,
        auth_credentials=Auth.api_key(wcd_api_key),
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
    )
    return client

def search_products(client, query, limit=2):
    """Search for products in Weaviate using a near_text query."""
    questions = client.collections.get("products")

    response = questions.query.near_text(
        query=query,
        limit=limit
    )

    results = [json.dumps(obj.properties, indent=2) for obj in response.objects]
    return results

def disconnect_weaviate(client):
    client.close()  # Free up resources

def main():
    client = connect_to_weaviate()
    try:
        results = search_products(client, query="smartphone", limit=2)
        for result in results:
            print(result)
    finally:
        client.close()  # Free up resources

if __name__ == "__main__":
    main()