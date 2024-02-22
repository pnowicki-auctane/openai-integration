from flask import jsonify, request
from . import app, db
from .models import Question, Answer
from openai import OpenAI
import os
import requests
import openai

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Dodawanie pytania
@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()
    question_text = data.get('text')
    if not question_text:
        print("brak pytania - print")
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
    data = request.json
    question_text = data.get('text')
    if not question_text:
        return jsonify({'error': 'Brak tekstu pytania'}), 400

    question = Question.query.filter_by(text=question_text).first()
    if question and question.answers:
        return jsonify({'answer': question.answers[0].text}), 200

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Pytanie od użytkownika Slack."}, {"role": "user", "content": question_text}]
        )
        # Poprawione odwołanie do treści odpowiedzi
        answer_text = response.choices[0].message.content

        if not question:
            new_question = Question(text=question_text)
            db.session.add(new_question)
            db.session.flush()
            new_answer = Answer(text=answer_text, question_id=new_question.id)
            db.session.add(new_answer)
            db.session.commit()

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
    print("slackowe:", data)
    question_text = data['event']['text']

    question = Question.query.filter_by(text=question_text).first()

    # Obsługa weryfikacji URL przez Slack
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    print("slack EVENTS:", question_text)
    # Obsługa zdarzeń komunikatów
    if data.get('type') == 'event_callback' and 'bot_id' not in data['event']:
        event_message = data['event']
        message_text = event_message.get('text')
        channel_id = event_message.get('channel')
        thread_ts = event_message.get('thread_ts')  # ID wątku dla wiadomości

        # Sprawdzenie czy wiadomość kończy się znakiem zapytania i czy nie jest to wątek
        if message_text.endswith('?') and not thread_ts:
            # Sprawdzenie czy pytanie istnieje w bazie danych
            question = Question.query.filter_by(text=message_text).first()

            if question:
                # Jeśli pytanie istnieje, znajdź odpowiedź i wyślij w wątku
                answer = question.answers.first()
                if answer:
                    send_message_to_slack(channel_id, answer.text, thread_ts=event_message['ts'])
                else:
                    # Jeśli pytanie nie ma jeszcze odpowiedzi, poinformuj o tym użytkownika
                    send_message_to_slack(channel_id, "To pytanie już istnieje, ale jeszcze na nie nie odpowiedziałem.",
                                          thread_ts=event_message['ts'])
            else:
                # Jeśli pytanie nie istnieje, informuj użytkownika, że odpowiedź jest generowana
                send_message_to_slack(channel_id, "Generuję odpowiedź, proszę czekać...", thread_ts=event_message['ts'])

                # Generowanie nowej odpowiedzi przy użyciu openai
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-0613",
                        messages=[
                            {"role": "system", "content": "Pytanie od użytkownika Slack."},
                            {"role": "user", "content": question_text}
                        ]
                    )
                    answer_text = response.choices[0].message.content

                    # Zapisanie pytania i odpowiedzi do bazy danych
                    new_question = Question(text=message_text)
                    db.session.add(new_question)
                    db.session.flush()  # Uzyskanie ID pytania przed zatwierdzeniem transakcji
                    new_answer = Answer(text=answer_text, question_id=new_question.id)
                    db.session.add(new_answer)
                    db.session.commit()

                    # Wysyłanie odpowiedzi do Slacka w wątku
                    send_message_to_slack(channel_id, answer_text, thread_ts=event_message['ts'])
                except Exception as e:
                    print(f"Błąd przy generowaniu odpowiedzi: {e}")
                    send_message_to_slack(channel_id, "Wystąpił problem podczas generowania odpowiedzi.",
                                          thread_ts=event_message['ts'])

    return jsonify({'status': 'ok'}), 200


def send_message_to_slack(channel_id, message_text, thread_ts=None):
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("Błąd: Zmienna środowiskowa SLACK_BOT_TOKEN nie jest ustawiona.")
        return
    headers = {'Authorization': 'Bearer ' + token}
    payload = {
        'channel': channel_id,
        'text': message_text
    }
    # Jeśli thread_ts jest dostarczony, dodajemy go do payloadu
    if thread_ts:
        payload['thread_ts'] = thread_ts
    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)
    if not response.ok:
        print(f"Błąd wysyłania wiadomości do Slack: {response.text}")