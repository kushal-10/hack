# Bargain Master GPT

This repository contains a voice-based conversational agent that lets you bargain about products. It can pick the right product based on user preferences from a predefined list of products in a vector database. You can then bargain with the agent about the selected products.

WARNING: Currently only works with headphones because of the unresolved playback microphone issue!
## Prerequisites

Make sure you have the following dependencies installed:

- `weaviate-client==4.10.4`
- `pynput`
- `openai_realtime_client`
- `llama_index`
- `vonage==4.4.0`
- `fastapi[standard]`

You can install these dependencies int the requirements.txt

## How to start

Execute the conversation.py script from your console

## Based on
The following repo served as a starting point:
https://github.com/run-llama/openai_realtime_client

## Contributing

We welcome contributions to this repository. If you have an example you'd like to add or improvements to existing examples, please feel free to submit a pull request.
