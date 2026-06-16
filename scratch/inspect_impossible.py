import json
from datetime import datetime

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
current_date = datetime(2026, 6, 16)

def inspect():
    honeypot_candidates = []
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            cid = data.get("candidate_id")
            profile = data.get("profile", {})
            career = data.get("career_history", [])
            skills = data.get("skills", [])
            education = data.get("education", [])
            
            reasons = []
            
            # Check 1: Single job duration > total years of experience
            years_exp = profile.get("years_of_experience", 0)
            for job in career:
                job_years = job.get("duration_months", 0) / 12.0
                if job_years > years_exp + 0.1:
                    reasons.append(f"job_duration_{job.get('duration_months')}_months_exceeds_total_exp_{years_exp}_years")
            
            # Check 2: Total duration of non-overlapping jobs > total years of experience? 
            # Or overlapping dates that are completely impossible (e.g. working full time at two different companies for 5 years simultaneously)
            # Actually, let's look at start/end dates. If there are multiple current jobs or overlaps:
            
            # Check 3: "expert" proficiency in skills with 0 duration
            expert_zero = sum(1 for sk in skills if sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0)
            # Let's see if they have multiple expert/advanced skills with 0 duration. We saw 21 candidates with >= 3.
            if expert_zero >= 3:
                reasons.append(f"expert_zero_duration_skills_{expert_zero}")
                
            # Check 4: Age or education timeline mismatch
            # E.g. start_year > end_year in education
            for edu in education:
                sy = edu.get("start_year", 0)
                ey = edu.get("end_year", 0)
                if sy > ey:
                    reasons.append(f"edu_start_{sy}_after_end_{ey}")
            
            # Check 5: Job start date is before education start date by a lot, or during education?
            # Usually some work during education is fine, but starting a full time role before education starts?
            
            # Check 6: Mismatched description details.
            # E.g. description says "mechanical engineering" but title is "Marketing Manager".
            # Let's check if the description text mentions a completely different job.
            # Let's inspect descriptions for mismatched keywords:
            for job in career:
                title = job.get("title", "").lower()
                desc = job.get("description", "").lower()
                if "marketing manager" in title and "mechanical engineering" in desc:
                    reasons.append("marketing_manager_with_mechanical_engineering_desc")
                if "operations manager" in title and "mechanical engineering" in desc:
                    # Saanvi Sethi (CAND_0000002) had this: "Operations Manager" at "Wipro" with "Mechanical engineering design role at a hardware-product company"
                    # Wait, Saanvi Sethi is a sample candidate. Is Saanvi Sethi a honeypot?
                    # Wait, let's check if Saanvi Sethi is a honeypot.
                    # Saanvi's current title is "Operations Manager" and she worked as "Operations Manager" at Wipro from 2021-09-13 to 2022-11-07 (14 months)
                    # and the description is "Mechanical engineering design role... CAD, FEA, ANSYS...".
                    # Is this considered a honeypot or is this just synthetic noise?
                    # Let's look at the description of honeypots:
                    # "The dataset contains a small number (~80) of honeypot candidates with subtly impossible profiles (e.g., 8 years of experience at a company founded 3 years ago; "expert" proficiency in 10 skills with 0 years used)."
                    pass

            if reasons:
                honeypot_candidates.append((cid, reasons))

    print(f"Total logical anomalies found: {len(honeypot_candidates)}")
    for cid, reasons in honeypot_candidates[:20]:
        print(f"  {cid}: {reasons}")

if __name__ == "__main__":
    inspect()
