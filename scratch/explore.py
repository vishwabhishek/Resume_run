import json
import gzip
import os
from collections import Counter

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def explore():
    total_count = 0
    locations = Counter()
    experience = []
    current_companies = Counter()
    current_industries = Counter()
    skills_counter = Counter()
    
    # Honeypot candidates check
    honeypot_candidates = []
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            total_count += 1
            data = json.loads(line)
            profile = data.get("profile", {})
            loc = profile.get("location", "")
            locations[loc] += 1
            experience.append(profile.get("years_of_experience", 0))
            current_companies[profile.get("current_company", "")] += 1
            current_industries[profile.get("current_industry", "")] += 1
            
            skills = data.get("skills", [])
            for sk in skills:
                skills_counter[sk.get("name", "")] += 1
                
            # Check for possible honeypot features
            # E.g., expert proficiency in 10 skills with 0 duration_months
            expert_zero_duration_skills = 0
            for sk in skills:
                if sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0:
                    expert_zero_duration_skills += 1
            
            # E.g. Check overlap in career history, or total duration at a company exceeds years of experience,
            # or experience at a company founded recently (but how do we know founding date? Maybe we don't, 
            # let's look for suspicious things).
            # Let's inspect some candidate profiles with expert/advanced skills but 0 duration.
            if expert_zero_duration_skills >= 5 or (len(skills) > 0 and all(sk.get("duration_months", 0) == 0 for sk in skills)):
                honeypot_candidates.append((data.get("candidate_id"), "zero_duration_skills", len(skills), expert_zero_duration_skills))
                
            if total_count >= 1000:
                # Let's check first 1000 first, or we can scan all since it takes very little time.
                pass
                
    print(f"Total candidates: {total_count}")
    print(f"Average experience: {sum(experience)/len(experience):.2f} years")
    print(f"Location sample (top 20): {locations.most_common(20)}")
    print(f"Current companies sample (top 20): {current_companies.most_common(20)}")
    print(f"Current industries sample (top 20): {current_industries.most_common(20)}")
    print(f"Skills sample (top 20): {skills_counter.most_common(20)}")
    print(f"Potential honeypots based on 0-duration skill check (found in first scan): {len(honeypot_candidates)}")
    if honeypot_candidates:
        print(f"Sample honeypots: {honeypot_candidates[:10]}")

if __name__ == "__main__":
    explore()
