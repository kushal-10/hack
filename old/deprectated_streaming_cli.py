import asyncio
import os
import base64

from pynput import keyboard
from openai_realtime_client import RealtimeClient, AudioHandler, InputHandler, TurnDetectionMode
from llama_index.core.tools import FunctionTool
from prompt import SYSTEM_PROMPT
from database.vector_search_callable import connect_to_weaviate, search_products, disconnect_weaviate

W_CLIENT = ""
conversation = []  # List to store the conversation
terminate = False

# Format the SYSTEM_PROMPT with the variables
formatted_prompt = SYSTEM_PROMPT.format(
    PRODUCT_CATEGORY="smartphones",
    MIN_PRICE="-10%"
)

# Add your own tools here! This is an example of a tool that returns a phone number based on the name
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

# NOTE: Terminate conversation when the user expresses the desire to end it
def terminate_call():
    """Terminate conversation."""
    global terminate
    print("Terminating conversation...")  # Debugging
    terminate = True

tools = [
    FunctionTool.from_defaults(fn=get_phone_number),
    FunctionTool.from_defaults(fn=get_products),
    FunctionTool.from_defaults(fn=terminate_call)
]

async def main():
    global W_CLIENT, conversation, terminate
    audio_handler = AudioHandler()
    input_handler = InputHandler()
    input_handler.loop = asyncio.get_running_loop()
    W_CLIENT = connect_to_weaviate()
    client = RealtimeClient(
        api_key=os.environ.get("OPENAI_API_KEY"),
        on_text_delta=lambda text: (print(f"\nAssistant: {text}", end="", flush=True), conversation.append(f"Assistant: {text}")),
        on_audio_delta=lambda audio: audio_handler.play_audio(audio),
        on_interrupt=lambda: audio_handler.stop_playback_immediately(),
        turn_detection_mode=TurnDetectionMode.SERVER_VAD,
        tools=tools
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
        await client.send_text(formatted_prompt)
        conversation.append(f"User: {formatted_prompt}")
        
        # Start continuous audio streaming
        streaming_task = asyncio.create_task(audio_handler.start_streaming(client))
        
        # Simple input loop for quit command
        while True:
            command, _ = await input_handler.command_queue.get()
            
            if command == 'q' or terminate:
                print("Exiting conversation loop...")  # Debugging
                break
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up resources...")  # Debugging
        audio_handler.stop_streaming()
        audio_handler.cleanup()
        disconnect_weaviate(W_CLIENT)
        await client.close()
        with open("conversation_history.txt", "w", encoding="utf-8") as file:
            for line in conversation:
                file.write(line + "\n")
        print("Conversation history exported to conversation_history.txt")

if __name__ == "__main__":
    print("Starting Realtime API CLI with Server VAD...")
    asyncio.run(main())