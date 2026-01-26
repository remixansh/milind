import json
import os
import glob

DAILY_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/daily_science"
ANSWERS_DB = r"c:/Users/HP/Desktop/CS Project/experimental/boards/answers_db.json"

def load_answers():
    if os.path.exists(ANSWERS_DB):
        with open(ANSWERS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_answers(answers):
    with open(ANSWERS_DB, 'w', encoding='utf-8') as f:
        json.dump(answers, f, indent=4, ensure_ascii=False)

def get_all_questions():
    files = glob.glob(os.path.join(DAILY_DIR, "*.json"))
    questions = {} # text -> q_obj
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for q in data.get('questions', []):
                q_text = q.get('question', '').strip()
                if q_text and q_text not in questions:
                    questions[q_text] = q
    return questions

def status():
    all_qs = get_all_questions()
    answered = load_answers()
    
    unique_count = len(all_qs)
    answered_count = 0
    for q_text in all_qs:
        if q_text in answered:
            answered_count += 1
            
    print(f"Total unique questions: {unique_count}")
    print(f"Answered: {answered_count}")
    print(f"Remaining: {unique_count - answered_count}")

def export_next_batch(batch_size=20):
    all_qs = get_all_questions()
    answered = load_answers()
    
    batch = []
    for q_text, q_obj in all_qs.items():
        if q_text not in answered:
            batch.append(q_obj)
            if len(batch) >= batch_size:
                break
    
    print(json.dumps(batch, indent=4, ensure_ascii=False))

def export_to_file(batch_size=20, filename="batch.json"):
    all_qs = get_all_questions()
    answered = load_answers()
    
    batch = []
    for q_text, q_obj in all_qs.items():
        if q_text not in answered:
            batch.append(q_obj)
            if len(batch) >= batch_size:
                break
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=4, ensure_ascii=False)
    print(f"Exported {len(batch)} questions to {filename}")

def apply_answers():
    answers = load_answers()
    files = glob.glob(os.path.join(DAILY_DIR, "*.json"))
    count_updated = 0
    
    for fpath in files:
        updated = False
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for q in data.get('questions', []):
            q_text = q.get('question', '').strip()
            if q_text in answers:
                correct_idx = answers[q_text]
                if q.get('correct') != correct_idx:
                    q['correct'] = correct_idx
                    # Also update correctAnswer text
                    if 0 <= correct_idx < len(q['options']):
                         q['correctAnswer'] = q['options'][correct_idx]
                    updated = True
        
        if updated:
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            count_updated += 1
            
    print(f"Updated {count_updated} files.")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        status()
    elif cmd == "export":
        export_next_batch()
    elif cmd == "export_file":
        size = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        export_to_file(batch_size=size)
    elif cmd == "apply":
        apply_answers()
