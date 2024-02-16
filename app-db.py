# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# import os
# import requests
# import openai
#
# # Inicjalizacja aplikacji Flask
# app = Flask(__name__)
# CORS(app)
#
# # Konfiguracja bazy danych SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://slackgptadmin:gpt@localhost/slackgpt'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
#
# # Definicje modeli bazy danych
# class Question(db.Model):
#     __tablename__ = 'question'
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String, unique=True, nullable=False)
#     answers = db.relationship('Answer', backref='question', lazy=True)
#
# class Answer(db.Model):
#     __tablename__ = 'answer'
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String, nullable=False)
#     question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
#
# # Inicjalizacja klienta OpenAI
# openai.api_key = os.getenv('OPENAI_API_KEY')
#
# @app.route('/add_question', methods=['POST'])
# def add_question():
#     data = request.get_json()
#     question_text = data.get('text')
#     if not question_text:
#         return jsonify({'error': 'Brak tekstu pytania'}), 400
#     question = Question.query.filter_by(text=question_text).first()
#     if question is not None:
#         return jsonify({'error': 'Pytanie już istnieje'}), 400
#     new_question = Question(text=question_text)
#     db.session.add(new_question)
#     db.session.commit()
#     return jsonify({'message': 'Pytanie dodane pomyślnie'}), 201
#
# @app.route('/generate_answer', methods=['POST'])
# def generate_answer():
#     data = request.get_json()
#     question_text = data.get('text')
#     if not question_text:
#         return jsonify({'error': 'Brak tekstu pytania'}), 400
#     try:
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=question_text,
#             max_tokens=150,
#             n=1,
#             stop=None,
#             temperature=0.5
#         )
#         answer_text = response.choices[0].text.strip()
#         return jsonify({'answer': answer_text}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# @app.route('/questions', methods=['GET'])
# def questions():
#     questions_list = Question.query.all()
#     questions_data = [{'id': q.id, 'text': q.text, 'answers': [a.text for a in q.answers]} for q in questions_list]
#     return jsonify(questions_data), 200
#
# @app.route('/slack/events', methods=['POST'])
# def slack_events():
#     data = request.json
#     # Obsługa wyzwań URL od Slacka
#     if data.get('type') == 'url_verification':
#         return jsonify({'challenge': data.get('challenge')})
#     # Obsługa zdarzeń wiadomości
#     elif data.get('type') == 'event_callback':
#         event = data.get('event', {})
#         if event.get('type') == 'message' and not event.get('bot_id'):
#             channel_id = event.get('channel')
#             user_message = event.get('text')
#             # Tutaj dodasz logikę generowania odpowiedzi i wysyłania jej do Slacka
#             # Na przykład:
#             # response_text = "Oto moja odpowiedź"
#             # send_message_to_slack(channel_id, response_text)
#     return jsonify({'status': 'ok'}), 200
#
# def send_message_to_slack(channel_id, message_text):
#     headers = {'Authorization': 'Bearer ' + os.getenv('SLACK_BOT_TOKEN')}
#     payload = {
#         'channel': channel_id,
#         'text': message_text
#     }
#     response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)
#     if not response.ok:
#         print(f"Błąd wysyłania wiadomości do Slack: {response.text}")
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, port=5001)
