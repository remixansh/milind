import os
import json
import collections

DAILY_DIR = r"c:/Users/HP/Desktop/CS Project/experimental/boards/daily_social_science"

def list_missing():
    missing_counts = collections.defaultdict(int)
    questions_data = {}

    files = [f for f in os.listdir(DAILY_DIR) if f.endswith('.json')]
    
    for filename in files:
        path = os.path.join(DAILY_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for q in data.get('questions', []):
            if q.get('correct') == -1:
                q_text = q.get('question', '').strip()
                missing_counts[q_text] += 1
                if q_text not in questions_data:
                    questions_data[q_text] = q

    # Sort by frequency
    sorted_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Total unique questions missing answers: {len(sorted_missing)}")
    print("-" * 40)
    
    # Print top 20
    for q_text, count in sorted_missing[:20]:
        q = questions_data[q_text]
        print(f"Count: {count}")
        print(f"Q: {q_text}")
        print(f"Options: {q.get('options')}")
        print("-" * 20)

if __name__ == "__main__":
    list_missing()
