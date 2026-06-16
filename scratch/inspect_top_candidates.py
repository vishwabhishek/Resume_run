import json
import gzip
from datetime import datetime
import numpy as np

candidates_path = "/home/abhishek-vishwakarma/Documents/Resume_Run/extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"

# List of consulting/IT services companies to disqualify if candidate worked ONLY there
CONSULTING_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "capgemini", "cognizant",
    "tech mahindra", "hcl", "mindtree", "mphasis", "genpact ai"
}

# List of product companies (fictional + real) to award product fit points
PRODUCT_COMPANIES = {
    "pied piper", "hooli", "initech", "dunder mifflin", "globex inc", "acme corp",
    "wayne enterprises", "stark industries", "cred", "flipkart", "freshworks",
    "meesho", "nykaa", "ola", "paytm", "pharmeasy", "phonepe", "razorpay",
    "swiggy", "unacademy", "vedantu", "zoho", "zomato", "upgrad", "krutrim",
    "sarvam ai", "rephrase.ai", "saarthi.ai", "observe.ai", "niramai",
    "mad street den", "locobuzz", "haptik", "yellow.ai", "verloop.io",
    "wysa", "aganitha", "glance", "inmobi", "google", "meta", "netflix",
    "uber", "amazon", "apple", "microsoft", "linkedin", "adobe", "salesforce"
}

TARGET_CITIES = {"pune", "noida", "delhi", "gurgaon", "ghaziabad", "faridabad"}

CORE_SKILLS = {
    "embeddings", "retrieval", "vector database", "pinecone", "weaviate", "qdrant",
    "milvus", "elasticsearch", "faiss", "ndcg", "mrr", "map", "rag", "search",
    "recommender", "recommendation", "learning-to-rank", "lora", "qlora",
    "fine-tuning", "nlp", "machine learning", "deep learning", "pytorch",
    "tensorflow", "scikit-learn"
}

# Specific ML keywords for checking titles/descriptions
ML_TITLE_KEYWORDS = {"ai", "ml", "machine learning", "nlp", "search", "retrieval", "recommender", "recommendation", "ranking", "data scientist", "computer vision", "cv", "speech"}

def parse_date(d_str):
    if not d_str:
        return None
    try:
        return datetime.strptime(d_str, "%Y-%m-%d")
    except:
        return None

def is_honeypot(data):
    skills = data.get("skills", [])
    has_expert_zero = any(sk.get("proficiency") in ["expert", "advanced"] and sk.get("duration_months", 0) == 0 for sk in skills)
    if has_expert_zero:
        return True
    career = data.get("career_history", [])
    for job in career:
        comp = job.get("company", "").strip()
        start_str = job.get("start_date")
        if not start_str:
            continue
        start_date = parse_date(start_str)
        if start_date:
            if comp in ["Krutrim", "Sarvam AI"] and start_date.year < 2023:
                return True
    return False

def check_consulting_only(career):
    if not career:
        return False
    companies = [job.get("company", "").strip().lower() for job in career if job.get("company")]
    if not companies:
        return False
    return all(comp in CONSULTING_COMPANIES for comp in companies)

def score_candidate_v2(data):
    profile = data.get("profile", {})
    career = data.get("career_history", [])
    skills = data.get("skills", [])
    signals = data.get("redrob_signals", {})
    
    # 1. Hard filters / Disqualifiers
    if is_honeypot(data) or check_consulting_only(career):
        return 0.0, {}
        
    # 2. Experience Year Fit Score (Target: 5-9 years, ideally 6-8)
    exp = profile.get("years_of_experience", 0)
    if exp < 3.0:
        exp_score = 0.0
    elif exp < 5.0:
        exp_score = 0.4 + 0.6 * (exp - 3.0) / 2.0
    elif 5.0 <= exp <= 9.0:
        exp_score = 1.0
    elif 9.0 < exp <= 12.0:
        exp_score = 1.0 - 0.5 * (exp - 9.0) / 3.0
    else:
        exp_score = 0.5 - 0.4 * min(exp - 12.0, 8.0) / 8.0
        exp_score = max(exp_score, 0.05)
        
    # 3. Calculate ML/AI specific career history duration
    # Let's count how many months of experience they have in ML/AI/Data Science roles
    ml_months = 0
    for job in career:
        job_title = job.get("title", "").lower()
        job_desc = job.get("description", "").lower()
        duration = job.get("duration_months", 0)
        
        # Check if the title is ML-related
        is_ml_job = any(kw in job_title for kw in ["ml ", " ml", "ai ", " ai", "machine learning", "nlp", "search", "retrieval", "recommender", "recommendation", "ranking", "data scientist", "data science"])
        # Or if the description has strong ML indicators
        has_ml_desc = any(kw in job_desc for kw in ["machine learning", "deep learning", "nlp", "neural network", "transformer", "embeddings", "vector search", "recommender system"])
        
        if is_ml_job or has_ml_desc:
            ml_months += duration
            
    ml_years = ml_months / 12.0
    # Score ML experience duration: prefer 3+ years of ML experience
    if ml_years == 0:
        ml_exp_score = 0.0
    elif ml_years < 3.0:
        ml_exp_score = 0.3 + 0.7 * (ml_years / 3.0)
    else:
        ml_exp_score = 1.0
        
    # 4. Role / Title Relevance Score
    title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    
    # Non-tech filters
    non_tech_keywords = ["marketing", "operations manager", "accountant", "hr manager", "civil engineer", "mechanical engineer", "business analyst", "project manager", "product manager", "qa ", "test engineer"]
    is_non_tech = any(kw in title for kw in non_tech_keywords)
    
    if is_non_tech:
        role_score = 0.0
    elif any(kw in title for kw in ["ai engineer", "ml engineer", "machine learning engineer", "nlp engineer", "search engineer", "retrieval engineer", "recommender engineer", "ranking engineer"]):
        role_score = 1.0
    elif "data scientist" in title:
        role_score = 0.9
    elif any(kw in title for kw in ["backend", "software engineer", "developer", "full stack", "data engineer"]):
        # Backend with ML focus
        if ml_years > 1.0:
            role_score = 0.8
        else:
            role_score = 0.4
    else:
        role_score = 0.1
        
    # 5. Skills Score (Matches core retrieval and ML skills)
    skill_score = 0.0
    matched_skills = []
    for sk in skills:
        name = sk.get("name", "").lower()
        prof = sk.get("proficiency", "beginner").lower()
        dur = sk.get("duration_months", 0)
        
        is_core = any(cs in name for cs in CORE_SKILLS)
        if is_core:
            matched_skills.append(name)
            prof_mult = {"expert": 4, "advanced": 3, "intermediate": 2, "beginner": 1}.get(prof, 1)
            dur_mult = np.log1p(dur) / np.log1p(60)
            skill_score += prof_mult * dur_mult
            
    norm_skill_score = min(skill_score / 15.0, 1.0)
    
    # 6. Description Keywords Score
    keyword_matches = 0
    system_keywords = ["embedding", "retrieval", "vector", "search", "recommender", "recommendation", "ranking", "ndcg", "mrr", "map", "rag", "fine-tune", "lora", "qlora", "eval"]
    for job in career:
        desc = job.get("description", "").lower()
        job_title = job.get("title", "").lower()
        matches = sum(1 for kw in system_keywords if kw in desc or kw in job_title)
        keyword_matches += matches
    norm_system_score = min(keyword_matches / 6.0, 1.0)
    
    # 7. Product Company Fit
    total_months = sum(job.get("duration_months", 0) for job in career)
    product_months = sum(job.get("duration_months", 0) for job in career if job.get("company", "").strip().lower() in PRODUCT_COMPANIES)
    product_ratio = (product_months / total_months) if total_months > 0 else 0.0
    product_score = 0.5 + 0.5 * product_ratio
    
    # Profile Fit Score (Total out of 1.0)
    # Give ML experience and skills high weights, and years of experience / role score
    profile_fit = (
        exp_score * 0.15 + 
        ml_exp_score * 0.25 + 
        role_score * 0.20 + 
        norm_skill_score * 0.20 + 
        norm_system_score * 0.10 + 
        product_score * 0.10
    )
    
    # 8. Behavioral Signals (Modified range to avoid overriding profile fit)
    # We use a base multiplier of 1.0, and add small bonuses / apply strong penalties
    behavioral_bonus = 0.0
    
    # Recency (Decay)
    last_act_str = signals.get("last_active_date", "")
    last_act = parse_date(last_act_str)
    recency_mult = 1.0
    if last_act:
        ref_date = datetime(2026, 6, 16)
        months_inactive = (ref_date.year - last_act.year) * 12 + (ref_date.month - last_act.month)
        if months_inactive <= 1:
            behavioral_bonus += 0.03
        elif months_inactive <= 3:
            behavioral_bonus += 0.01
        elif months_inactive <= 6:
            recency_mult = 0.8
        else:
            recency_mult = 0.4
    else:
        recency_mult = 0.5
        
    # Recruiter Response Rate
    rr = signals.get("recruiter_response_rate", 0.0)
    if rr >= 0.8:
        behavioral_bonus += 0.03
    elif rr >= 0.5:
        behavioral_bonus += 0.01
    elif rr < 0.2:
        recency_mult *= 0.7  # Additional penalty for very low response rate
        
    # Average Response Time
    rt = signals.get("avg_response_time_hours", 24.0)
    if rt <= 4.0:
        behavioral_bonus += 0.02
    elif rt > 72.0:
        recency_mult *= 0.9
        
    # Open to Work
    if signals.get("open_to_work_flag", False):
        behavioral_bonus += 0.03
        
    # GitHub Activity
    gh = signals.get("github_activity_score", -1)
    if gh > 50:
        behavioral_bonus += 0.03
    elif gh > 10:
        behavioral_bonus += 0.01
        
    # Notice Period
    np_days = signals.get("notice_period_days", 0)
    np_mult = 1.0
    if np_days <= 30:
        behavioral_bonus += 0.03
    elif np_days > 90:
        np_mult = 0.5
    elif np_days > 60:
        np_mult = 0.8
        
    # Location
    loc_str = profile.get("location", "").lower()
    willing_relocate = signals.get("willing_to_relocate", False)
    is_local = any(tc in loc_str for tc in TARGET_CITIES)
    loc_mult = 1.0
    if is_local:
        behavioral_bonus += 0.03
    else:
        is_tier1 = any(city in loc_str for city in ["bangalore", "mumbai", "hyderabad", "chennai", "kolkata"])
        if is_tier1:
            if not willing_relocate:
                loc_mult = 0.75
        else:
            if willing_relocate:
                loc_mult = 0.85
            else:
                loc_mult = 0.5
                
    final_mult = recency_mult * np_mult * loc_mult
    final_score = profile_fit * (1.0 + behavioral_bonus) * final_mult
    
    breakdown = {
        "exp_score": exp_score,
        "ml_exp_score": ml_exp_score,
        "role_score": role_score,
        "norm_skill_score": norm_skill_score,
        "norm_system_score": norm_system_score,
        "product_score": product_score,
        "profile_fit": profile_fit,
        "behavioral_bonus": behavioral_bonus,
        "final_mult": final_mult,
        "ml_years": ml_years,
        "matched_skills": matched_skills
    }
    
    return float(np.round(final_score, 4)), breakdown

def test():
    candidates = []
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                candidates.append(json.loads(line))
                
    scored = []
    for cand in candidates:
        score, bd = score_candidate_v2(cand)
        if score > 0.0:
            scored.append((cand, score, bd))
            
    scored.sort(key=lambda x: x[0]["candidate_id"])
    scored.sort(key=lambda x: x[1], reverse=True)
    
    print("TOP 20 CANDIDATES BREAKDOWN (V2):")
    print("-" * 100)
    for idx, (cand, score, bd) in enumerate(scored[:20]):
        prof = cand["profile"]
        print(f"#{idx+1} {cand['candidate_id']} | {prof['anonymized_name']} | Score: {score}")
        print(f"  Title: {prof['current_title']} | Headline: {prof['headline']}")
        print(f"  Exp: {prof['years_of_experience']} yrs | ML Exp: {bd['ml_years']:.1f} yrs")
        print(f"  Skills: {', '.join(bd['matched_skills'][:5])}")
        print(f"  Breakdown: profile_fit={bd['profile_fit']:.3f}, bonus={bd['behavioral_bonus']:.2f}, mult={bd['final_mult']:.2f}")
        print(f"  Product Companies: {[job.get('company') for job in cand.get('career_history', []) if job.get('company', '').strip().lower() in PRODUCT_COMPANIES]}")
        print("-" * 100)

if __name__ == "__main__":
    test()
