"""Vercel Serverless Function entrypoint for TalentLens AI."""
import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/api/health", "/health"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "TalentLens AI Serverless Gateway",
                "version": "2.0.0",
                "platform": "Vercel",
                "engine": "Scikit-Learn Multi-Factor TF-IDF Matching Engine",
            }
            self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))
            return

        # Default Landing & Gateway page for Vercel
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TalentLens AI - Enterprise Recruitment Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(circle at top center, #131d31 0%, #080c14 100%);
            color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .card {
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            max-width: 680px;
            width: 100%;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(59, 130, 246, 0.15);
            text-align: center;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.35);
            color: #60a5fa;
            font-size: 12px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 30%, #93c5fd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
        }
        p.subtitle {
            color: #94a3b8;
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 28px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 32px;
            text-align: left;
        }
        .stat-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 14px;
        }
        .stat-box h3 {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .stat-box p {
            font-size: 16px;
            font-weight: 700;
            color: #38bdf8;
        }
        .actions {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff;
            box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 24px -5px rgba(37, 99, 235, 0.6);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.06);
            color: #cbd5e1;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }
        .note {
            margin-top: 24px;
            font-size: 12px;
            color: #64748b;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">● Cloud Deployment Live</div>
        <h1>TalentLens AI</h1>
        <p class="subtitle">
            Enterprise AI resume screening & candidate intelligence platform powered by multi-factor explainable machine learning.
        </p>

        <div class="grid">
            <div class="stat-box">
                <h3>Match Engine</h3>
                <p>Multi-Factor AI</p>
            </div>
            <div class="stat-box">
                <h3>Skill Taxonomy</h3>
                <p>250+ Categories</p>
            </div>
            <div class="stat-box">
                <h3>Vercel Gateway</h3>
                <p>Active</p>
            </div>
        </div>

        <div class="actions">
            <a href="https://share.streamlit.io" target="_blank" class="btn btn-primary">
                Open Full Interactive UI ↗
            </a>
            <a href="/api/health" class="btn btn-secondary">
                View Serverless API Health ↗
            </a>
        </div>

        <p class="note">
            💡 The full interactive Streamlit UI runs with persistent WebSockets on Render or Streamlit Cloud, while Vercel serves serverless edge APIs and gateways.
        </p>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))
