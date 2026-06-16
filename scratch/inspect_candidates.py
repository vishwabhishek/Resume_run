import json

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

def inspect_candidates(ids):
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            cid = data.get("candidate_id")
            if cid in ids:
                print(f"--- CANDIDATE {cid} ---")
                print(json.dumps(data, indent=2))
                print()

if __name__ == "__main__":
    inspect_candidates(["CAND_0016000", "CAND_0046649"])
