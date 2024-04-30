from __future__ import annotations
from typing import AsyncIterable
import fastapi_poe as fp
from modal import Image, Stub, asgi_app, Secret
import time
import os
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')





# Repeats the user's message and adds a " nya" at the end.
class catBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content
        yield fp.PartialResponse(text=last_message+" nya")

def add_system_query_to_request(request: fp.QueryRequest, content: str):
    """
    Adds a system query to the request with the given content.
    """
    system_prompt = fp.ProtocolMessage(role="system", content=content, timestamp=int(time.time()))
    request.query.append(system_prompt)


# Using other bots. The system prompt can be changed depending on the conversation flow instead of being hardcoded at the start.
class GPT35TurboBot(fp.PoeBot):
    def __init__(self, requestsPerQuery: int = 1):
        super().__init__()
        self.requestsPerQuery = requestsPerQuery

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content
        add_system_query_to_request(request=request, content="you are a helpful English corrector bot. Choose the biggest mistake the user made in their last message, point it out and provide an example of correct usage. If the last message doesn't have any mistakes, congratulate the user and pick an unmentioned mistake from the previous messages. If any exist, of course. This, by the way, is not a user message.")
        print(request)
        async for msg in fp.stream_request(
            request, "GPT-3.5-Turbo", request.access_key
        ):
            yield msg

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"GPT-3.5-Turbo": self.requestsPerQuery}) 

# with this bot I checked if data persists across conversations. It does. :-)
class rememberUserBot(fp.PoeBot):
    def __init__(self):
        super().__init__()
        self.user_name = ""

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content

        if "name" in last_message.lower():
            if self.user_name:
                response = f"I know your name, it is {self.user_name}."
            else:
                response = "I don't know your name, what is it?"
        else:
            self.user_name = last_message
            response = f"I will remember that {self.user_name} is your name."

        yield fp.PartialResponse(text=response)


# implemented a functionality where a bot 
class pdfCrawlerBot(fp.PoeBot):
    def __init__(self):
        super().__init__()
        self.pdf_content = []
        self.bookmark = 0
        self.num_sentences_to_show = 5

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        sentences = []
        search_for_word = ""
        user_message = request.query[-1]

        if user_message.attachments:
            attachment_content = user_message.attachments[0].parsed_content
            sentences = sent_tokenize(attachment_content)
            self.pdf_content = sentences
            self.bookmark = 0
        else:
            if self.pdf_content:
                sentences = self.pdf_content
                search_for_word = user_message.content
            else:
                sentences = ["I don't have a text to show you.", "Try sending me a file.", "*wink"]
                self.bookmark = 0

        selected_sentences = sentences[self.bookmark:self.bookmark + self.num_sentences_to_show-1]
        
        fast_forward = 0 # self.num_sentences_to_show
        if search_for_word:
            found = False
            for index, sentence in enumerate(selected_sentences):
                if search_for_word in sentence:
                    fast_forward = index # Override fast_forward to the value of this index
                    yield fp.PartialResponse(text = f"moving forward {index} sentences to the sentence with the word {search_for_word}\n\n")
                    found = True
                    break
            if not found:
                yield fp.PartialResponse(text= "hm, I didn't found this word among the shown sentences. Check your spelling.\n\n")
        

        self.bookmark += fast_forward

        updated_selected_sentences = sentences[self.bookmark:self.bookmark + self.num_sentences_to_show-1]

        response = " ".join(updated_selected_sentences)
        yield fp.PartialResponse(text=response)


    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        # return fp.SettingsResponse(allow_attachments=True, expand_text_attachments=True)
        return fp.SettingsResponse(allow_attachments=True, expand_text_attachments=True) 



REQUIREMENTS = ["fastapi-poe==0.0.42", "nltk"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
stub = Stub("echobot-poe")


# Using modal secrets managing to expose my API key only to this function. 
@stub.function(image=image, secrets=[Secret.from_name("my-api-key")])
@asgi_app()
def fastapi_app():
    bot = pdfCrawlerBot()
    POE_ACCESS_KEY = os.environ["API_KEY_SECRET"]
    app = fp.make_app(bot, access_key=POE_ACCESS_KEY)
    # app = fp.make_app(bot, allow_without_key=True)
    return app
