import React, { useEffect, useState } from "react";
import LogsTable from "./components/LogsTable";
import "./App.css";

export default function App() {
  const [stats, setStats] = useState({
    total: 0,
    threats: 0,
    percent: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("http://localhost:8000/stats");
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Failed to fetch stats:", err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2>🛡 NeuroSentry</h2>

        <div className="stat-card">
          <span>Total Scans</span>
          <h1>{stats.total}</h1>
        </div>

        <div className="stat-card">
          <span>Threats Detected</span>
          <h1 style={{ color: "#ff4d4d" }}>{stats.threats}</h1>
        </div>

        <div className="stat-card">
          <span>Threat %</span>
          <h1 style={{ color: "#fbbf24" }}>{stats.percent}%</h1>
        </div>
      </div>

      <div className="main-panel">
        <h2>🔴 Live Threat Feed</h2>
        <LogsTable />
      </div>
    </div>
  );
}
