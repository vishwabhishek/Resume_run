import json
from collections import defaultdict
from datetime import datetime

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
current_date = datetime(2026, 6, 16)

def analyze():
    # Keep track of min start date for each company across the entire dataset to infer when it might have been founded,
    # or look at durations of people who work there.
    # Actually, if a company was founded 3 years ago, it means its oldest start date in the dataset (or real life) is 3 years ago.
    # But wait, if someone has a start date 8 years ago at that company, they are a honeypot!
    # Let's collect all start dates for each company.
    company_starts = defaultdict(list)
    company_durations = defaultdict(list)
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            career = data.get("career_history", [])
            for job in career:
                comp = job.get("company", "").strip()
                start_str = job.get("start_date")
                duration = job.get("duration_months", 0)
                if comp and start_str:
                    try:
                        start_date = datetime.strptime(start_str, "%Y-%m-%d")
                        company_starts[comp].append(start_date)
                        company_durations[comp].append(duration)
                    except:
                        pass
                        
    # For each company, find the minimum start date, maximum duration, etc.
    print("Company | Count | Min Start Date | Max Start Date | Max Duration (months)")
    print("-" * 80)
    for comp in sorted(company_starts.keys()):
        starts = company_starts[comp]
        durs = company_durations[comp]
        min_start = min(starts).strftime("%Y-%m-%d")
        max_start = max(starts).strftime("%Y-%m-%d")
        max_dur = max(durs)
        print(f"{comp} | {len(starts)} | {min_start} | {max_start} | {max_dur}")

if __name__ == "__main__":
    analyze()
