import os
import json
import difflib

# Configuration
DAILY_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/daily_social_science"
ANSWERS_DB = r"c:/Users/HP/Desktop/CS Project/experimental/boards/answers_db.json"
KNOWN_ANSWERS = r"c:/Users/HP/Desktop/CS Project/experimental/boards/known_answers.json"

def normalize_text(text):
    if not text: return ""
    return " ".join(text.strip().lower().split())

def load_json_map(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def populate_answers():
    db_map = load_json_map(ANSWERS_DB)
    known_map = load_json_map(KNOWN_ANSWERS)
    
    # Merge, known takes precedence
    answers_map = {**db_map, **known_map}
    
    # Create normalized map for better matching
    norm_answers_map = {normalize_text(k): v for k, v in answers_map.items()}
    
    files = [f for f in os.listdir(DAILY_DIR) if f.endswith('.json')]
    total_updated = 0
    total_questions = 0
    total_missed = 0
    
    for filename in files:
        path = os.path.join(DAILY_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = False
            for q in data.get('questions', []):
                total_questions += 1
                
                # Case 1: Answer already present (not -1) -> Skip or Verify?
                # User asked to check every question.
                # If correct is -1, we MUST find answer.
                
                if q.get('correct') == -1:
                    # Try to find via correctText
                    if q.get('correctAnswer'):
                        # Try to find this text in options
                        found_idx = -1
                        for i, opt in enumerate(q.get('options', [])):
                            if q['correctAnswer'].strip() == opt.strip(): # Exact match first
                                found_idx = i
                                break
                        if found_idx == -1: # Try lax comparison
                             for i, opt in enumerate(q.get('options', [])):
                                if q['correctAnswer'].strip().lower() in opt.strip().lower():
                                    found_idx = i
                                    break
                                    
                        if found_idx != -1:
                            q['correct'] = found_idx
                            updated = True
                            total_updated += 1
                            continue # Successfully found via text
                    
                    # Try to find via DB
                    q_text = normalize_text(q.get('question', ''))
                    if q_text in norm_answers_map:
                        q['correct'] = norm_answers_map[q_text]
                        # Also populate correctAnswer text if missing
                        if not q.get('correctAnswer') and q.get('options') and 0 <= q['correct'] < len(q['options']):
                             q['correctAnswer'] = q['options'][q['correct']]
                        updated = True
                        total_updated += 1
                    else:
                        # Try fuzzy match?
                        # For now, just mark missed
                        total_missed += 1
                        # We can try to guess from options if they are standard? No.
                        
            if updated:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Processing complete.")
    print(f"Total Questions: {total_questions}")
    print(f"Total Updated: {total_updated}")
    print(f"Total Missed (Still -1): {total_missed}")

if __name__ == "__main__":
    populate_answers()
