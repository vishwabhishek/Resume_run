import json
from datetime import datetime

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def check_dates():
    # Real life founding dates:
    # Krutrim: Dec 2023
    # Sarvam AI: Jul 2023
    # CRED: Nov 2018
    # Razorpay: 2014
    # Swiggy: Aug 2014
    # Zomato: Jul 2008
    # Let's count candidates who started before these dates.
    
    anomalous_candidates = []
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            cid = data.get("candidate_id")
            career = data.get("career_history", [])
            
            for job in career:
                comp = job.get("company", "").strip()
                start_str = job.get("start_date")
                if not start_str:
                    continue
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                    year = start_date.year
                    
                    if comp == "Krutrim" and year < 2023:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                    elif comp == "Sarvam AI" and year < 2023:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                    elif comp == "CRED" and year < 2018:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                    elif comp == "Razorpay" and year < 2014:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                    elif comp == "Swiggy" and year < 2014:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                    elif comp == "Zomato" and year < 2008:
                        anomalous_candidates.append((cid, comp, start_str, job.get("duration_months")))
                except:
                    pass
                    
    print(f"Found {len(anomalous_candidates)} candidates with pre-founding start dates:")
    for cid, comp, start_str, dur in anomalous_candidates[:30]:
        print(f"  {cid}: {comp} starting on {start_str} (duration: {dur} months)")

if __name__ == "__main__":
    check_dates()
