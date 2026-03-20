# Neurosentry

Neurosentry is a real-time malware detection and threat intelligence system that leverages machine learning and artificial intelligence to monitor, analyze, and explain system-level threats. It provides a comprehensive suite of tools for log ingestion, automated analysis, and visual monitoring.

## Core Components

The system is organized into several distinct architectural layers:

### 1. TCP Log Collector
The collector is a high-performance TCP server designed for efficient log ingestion.
- **Asynchronous Processing**: Uses a thread-per-connection model for reading and a dedicated writer thread for disk I/O.
- **Log Enrichment**: Automatically adds ISO8601 UTC timestamps to incoming records.
- **Storage**: Outputs logs in newline-delimited JSON (JSONL) format for easy parsing and analysis.

### 2. Analysis Backend (FastAPI)
The backend serves as the brain of the system, providing REST API endpoints for threat scanning and AI insights.
- **Predictive Scanning**: Uses a trained machine learning model to analyze Sysmon logs and identify malicious behavior patterns.
- **AI Explainer**: Integrates with large language models to provide detailed explanations of cybersecurity terms and identified threats.
- **Extensible API**: Offers endpoints for both automated system scans and interactive terminology explanations.

### 3. SOC Dashboard (Streamlit)
A professional Security Operations Center (SOC) interface for real-time monitoring.
- **Visual Analytics**: Displays live threat feeds, detection rates, and historical scan data.
- **Hacker-Centric Design**: Includes a theme-consistent interface with dynamic visualizations and a terminal-style status feed.
- **Threat Deep-Dives**: Provides detailed breakdowns of detected events, including severity levels and confidence scores.

### 4. React Frontend (NeuroSentry-UI)
A modern web dashboard built with React and Vite for advanced data visualization.
- **Live Threats**: Interactive view of ongoing system events and alerts.
- **Historical Analysis**: Broad access to past scan logs and detection statistics.
- **Modular Components**: Organized for easy extension and customization.

## Key Features

- **Real-time Monitoring**: Continuous collection and analysis of system events.
- **Machine Learning Detection**: Identifies threats with calculated confidence scores using a Random Forest based model.
- **AI-Driven Context**: Explains complex cybersecurity threats in plain language using AI.
- **Multi-Frontend Support**: Offers both a lightweight Streamlit dashboard and a robust React-based UI.
- **Historical Tracking**: Stores all scan results and findings in a local SQLite database for auditing and review.

## Technology Stack

- **Backend**: Python, FastAPI, Uvicorn, Pydantic
- **Dashboard**: Streamlit, Pandas, SQLite
- **React UI**: Vite, React, Node.js
- **Machine Learning**: Scikit-learn, Joblib
- **Collector**: Python Socket programming, Multi-threading
- **Manual Tool**: HTML5, Vanilla CSS, JavaScript

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm (for the React UI)
- Windows (for Sysmon ingestion) or any OS (for analysis and dashboard)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/broskifoo/Neurosentry.git
   cd Neurosentry
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn streamlit pandas scikit-learn joblib requests sqlite3
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Setup the React UI:
   ```bash
   cd frontend/neurosentry-ui
   npm install
   ```

## Usage

### 1. Start the Collector
Run the TCP collector to begin receiving logs:
```bash
python collector.py --port 9999 --log-file data/dynamic_trace.jsonl
```

### 2. Launch the Analysis Backend
Start the FastAPI server:
```bash
python main.py
```

### 3. Run the SOC Dashboard (Streamlit)
```bash
streamlit run app.py
```

### 4. Start the React Frontend
```bash
cd frontend/neurosentry-ui
npm run dev
```

## Configuration
Sysmon configuration files are provided in the root directory:
- `sysmon_config.xml`: Standard monitoring configuration.
- `sysmonconfig-export.xml`: Comprehensive configuration export.
