from bs4 import BeautifulSoup

def generate_paragraph_prompt(parameter) -> str:
  index, summary = parameter
  summary_prompt = f'and summary is {summary}' if len(summary) > 0 else ''
  prompt = f'''Paragraph {index + 1} is talking about "{summary}".''' if len(summary) > 0 else ''
  return prompt

def generate_section_prompt(parameter) -> str:
  index, section = parameter
  topic = section['topic']
  paragraphs = section['summaries'] or []
  topic_prompt = f'''Section {index + 1} is talking about "{topic}". include {len(paragraphs)} paragraphs.''' if len(topic) > 0 else f'''Section {index} include {len(paragraphs)} paragraphs.'''
  paragraphs_prompt = list(map(generate_paragraph_prompt, enumerate(paragraphs)))
  prompt = f'''{topic_prompt} {' '.join(paragraphs_prompt)}'''
  return prompt

def generate_prompt_with_sections(request: dict) -> str:
  title = request['title']
  sections = request['sections'] or []

  prefix = f'''Write an article about the following topic: "{title}". include {len(sections)} sections.\
  I'll give you topic and summary for each section, use these topics and summaries to write the article.\
  below is the topic and summary for each section:\
  '''
  postfix = f'''Write the article with html format, inside a "body" tag, and append a empty paragraph tag in every end of paragraph. just give me the article what you write, any note out of the article is unnecessary.'''
  sections_prompt = list(map(generate_section_prompt, enumerate(sections)))
  return f'''{prefix} {' '.join(sections_prompt)} {postfix}'''

def normalize_chatgpt_response(text: str = '') -> str:
  print(text)
  soup = BeautifulSoup(text, 'html.parser')
  if soup is None:
    return f'<p>{text}</p>'
  soup_html_tag = soup.find('body')
  if soup_html_tag is not None:
    return str(soup_html_tag)
  return str(soup)

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
  print(generate_prompt_with_sections(req))