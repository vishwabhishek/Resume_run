import json

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def find():
    expert_zero_counts = {}
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            cid = data.get("candidate_id")
            skills = data.get("skills", [])
            
            expert_zero = sum(1 for sk in skills if sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0)
            if expert_zero > 0:
                expert_zero_counts[cid] = (expert_zero, len(skills))
                
    # Print statistics of how many expert_zeros exist
    from collections import Counter
    c = Counter([v[0] for v in expert_zero_counts.values()])
    print("Number of expert/advanced skills with 0 duration per candidate:")
    for k in sorted(c.keys()):
        print(f"  {k} skills: {c[k]} candidates")
        
    # Print some candidate IDs with many such skills
    print("Candidates with >= 5 such skills:")
    for cid, (ez, total) in list(expert_zero_counts.items())[:15]:
        if ez >= 5:
            print(f"  {cid}: {ez} out of {total} skills")

if __name__ == "__main__":
    find()
