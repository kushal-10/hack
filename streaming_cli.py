import asyncio
import os

from pynput import keyboard
from openai_realtime_client import RealtimeClient, AudioHandler, InputHandler, TurnDetectionMode
from llama_index.core.tools import FunctionTool
from prompt import SYSTEM_PROMPT
from database.vector_search_callable import connect_to_weaviate, search_products, disconnect_weaviate

W_CLIENT = ""
# Format the SYSTEM_PROMPT with the variables
formatted_prompt = SYSTEM_PROMPT.format(
    PRODUCT_CATEGORY="smartphones",
    MIN_PRICE="-10%"
)

# Add your own tools here!
# NOTE: FunctionTool parses the docstring to get description, the tool name is the function name
def get_phone_number(name: str) -> str:
    """Get my phone number."""
    if name == "Jerry":
        return "1234567890"
    elif name == "Logan":
        return "0987654321"
    else:
        return "Unknown"

# NOTE: FunctionTool parses the docstring to get description, the tool product is the function product
def get_products(product: str) -> str:
    """Get specific products."""
    return search_products(W_CLIENT, query=product, limit=2)

tools = [
    FunctionTool.from_defaults(fn=get_phone_number),
    FunctionTool.from_defaults(fn=get_products)
]

async def main():
    global W_CLIENT
    audio_handler = AudioHandler()
    input_handler = InputHandler()
    input_handler.loop = asyncio.get_running_loop()
    W_CLIENT = connect_to_weaviate()
    client = RealtimeClient(
        api_key=os.environ.get("OPENAI_API_KEY"),
        on_text_delta=lambda text: print(f"\nAssistant: {text}", end="", flush=True),
        on_audio_delta=lambda audio: audio_handler.play_audio(audio),
        on_interrupt=lambda: audio_handler.stop_playback_immediately(),
        turn_detection_mode=TurnDetectionMode.SERVER_VAD,
        tools=tools
        # system_prompt=formatted_prompt  # Pass the formatted prompt to the client
    )

    # Start keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=input_handler.on_press)
    listener.start()
    
    try:
        await client.connect()
        message_handler = asyncio.create_task(client.handle_messages())
        
        print("Connected to OpenAI Realtime API!")
        print("Audio streaming will start automatically.")
        print("Press 'q' to quit")
        print("")

        # Start continuous audio streaming
        streaming_task = asyncio.create_task(audio_handler.start_streaming(client))
        first_input = True
        # Simple input loop for quit command
        while True:
            command, _ = await input_handler.command_queue.get()
            
            if command == 'q':
                break

            if first_input:
                command = f"{formatted_prompt}\n\n{command}"
                first_input = False
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        audio_handler.stop_streaming()
        audio_handler.cleanup()
        disconnect_weaviate(W_CLIENT)
        await client.close()

if __name__ == "__main__":
    print("Starting Realtime API CLI with Server VAD...")
    asyncio.run(main())
