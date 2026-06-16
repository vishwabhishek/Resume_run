import json
from datetime import datetime

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
current_date = datetime(2026, 6, 16) # Current date based on metadata

def parse_date(d_str):
    if not d_str:
        return None
    try:
        return datetime.strptime(d_str, "%Y-%m-%d")
    except:
        return None

def find_anomalies():
    anomalies = []
    count = 0
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            count += 1
            data = json.loads(line)
            cid = data.get("candidate_id")
            profile = data.get("profile", {})
            career = data.get("career_history", [])
            skills = data.get("skills", [])
            education = data.get("education", [])
            
            reasons = []
            
            # 1. Check skill duration vs proficiency
            # "expert" proficiency in 10 skills with 0 years used
            expert_zero_duration = sum(1 for sk in skills if sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0)
            if expert_zero_duration >= 5:
                reasons.append(f"expert_zero_duration_skills_{expert_zero_duration}")
                
            # 2. Check career duration vs dates
            for job in career:
                start = parse_date(job.get("start_date"))
                end = parse_date(job.get("end_date")) if job.get("end_date") else current_date
                if start:
                    actual_months = (end.year - start.year) * 12 + (end.month - start.month)
                    declared_months = job.get("duration_months", 0)
                    if abs(actual_months - declared_months) > 3: # Allow slight buffer
                        reasons.append(f"job_months_mismatch_{job.get('company')}_{declared_months}_vs_actual_{actual_months}")
            
            # 3. Check for specific impossible things, e.g. company founded 3 years ago but 8 years of experience.
            # Let's see if there are companies that are startups (founded recently) but have long durations.
            # Or if a single job duration is greater than years of experience.
            total_duration_months = sum(job.get("duration_months", 0) for job in career)
            years_exp = profile.get("years_of_experience", 0)
            if abs(total_duration_months / 12.0 - years_exp) > 2.0:
                # Some overlapping is fine, but if total_duration is way off or years of experience is much smaller:
                # E.g. years of experience is 3 but worked for 8 years at a company
                pass
                
            # 4. Check for description vs title mismatch
            # E.g. description talks about accounting or marketing but title is Civil Engineer or Software Engineer.
            # Let's check some keywords in descriptions that don't match the title at all.
            for job in career:
                desc = job.get("description", "").lower()
                title = job.get("title", "").lower()
                # If title is Civil Engineer but description mentions SaaS, marketing, or accounting
                if "civil engineer" in title and ("marketing" in desc or "accounting" in desc or "saas" in desc or "revenue" in desc):
                    reasons.append(f"mismatched_desc_civil_engineer_{job.get('company')}")
                if "accounting" in desc and "accountant" not in title and "finance" not in title and "accounting" not in title and "billing" not in title:
                    # Check if title is completely unrelated, like Software Engineer or Business Analyst with pure accounting desc
                    if "software" in title or "developer" in title or "engineer" in title or "analyst" in title:
                        reasons.append(f"mismatched_desc_accounting_in_{title}")
                        
            # 5. Check education timeline mismatch
            # e.g. start year > end year, or M.Tech ended before B.Tech started, or graduation in 2005 but experience started in 2024
            if education:
                grad_years = [edu.get("end_year") for edu in education if edu.get("end_year")]
                if grad_years:
                    max_grad_year = max(grad_years)
                    min_grad_year = min(grad_years)
                    first_job_year = min([parse_date(job.get("start_date")).year for job in career if parse_date(job.get("start_date"))] or [9999])
                    if first_job_year != 9999 and first_job_year - max_grad_year > 10:
                        # Graduated more than 10 years before first job
                        reasons.append(f"huge_gap_grad_{max_grad_year}_to_first_job_{first_job_year}")
                    if any(edu.get("start_year", 0) > edu.get("end_year", 0) for edu in education):
                        reasons.append("education_start_after_end")

            if reasons:
                anomalies.append((cid, reasons))
                
            if len(anomalies) >= 100:
                # Let's inspect the first 100
                pass
                
    print(f"Total processed: {count}")
    print(f"Total anomalies found: {len(anomalies)}")
    print("Sample anomalies:")
    for a in anomalies[:20]:
        print(f"  {a[0]}: {a[1]}")

if __name__ == "__main__":
    find_anomalies()
