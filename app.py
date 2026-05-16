# Typing Master by python flask

import os
import random
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'typing-master-ultra-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///typing_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class UserResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wpm = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    errors = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_practice = db.Column(db.Date, nullable=False)
    current_streak = db.Column(db.Integer, default=1)

# --- Dictionaries ---
TEXT_DATA = {
    "easy": [
        "The quick brown fox jumps over the lazy dog.",
        "Practice makes perfect when it comes to typing speed.",
        "Simple words are easier to type fast without making errors.",
        "Light travels faster than sound which is why some people appear bright.",
        "Every day is a new opportunity to improve your skills.And remember, consistency is key!",
        "If you depends on others, you will always be their prisoner.",
        "The only way to do great work is to love what you do.",
        "Don't watch the clock; do what it does. Keep going.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "We should not give up and we should not allow the problem to defeat us."        
    ],
    "medium": [
        "Success is not final, failure is not fatal: it is 'the courage, to continue' that counts.",
        "Technology is best ,when it 'brings people together' and solves real world problems.",
        "Consistency is the key to 'mastering any complex skill' in the modern digital age.",
        "In the middle ,of every difficulty, lies ,opportunity for those who seek it.",
        "The beautiful thing 'about learning' is that no one can take it away from you.",
        "The only` limit to our, realization of 'tomorrow will be' our doubts of today.",
        "Every great dream ,begins with a dreamer. Always remember, you have within you the strength,",
        "the patience, and the passion to 'reach for the stars to' change the world.",
        "The world is 'full of magical thing's patiently waiting for our wits to grow sharper.",
        "The only way to do ,great work is to love what you do. If you ,haven't found it yet, keep looking."
    ],
    "hard": [
        "The phenomenon of linguistic 'evolution demonstrates456' how #communication adapts to cultural shifts.",
        "Quantum computing utilizes the principles of @superposition and'789entanglement' to process data.",
        "Philosophical !inquiries '629into the nature of consciousness' often yield paradoxical conclusions.",
        "The 'infrastructure' of 567contemporary metropolitan areas &requires 654meticulous architectural planning.",
        "Synchronous execution of 'asynchronous functions' can ^lead610 to significant performance bottlenecks.",
        "The intricacies of human 'cognition are still 231not' fully understood %by neuroscientists.",
        "Cryptographic algorithms are 491essential *for securing 'digital communication' in the modern era.",
        "The ethical implications of $artificial intelligence are a '098subject of intense' debate among experts.",
        "The study of astrophysics (reveals the '063fundamental) forces' that govern the universe.",
        "The convergence of biotechnology and 'information technology826' is ()revolutionizing healthcare.",
        "The impact of climate change on 'global296 ecosystems' is a pressing[] concern for scientists."
    ]
}

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-text')
def get_text():
    difficulty = request.args.get('difficulty', 'medium')
    text = random.choice(TEXT_DATA.get(difficulty, TEXT_DATA['medium']))
    return jsonify({"text": text})

@app.route('/api/submit-result', methods=['POST'])
def submit_result():
    data = request.json
    new_result = UserResult(
        wpm=data['wpm'],
        accuracy=data['accuracy'],
        errors=data['errors'],
        difficulty=data['difficulty']
    )
    db.session.add(new_result)
    
    # Simple Streak Logic
    today = datetime.utcnow().date()
    streak = UserStreak.query.first()
    if not streak:
        streak = UserStreak(last_practice=today, current_streak=1)
        db.session.add(streak)
    else:
        if streak.last_practice == today - timedelta(days=1):
            streak.current_streak += 1
            streak.last_practice = today
        elif streak.last_practice < today - timedelta(days=1):
            streak.current_streak = 1
            streak.last_practice = today
            
    db.session.commit()
    return jsonify({
        "status": "success", 
        "streak": streak.current_streak,
        "best_wpm": db.session.query(db.func.max(UserResult.wpm)).scalar()
    })

@app.route('/api/leaderboard')
def leaderboard():
    results = UserResult.query.order_by(UserResult.wpm.desc()).limit(10).all()
    output = []
    for r in results:
        output.append({
            "wpm": r.wpm,
            "accuracy": r.accuracy,
            "difficulty": r.difficulty,
            "date": r.timestamp.strftime("%Y-%m-%d")
        })
    return jsonify(output)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)