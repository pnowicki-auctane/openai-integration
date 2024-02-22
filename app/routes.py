from flask import jsonify, request
from . import app, db
from .models import Question, Answer
import openai
import os
import requests

# Dodawanie pytania
@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()
    question_text = data.get('text')
    if not question_text:
        return jsonify({'error': 'Brak tekstu pytania'}), 400
    question = Question.query.filter_by(text=question_text).first()
    if question is not None:
        return jsonify({'error': 'Pytanie już istnieje'}), 400
    new_question = Question(text=question_text)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Pytanie dodane pomyślnie'}), 201

# Generowanie odpowiedzi
@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    data = request.get_json()
    question_text = data.get('text')
    if not question_text:
        return jsonify({'error': 'Brak tekstu pytania'}), 400
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=question_text,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5
        )
        answer_text = response.choices[0].text.strip()
        return jsonify({'answer': answer_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pobieranie pytań i odpowiedzi
@app.route('/questions', methods=['GET'])
def questions():
    questions_list = Question.query.all()
    questions_data = [{'id': q.id, 'text': q.text, 'answers': [a.text for a in q.answers]} for q in questions_list]
    return jsonify(questions_data), 200

# Obsługa zdarzeń Slack
@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    elif data.get('type') == 'event_callback' and 'bot_id' not in data['event']:
        message_text = data['event'].get('text')
        channel_id = data['event'].get('channel')
        # Tutaj możesz dodać logikę dotyczącą obsługi zdarzeń Slack
        # Na przykład, wysyłanie odpowiedzi z OpenAI lub wysyłanie zapisanej odpowiedzi z bazy danych
        send_message_to_slack(channel_id, "Twoja zaktualizowana odpowiedź z OpenAI lub bazy danych")
    return jsonify({'status': 'ok'}), 200

def send_message_to_slack(channel_id, message_text):
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("Błąd: Zmienna środowiskowa SLACK_BOT_TOKEN nie jest ustawiona.")
        return
    headers = {'Authorization': 'Bearer ' + token}
    payload = {
        'channel': channel_id,
        'text': message_text
    }
    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)
    if not response.ok:
        print(f"Błąd wysyłania wiadomości do Slack: {response.text}")
