import os
import json
import hashlib

# Configuration
SOURCE_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/sample_data/social_science"
STATE_FILE = r"c:/Users/HP/Desktop/CS Project/experimental/boards/analysis_state_social.json"
BATCH_SIZE = 5

def normalize_text(text):
    if not text: return ""
    return " ".join(text.strip().lower().split())

def get_year_from_filename(filename):
    try:
        parts = filename.replace('.json', '').split('_')
        if parts[-1].isdigit():
            return int(parts[-1])
    except:
        pass
    return 2025

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_files": [], "questions": {}}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def analyze_batch():
    state = load_state()
    processed_files = set(state["processed_files"])
    
    all_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')])
    pending_files = [f for f in all_files if f not in processed_files]
    
    if not pending_files:
        print("All files have been processed!")
        return
    
    batch_files = pending_files[:BATCH_SIZE]
    print(f"Processing batch of {len(batch_files)} files: {', '.join(batch_files)}")
    
    for filename in batch_files:
        path = os.path.join(SOURCE_DIR, filename)
        year = get_year_from_filename(filename)
        
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            questions = []
            if isinstance(data, list):
                questions = data
            elif isinstance(data, dict):
                if 'questions' in data:
                    questions = data['questions']
                elif 'subjects' in data and 'social_science' in data['subjects']:
                    questions = data['subjects']['social_science'].get('questions', [])
            
            for q in questions:
                q_text = q.get('question', '')
                norm_q = normalize_text(q_text)
                if not norm_q: continue
                
                # Use normalized text as key
                key = norm_q
                
                if key not in state["questions"]:
                    state["questions"][key] = {
                        "count": 0,
                        "years": [],
                        "data": q # Store sample data
                    }
                    # Ensure sample data has a year if missing
                    if 'year' not in state["questions"][key]["data"]:
                        state["questions"][key]["data"]["year"] = year

                state["questions"][key]["count"] += 1
                if year not in state["questions"][key]["years"]:
                    state["questions"][key]["years"].append(year)
                    state["questions"][key]["years"].sort()
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
        state["processed_files"].append(filename)
        
    save_state(state)
    
    print("-" * 40)
    print(f"Files processed so far: {len(state['processed_files'])} / {len(all_files)}")
    print(f"Total unique questions identified: {len(state['questions'])}")
    print("Run the script again to process the next batch.")

if __name__ == "__main__":
    analyze_batch()
