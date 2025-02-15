import weaviate
from weaviate.classes.init import Auth
import os, json
from dotenv import load_dotenv
load_dotenv()
# Best practice: store your credentials in environment variables
wcd_url = os.getenv("WCD_URL")
wcd_api_key = os.getenv("WCD_API_KEY")
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=Auth.api_key(wcd_api_key),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
)

questions = client.collections.get("products")

response = questions.query.near_text(
    query="smartphone",
    limit=2
)

for obj in response.objects:
    print(json.dumps(obj.properties, indent=2))

client.close()  # Free up resources