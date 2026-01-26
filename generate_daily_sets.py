import json
import os
import datetime
from datetime import timedelta

# Configuration
STATE_FILE = r"c:/Users/HP/Desktop/CS Project/experimental/boards/analysis_state.json"
OUTPUT_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/daily_science"
START_DATE = datetime.date(2026, 1, 25)
END_DATE = datetime.date(2026, 2, 15) # Inclusive? 22 days: Jan 25 to Feb 15 is 22 days.
QUESTIONS_PER_DAY = 50

def load_state():
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def get_date_range():
    curr = START_DATE
    while curr <= END_DATE:
        yield curr
        curr += timedelta(days=1)

def generate_sets():
    state = load_state()
    questions_map = state.get("questions", {})
    
    # Convert map to list of tuples (question_text, data)
    # Sort by frequency (count) descending, then by text length or something stable
    all_questions = []
    for q_text, q_data in questions_map.items():
        all_questions.append(q_data)
    
    # Sort: Primary key = count (desc), Secondary = year (desc) to prefer newer revisions if counts equal? 
    # Or just count.
    # The prompt says: "High Relevance Definition: Prioritize questions that have appeared most frequently"
    all_questions.sort(key=lambda x: (x['count'], max(x['years'] if x['years'] else [0])), reverse=True)
    
    total_slots_needed = 22 * QUESTIONS_PER_DAY
    unique_available = len(all_questions)
    
    print(f"Total unique questions available: {unique_available}")
    print(f"Total slots needed: {total_slots_needed}")
    
    # Prepare the list to distribute
    # We will fill the schedule with the top unique questions.
    # If we have more unique questions than slots, we just take the top N.
    # If we have fewer, we might need to repeat (but we have 1362 > 1100, so we are good).
    
    date_iterator = get_date_range()
    
    q_index = 0
    
    ensure_output_dir()
    
    for day_date in date_iterator:
        day_month_str = day_date.strftime("%m%d") # Format "0202"
        date_display = day_date.strftime("%d %B %Y")
        
        daily_questions = []
        
        # Select 50 questions
        for _ in range(QUESTIONS_PER_DAY):
            if q_index < len(all_questions):
                selected_q_data = all_questions[q_index]
                # Construct the question object for output
                # The stored 'data' in 'q_data' is the original question object.
                # We need to preserve that structure but maybe update year/metadata if needed?
                # The prompt example shows "year": 2017. 
                # Since we aggregated, a question might have multiple years. 
                # The prompt schema just shows "year": 2017 (singular).
                # We can just use the most recent year or the first year found from the stored data.
                # Let's use the 'data' field we saved which is one instance of the question.
                # But we might want to show which years it appeared if we were fancy, but strict schema says 'year': int.
                # So we stick to the one in 'data'.
                
                output_q = selected_q_data['data'].copy()
                
                # Assign a daily ID strictly 1 to 50
                output_q['id'] = len(daily_questions) + 1
                
                daily_questions.append(output_q)
                q_index += 1
            else:
                # Fallback if we run out of unique questions (shouldn't happen per check)
                # Loop back to start (high relevance)
                fallback_index = (q_index) % len(all_questions)
                selected_q_data = all_questions[fallback_index]
                output_q = selected_q_data['data'].copy()
                output_q['id'] = len(daily_questions) + 1
                daily_questions.append(output_q)
                q_index += 1

        output_json = {
            "date": day_month_str,
            "dateDisplay": date_display,
            "testTime": "19:00",
            "subject": "science",
            "questions": daily_questions
        }
        
        filename = f"{day_month_str}.json"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, indent=4, ensure_ascii=False)
            
        print(f"Generated {filename} with {len(daily_questions)} questions.")

if __name__ == "__main__":
    generate_sets()
