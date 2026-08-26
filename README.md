<div align="center">

# ✦ TalentLens AI
### Enterprise AI Resume Screening & Candidate Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

*An explainable, multi-factor AI recruitment assistant built for hiring teams, recruiters, and engineering leaders.*

[Key Features](#-key-features) • [Architecture](#-architecture--matching-engine) • [Installation](#-installation--quick-start) • [Live Deployment](#-cloud-deployment) • [License](#-license)

</div>

---

## 🌟 Key Features

- 🧠 **Multi-Factor Explainable AI Matching**:
  - **45% Skill Intersection Coverage** against 250+ categorized industry technical proficiencies.
  - **35% Semantic Relevance** using sublinear TF-IDF N-gram cosine similarity.
  - **20% Contextual & Keyword Alignment**.
- 📄 **Multi-Modal Document Parsing**:
  - High-precision text and layout extraction from **PDF** (pdfplumber & PyPDF2) and **DOCX** files (python-docx).
  - Automatic entity extraction: Full Name, Email, Phone Number, LinkedIn, GitHub, Estimated Years of Experience, and Education Level.
- ⚡ **1-Click Batch Screening**:
  - Screen dozens of candidate resumes simultaneously against any selected job description with real-time animated progress tracking.
- 💼 **Job Role Management & Preset Library**:
  - Pre-configured industry benchmark templates (*Senior Full Stack Developer*, *Lead AI/ML Engineer*, *Cloud DevOps Specialist*) + custom role builder.
- 🔍 **Candidate Deep Dive & Radar Analytics**:
  - Interactive multi-dimensional **Radar Competency Spider Charts**, skill gap chips, and recruiter evaluation guidance (*Strengths*, *Gaps*, *Suggested Interview Questions*).
- ⚖️ **Side-by-Side Candidate Comparison**:
  - Compare 2 to 3 candidates simultaneously across match scores, experience, education, and skill matrices with grouped visual charts.
- 📊 **Talent Analytics Dashboard**:
  - Interactive Plotly charts: Suitability Distribution Donut, Ranked Candidate Bar Chart, and Skill Prevalence Breakdown.
- 📄 **Executive Branded PDF Dossier Generator**:
  - Instant 1-click generation of professional candidate evaluation dossiers using ReportLab.
- 🔒 **Privacy & Data Sovereignty**:
  - 100% local SQLite database persistence — no third-party data leakage.

---

## 🏗️ Architecture & Matching Engine

`mermaid
graph TD
    A[PDF / DOCX Resume] --> B[Resume Ingestion & Parser]
    B --> C[Entity & Skill Extractor]
    C --> D[(SQLite Database)]
    
    E[Job Description] --> F[Skill & Keyword Parser]
    
    C --> G[Multi-Factor Matching Engine]
    F --> G
    
    G -->|45%| H[Skill Match Score]
    G -->|35%| I[TF-IDF Semantic Similarity]
    G -->|20%| J[Context & Keyword Alignment]
    
    H & I & J --> K[Composite Score & Insights]
    K --> L[Candidate Ranking & Radar Analytics]
    K --> M[Executive PDF Dossier]
`

---

## 🚀 Installation & Quick Start

### 1. Clone the Repository
`ash
git clone https://github.com/your-username/talentlens-ai.git
cd talentlens-ai
`

### 2. Create Virtual Environment
`ash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
`

### 3. Install Dependencies
`ash
pip install -r requirements.txt
`

### 4. Launch Application
`ash
streamlit run app.py
`
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## ☁️ Cloud Deployment

### 1. 🚀 Deploy on Render (Recommended for Web Service)
Render supports background Python processes with real-time WebSockets natively.

**Option A: 1-Click Blueprint (Zero Config)**
1. Sign in to **[Render Dashboard](https://dashboard.render.com)**.
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository `Kumarshiv16/talentlens-ai`.
4. Render will automatically detect [`render.yaml`](render.yaml) and configure the build and start commands.
5. Click **Apply** to deploy!

**Option B: Manual Web Service**
1. Click **New +** > **Web Service** on Render.
2. Connect your repository.
3. Configure settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false`
4. Click **Deploy Web Service**.

---

### 2. ▲ Deploy on Vercel
Vercel is pre-configured with [`vercel.json`](vercel.json) and a dedicated serverless entrypoint ([`api/index.py`](api/index.py)):
1. Sign in to **[Vercel Dashboard](https://vercel.com)**.
2. Click **Add New...** > **Project** and import `Kumarshiv16/talentlens-ai`.
3. Keep default settings (Framework Preset: *Other*) and click **Deploy**.
4. Vercel will launch your live Cloud Gateway and Serverless API (`/api/health`).

---

### 3. 🎈 Deploy on Streamlit Community Cloud (100% Free)
1. Visit **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
2. Click **New app**, select `Kumarshiv16/talentlens-ai`, branch `main`.
3. Set **Main file path** to `app.py`.
4. Click **Deploy!**

---

### 4. 🐳 Deploy with Docker
```bash
docker build -t talentlens-ai .
docker run -p 8501:8501 talentlens-ai
```

---

## 📁 Project Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml              # Automated GitHub Actions CI pipeline
├── .streamlit/
│   └── config.toml             # Streamlit server & theme configuration
├── api/
│   └── index.py                # Vercel serverless function & gateway handler
├── database/
│   └── resumes.db              # SQLite candidate & job repository
├── uploads/                    # Local storage for uploaded documents
├── app.py                      # Main Streamlit application entrypoint
├── database.py                 # SQLite database schema and persistence layer
├── resume_parser.py            # PDF/DOCX parsing & 250+ skill taxonomy engine
├── matcher.py                  # Multi-factor explainable scoring algorithm
├── charts.py                   # Plotly charts & radar visualizations
├── utils.py                    # PDF dossier generator & sample data seeder
├── style.css                   # Modern dark glassmorphic styling
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition with dynamic $PORT support
├── Procfile                    # Web process entrypoint (Render/Heroku)
├── render.yaml                 # Render infrastructure-as-code blueprint
├── vercel.json                 # Vercel serverless routing configuration
├── CONTRIBUTING.md             # Developer contribution guidelines
├── LICENSE                     # MIT License
└── README.md                   # Repository documentation
```

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

---

<div align="center">
Crafted with ❤️ for modern, thoughtful hiring teams.
</div>
