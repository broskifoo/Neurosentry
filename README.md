NeuroSentry – AI‑Powered Cyber Threat Detection

NeuroSentry is a real‑time, AI‑powered threat detection system that monitors host activity, extracts rich behavioral features, and uses machine learning models to identify suspicious processes and attacks on the fly. It is designed for security analysts, blue‑teamers, and researchers who want an end‑to‑end, code‑first SOC lab.
Features

    End‑to‑end pipeline – from raw system/audit logs to real‑time prediction and alerting.

    Multi‑component architecture – backend collector, feature extractor, ML predictor, and a modern web dashboard.

    Configurable data sources – supports system logs, audit trails, and custom traces via pluggable parsers.

    Interpretable ML – exposes model metrics, feature importance, and SHAP‑style summaries to understand decisions.

    Frontend dashboard – React‑based UI (NeuroSentry‑UI) for live threats, historical logs, and statistics.

    Production‑ready layout – clear separation of backend/, core/, config/, and frontend/ for deployment.
Project Structure

Adjust names if any folder differs in your repo.

text
NeuroSentry/
├── backend/                 # API server, real‑time prediction endpoints
├── core/                    # Feature extraction, models, utilities
├── config/                  # YAML/XML configs for pipelines and log sources
├── frontend/                # React + Vite web UI (NeuroSentry‑UI)
├── .gitignore
├── main.py                  # Entry point for backend / orchestration
├── init_db.py               # Database initialization
├── real_predictor.py        # Online inference engine
├── parse_audit_logs.py      # Log parsing utilities
├── generate_dataset.py      # Offline dataset generation scripts
├── metrics.txt              # Model evaluation results
└── README.md                # You are here

Getting Started
Prerequisites

    Python 3.10+

    Node.js 18+ and npm (for the frontend)

    Git and a Unix‑like OS (Linux recommended)

    A virtual environment tool (e.g., venv or conda)
Backend Setup

bash
# Clone the repository
git clone https://github.com/broskifoo/Neurosentry.git
cd Neurosentry

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize database (if applicable)
python init_db.py

# Run backend server
python main.py

By default the backend exposes a REST API (and optionally WebSocket endpoints) for the frontend dashboard and other clients.
Frontend (UI) Setup

bash
cd frontend/neurosentry-ui

# Install dependencies
npm install

# Start development server
npm run dev

The UI will be available on the port shown in the terminal (often http://localhost:5173 or similar). You can customize API URLs in the frontend config if needed.
Usage

   1) Configure data sources

        Edit configuration files under config/ to point to your log sources (audit logs, Sysmon, etc.).

        Enable/disable features and model settings as needed.

    2) Collect and parse logs

        Use scripts like parse_audit_logs.py or dedicated collectors in backend/ / core/ to ingest raw events.

        Optionally run generate_dataset.py to build offline datasets for training.


    3) Train or load models

        Use real_predictor.py and related notebooks/scripts to train models on your datasets.

        Save trained models and update paths in config files.

    4) Run real‑time detection

        Start the backend (python main.py) to stream events through the feature pipeline and model.

        Open the frontend to view live alerts, log tables, and statistics.

Datasets and Large Files

Large trace/log files (for example dynamic_trace.jsonl, malicious_traces.jsonl, and other multi‑hundred‑MB artifacts) are not stored in this repository to keep the project lightweight and within GitHub limits.

You can:

    Generate your own traces by running the collectors.

    Plug in your own security datasets by adjusting paths and schemas in config/ and parsing scripts.

For serious workloads, consider storing raw logs in an external data lake or using Git LFS.
Configuration

Key configuration areas:

    config/ – pipeline, data source, and model configuration (YAML/XML).

    sysmon_config.xml, perfect_config.xml, etc. – example configurations for host telemetry.

    Environment variables – for ports, database URLs, and secrets (document or .env usage if you have it).

Update these to match your environment before running in production.
Roadmap / Ideas

You can keep or trim this section:

    Add support for more log sources (cloud, containers, network flows).

    Integrate with SIEM / SOAR platforms via webhooks or APIs.

    Add role‑based access control to the dashboard.

    Package backend as a Docker image and ship a docker-compose setup.

Limitations & Disclaimer

NeuroSentry is a research and educational project. It is not a drop‑in replacement for a commercial EDR/XDR product:

    Detection quality depends heavily on your training data and configuration.

    Always test in an isolated lab before deploying to production.

    Use at your own risk; the authors are not responsible for misuse.

        

