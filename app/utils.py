import requests
import os

def send_message_to_slack(channel_id, message_text):
    headers = {'Authorization': 'Bearer ' + os.getenv('SLACK_BOT_TOKEN')}
    payload = {
        'channel': channel_id,
        'text': message_text
    }
    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)
    if not response.ok:
        print(f"Błąd wysyłania wiadomości do Slack: {response.text}")
