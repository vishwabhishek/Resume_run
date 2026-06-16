import json
import datetime

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def get_honeypots():
    honeypots_skills = set()
    honeypots_dates = set()
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            cid = data.get("candidate_id")
            
            # Check 1: expert/advanced skill with 0 duration
            has_expert_zero = any(sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0 for sk in data.get("skills", []))
            if has_expert_zero:
                honeypots_skills.add(cid)
                
            # Check 2: Krutrim or Sarvam AI before 2023
            has_prefounding = False
            for job in data.get("career_history", []):
                comp = job.get("company", "").strip()
                start_str = job.get("start_date")
                if not start_str:
                    continue
                try:
                    start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                    if comp in ["Krutrim", "Sarvam AI"] and start_date.year < 2023:
                        has_prefounding = True
                except:
                    pass
            if has_prefounding:
                honeypots_dates.add(cid)
                
    overlap = honeypots_skills.intersection(honeypots_dates)
    union = honeypots_skills.union(honeypots_dates)
    
    print(f"Honeypots by skills: {len(honeypots_skills)}")
    print(f"Honeypots by dates: {len(honeypots_dates)}")
    print(f"Overlap: {len(overlap)}")
    print(f"Union (Total potential honeypots): {len(union)}")
    print(f"Sample union: {sorted(list(union))[:20]}")

if __name__ == "__main__":
    get_honeypots()
