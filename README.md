# modalCloudChatBotBackend
Various chatbots of increasing complexity testing the capabilities of the poe api.

# Poe Chatbot Backend Deployment

This project demonstrates the deployment of a chatbot backend to the cloud, specifically to Modal cloud, showcasing the ability to serve as a backend for various chatbot functionalities. The project includes several bots, each with unique capabilities, and provides instructions on how to switch between them.

## Features

- **Multiple Bots**: The project includes a variety of bots, each serving different purposes. You can switch between these bots by instancing a different bot on line 140.
- **API Key Management**: The API key is managed using Modal's secrets functionality, ensuring that the key is hidden and secure.
- **Attachment Expanding Functionality**: The project includes functionality for expanding attachments, which requires an API key. However, this functionality can be turned off if needed, allowing the bots to run without an API key.

## Requirements

To run this project, you will need the following libraries:

- `fastapi-poe`
- `nltk`
- `modal`

These libraries can be installed using pip:

```bash
pip install fastapi-poe nltk modal
```

## Running the Project

1. **Clone the Repository**: Clone this repository to your local machine.

2. **Install Dependencies**: Navigate to the project directory and install the required libraries using the command provided above.

3. **API Key**: If you wish to use the attachment expanding functionality, you will need an API key. If you do not have one, you can turn off the line `app = fp.make_app(bot, access_key=POE_ACCESS_KEY)` and turn on the line `app = fp.make_app(bot, allow_without_key=True)` to run without an API key. Note that all bots except the last one will work fine in this case.

4. **Run the Application**: Execute the `fastapi_app` function to start the application.

## Switching Between Bots

To switch between the bots, you can modify the bot instance on line 140. For example, to switch to the `GPT35TurboBot`, you would change the line to:

```python
bot = GPT35TurboBot()
```
