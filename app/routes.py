from . import app, db
from .models import Question, Answer
from .utils import send_message_to_slack
from flask import jsonify, request
import openai

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

@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    data = request.get_json()
    question_text = data.get('text')
    if not question_text:
        return jsonify({'error': 'Brak tekstu pytania'}), 400
    try:
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

@app.route('/questions', methods=['GET'])
def questions():
    questions_list = Question.query.all()
    questions_data = [{'id': q.id, 'text': q.text, 'answers': [a.text for a in q.answers]} for q in questions_list]
    return jsonify(questions_data), 200

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    # Obsługa wyzwań URL od Slacka
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    # Obsługa zdarzeń wiadomości
    elif data.get('type') == 'event_callback':
        event = data.get('event', {})
        if event.get('type') == 'message' and not event.get('bot_id'):
            channel_id = event.get('channel')
            user_message = event.get('text')
            # Tutaj dodasz logikę generowania odpowiedzi i wysyłania jej do Slacka
            # Na przykład:
            # response_text = "Oto moja odpowiedź"
            # send_message_to_slack(channel_id, response_text)
    return jsonify({'status': 'ok'}), 200
