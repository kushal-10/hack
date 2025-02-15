import weaviate
import weaviate.classes.config as wc
import os
import json
from weaviate.classes.init import Auth
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment variables
wcd_url = os.getenv("WCD_URL")
wcd_api_key = os.getenv("WCD_API_KEY")

# Initialize the Weaviate client
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=Auth.api_key(wcd_api_key),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
)

class_name = "products"

# Define the collection schema with nested properties for 'features'
properties = [
    wc.Property(name="name", data_type=wc.DataType.TEXT),
    wc.Property(name="category", data_type=wc.DataType.TEXT),
    wc.Property(name="price", data_type=wc.DataType.NUMBER),
    wc.Property(name="features", data_type=wc.DataType.TEXT),
]

# Create the collection
client.collections.create(
    name=class_name,
    properties=properties,
    vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
    generative_config=wc.Configure.Generative.openai(),
)

# Load the data
with open('database/sample2.json', 'r') as file:
    data = json.load(file)["products"]

# Import data using collection API
try:
    collection = client.collections.get(class_name)
    
    # Process items in smaller batches
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i + batch_size]
        objects_to_import = [
            {
                "name": d["name"],
                "category": d["category"],
                "price": d["price"],
                "features": d["features"],
            }
            for d in batch_data
        ]
        
        result = collection.data.insert_many(objects=objects_to_import)
        
        # Check for errors
        if hasattr(result, 'errors') and result.errors:
            print(f"Errors in batch {i//batch_size + 1}:")
            for error in result.errors:
                print(f"Error: {error}")
        
        print(f"Imported batch {i//batch_size + 1} ({len(batch_data)} items)")

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    client.close()

print("Import completed!")