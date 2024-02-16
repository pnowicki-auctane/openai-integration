import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://slackgptadmin:gpt@localhost/slackgpt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
