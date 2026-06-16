import json
import csv
import os

CORE_SKILLS = {
    "embeddings", "retrieval", "vector database", "pinecone", "weaviate", "qdrant",
    "milvus", "elasticsearch", "faiss", "ndcg", "mrr", "map", "rag", "search",
    "recommender", "recommendation", "learning-to-rank", "lora", "qlora",
    "fine-tuning", "nlp", "machine learning", "deep learning", "pytorch",
    "tensorflow", "scikit-learn"
}


def generate():
    csv_path = "submission.csv"
    candidates_path = "extracted_data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
    out_html = "dashboard.html"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist. Please run rank.py first.")
        return
        
    # Read the top 100 ranked candidate IDs, ranks, scores, and reasonings
    top_100_meta = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            top_100_meta[row['candidate_id']] = {
                'rank': int(row['rank']),
                'score': float(row['score']),
                'reasoning': row['reasoning']
            }
            
    # Find full profiles for these 100 candidates in the JSONL database
    top_100_profiles = {}
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                cid = data['candidate_id']
                if cid in top_100_meta:
                    top_100_profiles[cid] = data
                    
    # Combine metadata and profiles
    shortlist = []
    for cid, meta in top_100_meta.items():
        if cid in top_100_profiles:
            profile_data = top_100_profiles[cid]
            shortlist.append({
                'candidate_id': cid,
                'rank': meta['rank'],
                'score': meta['score'],
                'reasoning': meta['reasoning'],
                'profile': profile_data.get('profile', {}),
                'skills': profile_data.get('skills', []),
                'career': profile_data.get('career_history', []),
                'signals': profile_data.get('redrob_signals', {})
            })
            
    # Sort by rank
    shortlist.sort(key=lambda x: x['rank'])
    
    # HTML Content with premium dark-mode styling and interactions
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redrob AI Recruiter Shortlist Dashboard</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {{
            --bg-base: #080c14;
            --bg-surface: #0f1626;
            --bg-card: #151f32;
            --border-color: #23324e;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --primary: #14b8a6;
            --primary-hover: #0d9488;
            --accent: #6366f1;
            --danger: #ef4444;
            --success: #22c55e;
            --warning: #f59e0b;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            overflow-x: hidden;
            line-height: 1.5;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Outfit', sans-serif;
        }}
        
        header {{
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
            background-opacity: 0.9;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .logo i {{
            color: var(--primary);
            font-size: 1.8rem;
        }}
        
        .logo h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}
        
        .logo span {{
            color: var(--primary);
        }}
        
        .meta-pills {{
            display: flex;
            gap: 1rem;
        }}
        
        .pill {{
            background-color: rgba(20, 184, 166, 0.1);
            border: 1px solid rgba(20, 184, 166, 0.2);
            color: var(--primary);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        
        .pill.accent {{
            background-color: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            color: var(--accent);
        }}
        
        .dashboard-container {{
            display: grid;
            grid-template-columns: 320px 1fr;
            height: calc(100vh - 65px);
        }}
        
        /* Sidebar Filters */
        .sidebar {{
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}
        
        .filter-section-title {{
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }}
        
        .search-box {{
            position: relative;
        }}
        
        .search-box input {{
            width: 100%;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem 1rem 0.75rem 2.5rem;
            color: var(--text-primary);
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }}
        
        .search-box input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.15);
        }}
        
        .search-box i {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
        }}
        
        .checkbox-group {{
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }}
        
        .checkbox-label {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }}
        
        .checkbox-label:hover {{
            color: var(--text-primary);
        }}
        
        .checkbox-label input {{
            accent-color: var(--primary);
            width: 1rem;
            height: 1rem;
        }}
        
        /* Candidates View Grid */
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 450px;
            overflow: hidden;
        }}
        
        .candidates-list-wrapper {{
            padding: 1.5rem 2rem;
            overflow-y: auto;
            height: 100%;
        }}
        
        .list-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }}
        
        .list-header h2 {{
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        .list-header span {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .candidates-grid {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .candidate-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            display: flex;
            gap: 1.25rem;
        }}
        
        .candidate-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }}
        
        .candidate-card.active {{
            border-color: var(--primary);
            background-color: rgba(20, 184, 166, 0.03);
            box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.2);
        }}
        
        .rank-badge {{
            background: linear-gradient(135deg, var(--bg-surface) 0%, var(--border-color) 100%);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            width: 42px;
            height: 42px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            flex-shrink: 0;
            font-family: 'Outfit', sans-serif;
        }}
        
        .candidate-card:nth-child(1) .rank-badge {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            border-color: #f59e0b;
            color: #fff;
        }}
        .candidate-card:nth-child(2) .rank-badge {{
            background: linear-gradient(135deg, #94a3b8 0%, #475569 100%);
            border-color: #94a3b8;
            color: #fff;
        }}
        .candidate-card:nth-child(3) .rank-badge {{
            background: linear-gradient(135deg, #b45309 0%, #78350f 100%);
            border-color: #b45309;
            color: #fff;
        }}
        
        .card-details {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .card-row-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        
        .candidate-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .candidate-title {{
            font-size: 0.85rem;
            color: var(--primary);
            font-weight: 500;
            margin-top: 0.1rem;
        }}
        
        .score-pill {{
            background-color: rgba(20, 184, 166, 0.1);
            color: var(--primary);
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            border: 1px solid rgba(20, 184, 166, 0.2);
        }}
        
        .reasoning-preview {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-top: 0.25rem;
        }}
        
        .card-badges {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.4rem;
        }}
        
        .badge {{
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}
        
        .badge.highlight {{
            background-color: rgba(99, 102, 241, 0.08);
            border-color: rgba(99, 102, 241, 0.2);
            color: #818cf8;
        }}
        
        .badge.success {{
            background-color: rgba(34, 197, 94, 0.08);
            border-color: rgba(34, 197, 94, 0.2);
            color: #4ade80;
        }}
        
        /* Detail Pane */
        .detail-pane {{
            background-color: var(--bg-surface);
            border-left: 1px solid var(--border-color);
            padding: 1.5rem;
            overflow-y: auto;
            height: 100%;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}
        
        .detail-placeholder {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-secondary);
            text-align: center;
            gap: 1rem;
        }}
        
        .detail-placeholder i {{
            font-size: 3rem;
            color: var(--border-color);
        }}
        
        .detail-header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .detail-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .detail-headline {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-style: italic;
        }}
        
        .detail-score-circle {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid var(--primary);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: var(--primary);
            font-family: 'Outfit', sans-serif;
            background-color: rgba(20, 184, 166, 0.05);
        }}
        
        .detail-score-circle span {{
            font-size: 0.65rem;
            color: var(--text-secondary);
            font-weight: 400;
        }}
        
        .detail-section-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            border-left: 3px solid var(--primary);
            padding-left: 0.5rem;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .detail-reasoning-box {{
            background-color: rgba(20, 184, 166, 0.05);
            border: 1px solid rgba(20, 184, 166, 0.15);
            border-radius: 8px;
            padding: 1rem;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
        }}
        
        .timeline {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            position: relative;
            padding-left: 1rem;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 4px;
            top: 0.25rem;
            bottom: 0.25rem;
            width: 2px;
            background-color: var(--border-color);
        }}
        
        .timeline-item {{
            position: relative;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -16px;
            top: 6px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--border-color);
            border: 2px solid var(--bg-surface);
            transition: all 0.2s;
        }}
        
        .timeline-item.current::before {{
            background-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2);
        }}
        
        .timeline-comp {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .timeline-title {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
        
        .timeline-date {{
            font-size: 0.75rem;
            color: var(--primary);
            margin-bottom: 0.25rem;
        }}
        
        .timeline-desc {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
            background-color: var(--bg-card);
            padding: 0.5rem;
            border-radius: 6px;
        }}
        
        .skill-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}
        
        .skill-tag {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-size: 0.8rem;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        
        .skill-tag span {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}
        
        .skill-tag.core {{
            border-color: rgba(20, 184, 166, 0.3);
            background-color: rgba(20, 184, 166, 0.04);
            color: var(--primary);
        }}
        
        .signal-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }}
        
        .signal-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        
        .signal-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}
        
        .signal-value {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .empty-list-message {{
            text-align: center;
            color: var(--text-secondary);
            padding: 3rem;
            font-size: 1rem;
        }}
        
    </style>
</head>
<body>

    <header>
        <div class="logo">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            <h1>Redrob Matcher <span>AI</span></h1>
        </div>
        <div class="meta-pills">
            <div class="pill"><i class="fa-solid fa-user-tie"></i> Shortlisted: 100 Candidates</div>
            <div class="pill accent"><i class="fa-solid fa-shield-halved"></i> 94 Honeypots Blocked</div>
            <div class="pill accent"><i class="fa-solid fa-bolt"></i> Execution: 12.2s</div>
        </div>
    </header>

    <div class="dashboard-container">
        <!-- Sidebar Filters -->
        <div class="sidebar">
            <div>
                <div class="filter-section-title">Search Candidates</div>
                <div class="search-box">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="searchInput" placeholder="Search by name, title, skill..." oninput="filterCandidates()">
                </div>
            </div>
            
            <div>
                <div class="filter-section-title">Location Filter</div>
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" class="loc-filter" value="noida" onchange="filterCandidates()">
                        Noida (Local)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" class="loc-filter" value="delhi" onchange="filterCandidates()">
                        Delhi (Local)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" class="loc-filter" value="gurgaon" onchange="filterCandidates()">
                        Gurgaon (Local)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" class="loc-filter" value="pune" onchange="filterCandidates()">
                        Pune (Local)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="relocFilter" onchange="filterCandidates()">
                        Willing to Relocate
                    </label>
                </div>
            </div>
            
            <div>
                <div class="filter-section-title">Availability / Notice</div>
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="immediateFilter" onchange="filterCandidates()">
                        Sub-30 Day Notice Period
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="otwFilter" onchange="filterCandidates()">
                        Open to Work flag
                    </label>
                </div>
            </div>
            
            <div>
                <div class="filter-section-title">Profile Minimums</div>
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="minExpFilter" onchange="filterCandidates()">
                        5+ Years of Experience
                    </label>
                </div>
            </div>
        </div>
        
        <!-- Main View Grid -->
        <div class="main-content">
            <!-- Shortlist Column -->
            <div class="candidates-list-wrapper">
                <div class="list-header">
                    <h2>Top Ranked Shortlist</h2>
                    <span id="resultCount">Showing 100 of 100 Candidates</span>
                </div>
                
                <div class="candidates-grid" id="candidatesGrid">
                    <!-- Cards injected by JS -->
                </div>
            </div>
            
            <!-- Detail Pane Column -->
            <div class="detail-pane" id="detailPane">
                <div class="detail-placeholder">
                    <i class="fa-solid fa-id-card-clip"></i>
                    <p>Select a candidate to view their complete career history, skills, and behavioral signals.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Candidate Data Payload injected dynamically -->
    <script>
        const candidates = {json.dumps(shortlist)};
        const coreSkillsSet = {json.dumps(list(CORE_SKILLS))};
        
        let selectedCandidateId = null;

        function renderCandidates(filtered) {{
            const grid = document.getElementById('candidatesGrid');
            grid.innerHTML = '';
            
            document.getElementById('resultCount').textContent = `Showing ${{filtered.length}} of ${{candidates.length}} Candidates`;
            
            if (filtered.length === 0) {{
                grid.innerHTML = '<div class="empty-list-message">No matching candidates found matching the active filters.</div>';
                return;
            }}
            
            filtered.forEach(c => {{
                const card = document.createElement('div');
                card.className = `candidate-card ${{c.candidate_id === selectedCandidateId ? 'active' : ''}}`;
                card.onclick = () => selectCandidate(c.candidate_id);
                
                const exp = c.profile.years_of_experience;
                const notice = c.signals.notice_period_days;
                const loc = c.profile.location;
                
                let locationBadgeClass = 'badge';
                if (['Noida', 'Delhi', 'Gurgaon', 'Pune'].some(city => loc.includes(city))) {{
                    locationBadgeClass = 'badge success';
                }}
                
                card.innerHTML = `
                    <div class="rank-badge">${{c.rank}}</div>
                    <div class="card-details">
                        <div class="card-row-top">
                            <div>
                                <div class="candidate-name">${{c.profile.anonymized_name}}</div>
                                <div class="candidate-title">${{c.profile.current_title}}</div>
                            </div>
                            <div class="score-pill">${{c.score.toFixed(4)}}</div>
                        </div>
                        <div class="reasoning-preview">${{c.reasoning}}</div>
                        <div class="card-badges">
                            <span class="badge highlight"><i class="fa-solid fa-briefcase"></i> ${{exp}} yrs exp</span>
                            <span class="${{locationBadgeClass}}"><i class="fa-solid fa-location-dot"></i> ${{loc.split(',')[0]}}</span>
                            <span class="badge ${{notice <= 30 ? 'success' : ''}}"><i class="fa-regular fa-clock"></i> ${{notice}}d notice</span>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}
        
        function selectCandidate(cid) {{
            selectedCandidateId = cid;
            
            // Re-render card selection highlights
            const activeCards = document.querySelectorAll('.candidate-card');
            activeCards.forEach(card => {{
                card.classList.remove('active');
            }});
            
            // Re-render matching cards
            const currentFiltered = getCurrentFiltered();
            renderCandidates(currentFiltered);
            
            const cand = candidates.find(c => c.candidate_id === cid);
            if (!cand) return;
            
            const detailPane = document.getElementById('detailPane');
            
            // Generate skills tags list
            let skillsHTML = '';
            cand.skills.forEach(sk => {{
                const nameLower = sk.name.toLowerCase();
                const isCore = coreSkillsSet.some(cs => nameLower.includes(cs));
                skillsHTML += `
                    <span class="skill-tag ${{isCore ? 'core' : ''}}">
                        ${{sk.name}}
                        <span>${{sk.proficiency}}</span>
                    </span>
                `;
            }});
            
            // Generate career timeline list
            let careerHTML = '';
            cand.career.forEach((job, idx) => {{
                const start = job.start_date || 'Unknown';
                const end = job.is_current ? 'Present' : (job.end_date || 'Unknown');
                careerHTML += `
                    <div class="timeline-item ${{job.is_current ? 'current' : ''}}">
                        <div class="timeline-comp">${{job.company}}</div>
                        <div class="timeline-title">${{job.title}}</div>
                        <div class="timeline-date">${{start}} - ${{end}} (${{job.duration_months}} mos)</div>
                        <div class="timeline-desc">${{job.description}}</div>
                    </div>
                `;
            }});
            
            detailPane.innerHTML = `
                <div class="detail-header">
                    <div class="detail-title-row">
                        <div>
                            <h2>${{cand.profile.anonymized_name}}</h2>
                            <div class="candidate-title" style="font-size: 1rem;">${{cand.profile.current_title}}</div>
                        </div>
                        <div class="detail-score-circle">
                            ${{cand.score.toFixed(4)}}
                            <span>Score</span>
                        </div>
                    </div>
                    <div class="detail-headline">${{cand.profile.headline}}</div>
                </div>
                
                <div>
                    <div class="detail-section-title">Recruiter Assessment</div>
                    <div class="detail-reasoning-box">${{cand.reasoning}}</div>
                </div>
                
                <div>
                    <div class="detail-section-title">Platform Signals</div>
                    <div class="signal-grid">
                        <div class="signal-card">
                            <span class="signal-label">Notice Period</span>
                            <span class="signal-value">${{cand.signals.notice_period_days}} Days</span>
                        </div>
                        <div class="signal-card">
                            <span class="signal-label">Location</span>
                            <span class="signal-value">${{cand.profile.location}}</span>
                        </div>
                        <div class="signal-card">
                            <span class="signal-label">Willing to Relocate</span>
                            <span class="signal-value">${{cand.signals.willing_to_relocate ? 'Yes' : 'No'}}</span>
                        </div>
                        <div class="signal-card">
                            <span class="signal-label">Open To Work</span>
                            <span class="signal-value">${{cand.signals.open_to_work_flag ? 'Yes' : 'No'}}</span>
                        </div>
                        <div class="signal-card">
                            <span class="signal-label">GitHub Score</span>
                            <span class="signal-value">${{cand.signals.github_activity_score !== -1 ? cand.signals.github_activity_score.toFixed(1) : 'N/A'}}</span>
                        </div>
                        <div class="signal-card">
                            <span class="signal-label">Response Time</span>
                            <span class="signal-value">${{cand.signals.avg_response_time_hours.toFixed(1)}} Hours</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class="detail-section-title">Career Timeline</div>
                    <div class="timeline">
                        ${{careerHTML}}
                    </div>
                </div>
                
                <div>
                    <div class="detail-section-title">Verified Skills</div>
                    <div class="skill-grid">
                        ${{skillsHTML}}
                    </div>
                </div>
            `;
        }}
        
        function getCurrentFiltered() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            
            // Location checkboxes
            const locCheckboxes = document.querySelectorAll('.loc-filter:checked');
            const targetCities = Array.from(locCheckboxes).map(cb => cb.value);
            
            const relocChecked = document.getElementById('relocFilter').checked;
            const immediateChecked = document.getElementById('immediateFilter').checked;
            const otwChecked = document.getElementById('otwFilter').checked;
            const minExpChecked = document.getElementById('minExpFilter').checked;
            
            return candidates.filter(c => {{
                // Search term match
                const name = c.profile.anonymized_name.toLowerCase();
                const title = c.profile.current_title.toLowerCase();
                const headline = c.profile.headline.toLowerCase();
                const skills = c.skills.map(sk => sk.name.toLowerCase()).join(' ');
                
                const matchesSearch = !search || 
                    name.includes(search) || 
                    title.includes(search) || 
                    headline.includes(search) || 
                    skills.includes(search);
                    
                if (!matchesSearch) return false;
                
                // Location match
                if (targetCities.length > 0) {{
                    const locLower = c.profile.location.toLowerCase();
                    const matchesLoc = targetCities.some(city => locLower.includes(city));
                    if (!matchesLoc) return false;
                }}
                
                // Relocation match
                if (relocChecked && !c.signals.willing_to_relocate) return false;
                
                // Notice Period match
                if (immediateChecked && c.signals.notice_period_days > 30) return false;
                
                // Open to Work match
                if (otwChecked && !c.signals.open_to_work_flag) return false;
                
                // Min Exp match
                if (minExpChecked && c.profile.years_of_experience < 5.0) return false;
                
                return true;
            }});
        }}
        
        function filterCandidates() {{
            const filtered = getCurrentFiltered();
            renderCandidates(filtered);
            
            // Keep selection if it's still in the filtered list
            if (selectedCandidateId && !filtered.some(c => c.candidate_id === selectedCandidateId)) {{
                // Reset detail pane
                document.getElementById('detailPane').innerHTML = `
                    <div class="detail-placeholder">
                        <i class="fa-solid fa-id-card-clip"></i>
                        <p>Select a candidate to view their complete career history, skills, and behavioral signals.</p>
                    </div>
                `;
                selectedCandidateId = null;
            }}
        }}
        
        // Initial render
        renderCandidates(candidates);
    </script>
</body>
</html>
"""
    
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Dashboard successfully generated and saved to {out_html}")

if __name__ == "__main__":
    generate()
