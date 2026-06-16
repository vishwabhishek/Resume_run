import json
from collections import defaultdict
from datetime import datetime
import numpy as np

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def find_outliers():
    company_starts = defaultdict(list)
    
    # First pass: collect all start dates (as timestamps) for each company
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            career = data.get("career_history", [])
            for job in career:
                comp = job.get("company", "").strip()
                start_str = job.get("start_date")
                if comp and start_str:
                    try:
                        start_date = datetime.strptime(start_str, "%Y-%m-%d")
                        company_starts[comp].append(start_date.timestamp())
                    except:
                        pass

    # For each company, calculate percentiles of start dates
    company_stats = {}
    for comp, timestamps in company_starts.items():
        if len(timestamps) > 10:
            p5 = np.percentile(timestamps, 5) # 5th percentile
            p1 = np.percentile(timestamps, 1) # 1st percentile
            mean = np.mean(timestamps)
            std = np.std(timestamps)
            company_stats[comp] = {
                'p5': p5,
                'p1': p1,
                'mean': mean,
                'std': std,
                'min_date': datetime.fromtimestamp(min(timestamps)).strftime("%Y-%m-%d")
            }

    # Second pass: find candidates whose start date at a company is an outlier
    # E.g. start date is way before the 1st percentile or mean - 3*std
    outlier_candidates = []
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
                if comp in company_stats and start_str:
                    try:
                        ts = datetime.strptime(start_str, "%Y-%m-%d").timestamp()
                        stats = company_stats[comp]
                        # If the start date is more than 3 standard deviations below the mean,
                        # or significantly before the 1st percentile (e.g., more than 1 year before)
                        # Let's check if it is an outlier
                        if ts < stats['p1'] - 31536000: # 1 year in seconds
                            outlier_candidates.append((cid, comp, start_str, stats['min_date']))
                    except:
                        pass
                        
    print(f"Found {len(outlier_candidates)} company start date outliers:")
    for cid, comp, start_str, min_date in outlier_candidates[:30]:
        print(f"  {cid}: started at {comp} on {start_str} (normal min start date is around {min_date})")

if __name__ == "__main__":
    find_outliers()
