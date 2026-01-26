import json
import os
import glob
from collections import defaultdict

# Configuration
DATA_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/sample_data/science"
STATE_FILE = r"c:/Users/HP/Desktop/CS Project/experimental/boards/analysis_state.json"
BATCH_SIZE = 5

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_files": [], "questions": {}}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

def normalize_question(text):
    if not text:
        return ""
    return " ".join(text.strip().split())

def process_files():
    state = load_state()
    processed_files = set(state["processed_files"])
    
    # Get all json files
    all_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    all_files.sort()
    
    # Identify pending files
    pending_files = [f for f in all_files if os.path.basename(f) not in processed_files]
    
    if not pending_files:
        print("All files have been processed.")
        return

    # Select batch
    batch = pending_files[:BATCH_SIZE]
    print(f"Processing batch of {len(batch)} files:")
    
    for file_path in batch:
        filename = os.path.basename(file_path)
        print(f" - {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # Content might be a list or a dict with a 'questions' key, or nested in subjects
                questions = []
                if isinstance(content, list):
                    questions = content
                elif isinstance(content, dict):
                    if 'questions' in content:
                        questions = content['questions']
                    elif 'subjects' in content and 'science' in content['subjects']:
                        questions = content['subjects']['science'].get('questions', [])

                
                # Extract year from filename (e.g. questions_a_2016.json -> 2016)
                file_year = 0
                try:
                    # Assuming format questions_x_YYYY.json
                    parts = filename.replace('.json', '').split('_')
                    if len(parts) >= 3 and parts[-1].isdigit():
                        file_year = int(parts[-1])
                except:
                    pass

                for q in questions:
                    q_text = q.get('question', '')
                    norm_q = normalize_question(q_text)
                    
                    if not norm_q:
                        continue
                        
                    if norm_q not in state["questions"]:
                        state["questions"][norm_q] = {
                            "count": 0,
                            "years": [],
                            "data": q
                        }
                    
                    state["questions"][norm_q]["count"] += 1
                    
                    # Determine year: explicit in q > filename year
                    year = q.get('year', file_year)
                    if year != 0:
                        # Ensure we update the stored data 'year' if it was missing so it shows up in final output
                        if 'year' not in state["questions"][norm_q]["data"]:
                             state["questions"][norm_q]["data"]['year'] = year

                        if year not in state["questions"][norm_q]["years"]:
                            state["questions"][norm_q]["years"].append(year)

                            
        except Exception as e:
            print(f"   Error processing {filename}: {e}")
            continue

        state["processed_files"].append(filename)

    save_state(state)
    print(f"\nBatch complete. Total questions tracked: {len(state['questions'])}")
    print(f"Remaining files: {len(pending_files) - len(batch)}")

if __name__ == "__main__":
    process_files()
