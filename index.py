from flask import Flask, request, abort, redirect, render_template
from linebot.v3 import (
  WebhookHandler
)
from linebot.v3.exceptions import (
  InvalidSignatureError
)
from linebot.v3.messaging import (
  Configuration as LineBotConfiguration,
  ApiClient,
  MessagingApi,
  ReplyMessageRequest,
  TextMessage
)
from linebot.v3.webhooks import (
  MessageEvent,
  TextMessageContent
)
from dotenv import load_dotenv

from api.chatgpt import ChatGPT, ChatGPT35
from api.util import normalize_chatgpt_response, generate_prompt_with_sections

import os
import urllib.request

load_dotenv()

line_bot_configuration = LineBotConfiguration(os.getenv('LINE_BOT_CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('LINE_BOT_CHANNEL_SECRET'))
working_status = os.getenv('DEFALUT_TALKING', default = 'true').lower() == 'true'
chatgpt35_system_role_play = os.getenv('OPENAI_SYSTEM_ROLE_PLAY', default = 'You are a cat.')

app = Flask(__name__)
chatgpt = ChatGPT()
chatgpt35 = ChatGPT35(n=2, max_tokens=1024, system_role_play=chatgpt35_system_role_play)

# domain root
@app.route('/')
def home():
  return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def callback():
  # get X-Line-Signature header value
  signature = request.headers['X-Line-Signature']
  # get request body as text
  body = request.get_data(as_text=True)
  app.logger.info('Request body: ' + body)
  # handle webhook body
  try:
    line_handler.handle(body, signature)
  except InvalidSignatureError:
    abort(400)
  return 'OK'

@app.route('/generate/article', methods = ['GET'])
def generate_article_get():
  return {
    'content': '123',
  }

@app.route('/generate/article', methods = ['POST'])
def generate_article():
  # prompt = request.json.get('prompt')
  #  or request.form.get('prompt')
  # print(f'prompt, {prompt}, {request}')
  prompt = generate_prompt_with_sections(request.json)
  chatgpt_response = chatgpt35.generate_response(user_prompt=prompt)
  response = normalize_chatgpt_response(text=chatgpt_response)
  return {
    'content': response,

  }

@app.route('/image/<prompt>')
def generate_image(prompt: str = ''):
  image_url = chatgpt35.generate_img(prompt=prompt)
  return redirect(image_url)

@app.route("/func/create_img", methods = ['GET', 'POST'])
def generate_img():
  image_url = chatgpt35.generate_response('Could you provide the only html code about an article of visiting touhoku, japan on maple session with images on web?')
  print(image_url)
  # urllib.request.urlretrieve(image_url, "static/img/"+"dog"+".jpg")
  return image_url


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  global working_status
  
  if event.message.type != 'text':
    return
  
  with ApiClient(configuration) as api_client:
    if working_status:
      reply_msg = chatgpt35.generate_response(event.message.text)
      line_bot_api = MessagingApi(api_client)
      line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_msg)]
        )
    )

if __name__ == '__main__':
  app.run()
