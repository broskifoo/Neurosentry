import React, { useEffect, useState } from "react";
import "./LogsTable.css";

export default function LogsTable() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch("http://localhost:8000/logs");
        const data = await res.json();
        setLogs(data.reverse());
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="logs-container">
      <table>
        <thead>
          <tr>
            <th style={{ width: "15%" }}>Time</th>
            <th style={{ width: "12%" }}>Threat</th>
            <th style={{ width: "13%" }}>Confidence</th>
            <th style={{ width: "60%" }}>AI Explanation</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan="4" style={{ textAlign: "center", color: "#64748b" }}>
                No logs available. Waiting for events...
              </td>
            </tr>
          ) : (
            logs.map((log, i) => (
              <tr key={i}>
                <td>{new Date(log.timestamp).toLocaleTimeString()}</td>
                <td className={log.is_threat ? "threat" : "safe"}>
                  {log.is_threat ? "⚠ THREAT" : "✓ Benign"}
                </td>
                <td>{(log.confidence * 100).toFixed(1)}%</td>
                <td className="explanation">{log.ai_explanation}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
