import { useEffect, useState } from "react";
import { fetchLogs } from "../services/api";

export default function Dashboard() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchLogs().then(setLogs);

    const id = setInterval(() => {
      fetchLogs().then(setLogs);
    }, 4000);

    return () => clearInterval(id);
  }, []);

  const total = logs.length;
  const threats = logs.filter(l => l.is_threat === 1).length;
  const threatRate = total ? ((threats / total) * 100).toFixed(2) : 0;

  return (
    <div style={{ marginTop: "300px", padding: "20px" }}>

      {/* STATS */}
      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <Stat title="Total Scans" value={total} />
        <Stat title="Threats Detected" value={threats} />
        <Stat title="Threat Rate" value={`${threatRate}%`} />
      </div>

      {/* TABLE */}
      <div style={{
        maxHeight: "300px",
        overflowY: "auto",
        border: "1px solid #00ffff"
      }}>
        <table width="100%">
          <thead>
            <tr>
              <th>Time</th>
              <th>Threat</th>
              <th>Confidence</th>
              <th>Severity</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l, i) => (
              <tr key={i}>
                <td>{l.timestamp}</td>
                <td>{l.is_threat ? "YES" : "NO"}</td>
                <td>{l.confidence}</td>
                <td>{l.ai.severity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div style={{
      border: "1px solid #00ffff",
      padding: "15px",
      width: "200px",
      background: "rgba(0,0,0,0.6)"
    }}>
      <h4>{title}</h4>
      <h2>{value}</h2>
    </div>
  );
}
