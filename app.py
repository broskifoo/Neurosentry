import streamlit as st
import sqlite3
import json
import pandas as pd
from pathlib import Path

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="NeuroSentry SOC",
    page_icon="🛡️",
    layout="wide"
)

DB_PATH = Path("neurosentry.db")

# ===============================
# MATRIX BACKGROUND
# ===============================
st.markdown("""
<canvas id="matrix"></canvas>

<script>
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = "01";
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function draw() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#00f7ff";
  ctx.font = fontSize + "px monospace";

  for (let i = 0; i < drops.length; i++) {
    const text = letters[Math.floor(Math.random() * letters.length)];
    ctx.fillText(text, i * fontSize, drops[i] * fontSize);

    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975)
      drops[i] = 0;

    drops[i]++;
  }
}

setInterval(draw, 33);

window.onresize = () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
};
</script>

<style>
#matrix {
  position: fixed;
  top: 0;
  left: 0;
  z-index: -1;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# GLOBAL CSS
# ===============================
st.markdown("""
<style>
html, body, [class*="css"] {
    background: transparent !important;
    color: #e5e7eb !important;
}

section.main > div {
    background: transparent !important;
    z-index: 2;
}

h1, h2, h3 {
    color: #00f7ff !important;
}

.card {
    background: rgba(2, 6, 23, 0.85);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0,247,255,0.25);
    margin-bottom: 15px;
}

.sev-Low { color: #00ff9c; }
.sev-Medium { color: #facc15; }
.sev-High { color: #fb7185; }
.sev-Critical { color: #c084fc; }

.feed-row {
    padding: 10px;
    border-bottom: 1px solid #1f2937;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# HACKER TERMINAL
# ===============================
st.markdown("""
<div id="terminal">
  <pre id="terminal-text"></pre>
</div>

<script>
const lines = [
  "root@neurosentry:~# loading kernel hooks",
  "root@neurosentry:~# monitoring auditd",
  "root@neurosentry:~# intercepting execve",
  "root@neurosentry:~# anomaly detected",
  "root@neurosentry:~# correlating events",
  "root@neurosentry:~# alert dispatched"
];

let i = 0;
function typeLine() {
  const el = document.getElementById("terminal-text");
  if (i < lines.length) {
    el.innerHTML += lines[i] + "\\n";
    i++;
    setTimeout(typeLine, 900);
  } else {
    el.innerHTML = "";
    i = 0;
    setTimeout(typeLine, 1500);
  }
}
typeLine();
</script>

<style>
#terminal {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 420px;
  height: 220px;
  background: rgba(0,0,0,0.85);
  border: 1px solid #00f7ff;
  padding: 10px;
  font-family: monospace;
  font-size: 12px;
  color: #00ff9c;
  overflow: hidden;
  z-index: 1;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("""
<h1>🛡️ NeuroSentry</h1>
<p style="color:#9ca3af;">Real-Time Malware Detection & AI Threat Intelligence</p>
<hr>
""", unsafe_allow_html=True)

# ===============================
# DB LOAD
# ===============================
if not DB_PATH.exists():
    st.error("Database not found. Start predictor first.")
    st.stop()

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM scan_history ORDER BY scan_timestamp DESC",
        conn
    )
    conn.close()
    return df

df = load_data()

# ===============================
# METRICS
# ===============================
total = len(df)
threats = df[df["is_threat"] == 1].shape[0]
rate = (threats / total * 100) if total else 0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='card'><h3>Total Scans</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='card'><h3>Threats Detected</h3><h2>{threats}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='card'><h3>Threat Rate</h3><h2>{rate:.1f}%</h2></div>", unsafe_allow_html=True)

st.divider()

# ===============================
# LIVE FEED
# ===============================
st.subheader("🚨 Live Threat Feed")

for _, row in df.head(12).iterrows():
    conf = row["confidence"]
    conf_str = f"{conf:.2f}" if conf is not None else "N/A"
    findings = json.loads(row["findings_json"]) if row["findings_json"] else {}
    severity = findings.get("severity", "Medium")

    st.markdown(f"""
    <div class="feed-row">
        <b>{row["scan_timestamp"]}</b> —
        <span class="sev-{severity}">{severity}</span>
        | Confidence: {conf_str}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===============================
# AI EXPLAINER
# ===============================
st.subheader("🧠 AI Threat Analysis")

if not df.empty:
    latest = df.iloc[0]
    findings = json.loads(latest["findings_json"]) if latest["findings_json"] else {}

    st.markdown(f"""
    <div class="card">
        <h3>{findings.get("title", "Suspicious Behaviour Detected")}</h3>
        <p><b>Severity:</b> {findings.get("severity", "Unknown")}</p>
        <p>{latest["explanation"]}</p>
        <p><b>Event Window:</b> {findings.get("window", "N/A")}</p>
    </div>
    """, unsafe_allow_html=True)
