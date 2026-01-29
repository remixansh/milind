"""
BSEB Super 50 Quiz Platform
A minimalist Flask application for daily practice questions
"""

from flask import Flask, render_template, jsonify, request, session
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'bseb-super50-secret-key-2026'

# ==================== Helper Functions ====================

def get_ist_now():
    """Get current time in Indian Standard Time (UTC+5:30)"""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def get_data_dir(subject_id):
    """Get the directory path for a subject's data"""
    base_dir = os.path.dirname(__file__)
    if subject_id == 'science':
        return os.path.join(base_dir, 'daily_science')
    if subject_id == 'social_science':
        return os.path.join(base_dir, 'daily_social_science')
    if subject_id == 'hindi':
        return os.path.join(base_dir, 'daily_hindi')
    if subject_id == 'math':
        return os.path.join(base_dir, 'daily_math')
    if subject_id == 'sanskrit':
        return os.path.join(base_dir, 'daily_sanskrit')
    return os.path.join(base_dir, 'data', subject_id)

def load_daily_questions(subject_id, date_code):
    """Load daily questions from storage"""
    data_dir = get_data_dir(subject_id)
    file_path = os.path.join(data_dir, f'{date_code}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_available_dates(subject_id):
    """Get list of available daily question dates for a subject"""
    data_dir = get_data_dir(subject_id)
    dates = []
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                date_code = filename.replace('.json', '')
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        dates.append({
                            'code': date_code,
                            'display': data.get('dateDisplay', date_code),
                            'questionCount': len(data.get('questions', []))
                        })
                except:
                    pass
    
    # Sort by (month, day) for proper chronological order
    # Date code format from daily_science is MMDD, so we sort by MM (first 2) then DD (last 2)
    dates.sort(key=lambda x: (int(x['code'][:2]), int(x['code'][2:])))
    return dates

def get_subjects():
    """Get available subjects"""
    subjects = [
        {
            'id': 'science',
            'name': 'Science',
            'nameHindi': 'विज्ञान',
            'icon': 'flask',
            'color': 'emerald',
            'coming_soon': False
        },
        {
            'id': 'social_science',
            'name': 'Social Science',
            'nameHindi': 'सामाजिक विज्ञान',
            'icon': 'users',
            'color': 'blue',
            'coming_soon': False
        },
        {
            'id': 'hindi',
            'name': 'Hindi',
            'nameHindi': 'हिन्दी',
            'icon': 'book-open',
            'color': 'rose',
            'coming_soon': False
        },
        {
            'id': 'math',
            'name': 'Mathematics',
            'nameHindi': 'गणित',
            'icon': 'arithmetic',
            'color': 'indigo',
            'coming_soon': False
        },
        {
            'id': 'english',
            'name': 'English',
            'nameHindi': 'अंग्रेजी',
            'icon': 'abc',
            'color': 'sky',
            'coming_soon': True
        },
        {
            'id': 'sanskrit',
            'name': 'Sanskrit',
            'nameHindi': 'संस्कृत',
            'icon': 'om',
            'color': 'amber',
            'coming_soon': False
        }
    ]
    # Ensure sorted by availability (Available first)
    return sorted(subjects, key=lambda x: x['coming_soon'])

# ==================== Page Routes ====================

@app.route('/')
def dashboard():
    """Main dashboard with subjects"""
    subjects = get_subjects()
    progress = session.get('progress', {})
    return render_template('dashboard.html', subjects=subjects, progress=progress)

@app.route('/practice/<subject_id>')
def date_select(subject_id):
    """Date selection page for daily questions"""
    dates = get_available_dates(subject_id)
    subject = next((s for s in get_subjects() if s['id'] == subject_id), None)
    
    if not subject:
        return render_template('404.html'), 404
    
    # Get today's date for comparison (IST)
    today = get_ist_now()
    today_month = today.month
    today_day = today.day
    
    return render_template('date_select.html', 
                         subject=subject, 
                         dates=dates,
                         today_month=today_month,
                         today_day=today_day)

@app.route('/daily/<subject_id>/<date_code>')
def daily_questions(subject_id, date_code):
    """Display daily questions with answers"""
    # Load subject first
    subject = next((s for s in get_subjects() if s['id'] == subject_id), None)
    
    if not subject:
        return render_template('404.html'), 404

    # Load data to get testTime
    data = load_daily_questions(subject_id, date_code)
    
    if not data:
        return render_template('404.html'), 404

    # Date/Time restriction
    try:
        month = int(date_code[:2])
        day = int(date_code[2:])
        # Unlock Daily Questions at 00:00 (Midnight)
        target_dt = datetime(2026, month, day)
        
        # Use IST for comparison
        if get_ist_now() < target_dt:
             return render_template('locked.html', 
                                  subject=subject,
                                  date_display=data.get('dateDisplay', f"{day}/{month}/2026"),
                                  unlock_time="00:00",
                                  is_quiz=False)
    except ValueError:
        return render_template('404.html'), 404
    
    return render_template('daily_questions.html',
                         subject=subject,
                         date_code=date_code,
                         date_display=data.get('dateDisplay', ''),
                         questions=data.get('questions', []))

@app.route('/quiz/<subject_id>/<date_code>')
def quiz(subject_id, date_code):
    """Quiz mode - one question at a time"""
    subject = next((s for s in get_subjects() if s['id'] == subject_id), None)
    data = load_daily_questions(subject_id, date_code)
    
    if not data or not subject:
        return render_template('404.html'), 404
        
    # Time restriction: Available from testTime of the date
    try:
        month = int(date_code[:2])
        day = int(date_code[2:])
        test_time = data.get('testTime', '19:00')
        hour, minute = map(int, test_time.split(':'))
        
        target_dt = datetime(2026, month, day, hour, minute)
        
        # Use IST for comparison
        if get_ist_now() < target_dt:
             return render_template('locked.html', 
                                  subject=subject,
                                  date_display=data.get('dateDisplay', ''),
                                  unlock_time=test_time,
                                  is_quiz=True)
    except ValueError:
        pass # Fallthrough if parsing fails
    
    return render_template('quiz.html',
                         subject=subject,
                         date_code=date_code,
                         date_display=data.get('dateDisplay', ''),
                         questions=data.get('questions', []))

@app.route('/results/<subject_id>/<date_code>')
def results(subject_id, date_code):
    """Results page after quiz"""
    return render_template('results.html', subject_id=subject_id, date_code=date_code)

# ==================== API Routes ====================

@app.route('/api/daily/<subject_id>/<date_code>')
def api_daily_questions(subject_id, date_code):
    """API endpoint to fetch daily questions"""
    data = load_daily_questions(subject_id, date_code)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz and calculate score"""
    data = request.json
    answers = data.get('answers', {})
    subject_id = data.get('subject_id')
    date_code = data.get('date_code')
    
    questions_data = load_daily_questions(subject_id, date_code)
    if not questions_data:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = questions_data.get('questions', [])
    correct = 0
    total = len(questions)
    
    results = []
    for q in questions:
        q_id = str(q['id'])
        user_answer = answers.get(q_id)
        is_correct = user_answer == q['correct']
        if is_correct:
            correct += 1
        results.append({
            'id': q['id'],
            'userAnswer': user_answer,
            'correctAnswer': q['correct'],
            'isCorrect': is_correct
        })
    
    score = round((correct / total) * 100) if total > 0 else 0
    
    # Save progress
    progress = session.get('progress', {})
    if subject_id not in progress:
        progress[subject_id] = {'attempts': 0, 'best_score': 0}
    progress[subject_id]['attempts'] += 1
    progress[subject_id]['best_score'] = max(progress[subject_id]['best_score'], score)
    session['progress'] = progress
    
    return jsonify({
        'score': score,
        'correct': correct,
        'total': total,
        'results': results
    })

@app.route('/api/progress')
def get_progress():
    """Get user progress"""
    return jsonify(session.get('progress', {}))

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
