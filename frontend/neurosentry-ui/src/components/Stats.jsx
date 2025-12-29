import { useEffect, useState } from "react";
import { fetchStats } from "../services/api";

export default function Stats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats().then(setStats);
  }, []);

  if (!stats) return null;

  const box = {
    border: "1px solid cyan",
    padding: "16px",
    borderRadius: "10px",
    background: "rgba(0,0,0,0.85)",
    color: "cyan",
    marginBottom: "12px"
  };

  return (
    <div>
      <div style={box}>
        <h3>Total Scans</h3>
        <h1>{stats.total_scans}</h1>
      </div>

      <div style={box}>
        <h3>Threats</h3>
        <h1>{stats.threats}</h1>
      </div>

      <div style={box}>
        <h3>Threat %</h3>
        <h1>{stats.threat_rate}%</h1>
      </div>
    </div>
  );
}
