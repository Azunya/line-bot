import sys
import os
import openai
from dotenv import load_dotenv
from .util import generate_prompt_with_sections

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatGPT35:
  def __init__(self, 
    model: str = 'gpt-3.5-turbo',
    temperature: float = .6,
    frequency_penalty: float = 0,
    presence_penalty: float = .6,
    max_tokens: int = 1024,
    n: int = 1,
    system_role_play: str = 'You are cat',
  ):
    self.model = model
    self.temperature = temperature
    self.frequency_penalty = frequency_penalty
    self.presence_penalty = presence_penalty
    self.max_tokens = max_tokens
    self.n = n
    self.system_role_play = system_role_play

  def generate_response(self, user_prompt: str = '') -> str:
    response = openai.ChatCompletion.create(
      model=self.model,
      messages=[
        {
          'role': 'system',
          'content': self.system_role_play,
        },
        {
          'role': 'user',
          'content': user_prompt,
        },
      ],
      temperature=self.temperature,
      # frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
      frequency_penalty=self.frequency_penalty,
      # presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
      presence_penalty=self.presence_penalty,
      max_tokens=self.max_tokens,
      n=self.n,
    )
    return response.choices[0].message.content or ''

  def generate_chapters(book_title):
    prompt = [{"role": "system", "content":  f"generate a list of chapters and subchapters for a book titled {book_title} in json format. do not include any explanation or code formatting. format it in this way: "+"{\"chapter_name\":[\"subchapter_names\"],}"+". please include between 5 and 10 subchapters per chapter. use this format exactly."},{"role": "user", "content":  "generate with 4 space indents"},]
    response = openai.ChatCompletion.create(
      model=self.model,
      messages=prompt
    )
    
    gpt_response = response['choices'][0]['message']['content']
    
    return gpt_response


  def generate_img(self, prompt: str = '', size: str = '256x256') -> str:
    response = openai.Image.create(
      prompt=prompt,
      n=1,
      size=size
    )
    return response['data'][0]['url']

class ChatGPT:
    def __init__(self):
        from api.prompt import Prompt
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default = "text-davinci-003")
        #self.model = os.getenv("OPENAI_MODEL", default = "chatbot")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0.6))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 240))

    def generate_response(self):
        response = openai.Completion.create(
            model=self.model,
            prompt=self.prompt.generate_prompt(),
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            max_tokens=self.max_tokens
        )
        return response['choices'][0]['text'].strip()

    def add_msg(self, text):
        self.prompt.add_msg(text)

if __name__ == '__main__':
  req = {
    'title': 'Traveling',
    'sections': [
      {
        'topic': 'Sakura season',
        'summaries': [
          'Tohoku, Japan',
          'Kyoto, Japan',
        ]
      },
      {
        'topic': 'Maple season',
        'summaries': [
          'Tohoku, Japan',
          'HoKaito, Japan',
        ]
      },
    ],
  }
  gpt = ChatGPT35()
  print(gpt.generate_response(generate_prompt_with_sections(req)))

  # if (len(sys.argv) > 0):
  #     user_prompt = sys.argv[1] or 'Hi'
  #     gpt = ChatGPT35()
  #     print(gpt.generate_response(user_prompt))