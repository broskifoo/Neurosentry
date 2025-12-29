import { useEffect, useState } from "react";
import { fetchLatest } from "../services/api";

export default function ThreatExplanation() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchLatest().then(setData);
  }, []);

  if (!data) return null;

  return (
    <div style={{
      border: "1px solid #00ffff",
      padding: "16px",
      borderRadius: "10px",
      marginTop: "20px",
      color: "#00ffff"
    }}>
      <h3>AI Threat Explanation</h3>

      <p><b>Threat:</b> {data.is_threat ? "YES" : "NO"}</p>
      <p><b>Confidence:</b> {data.confidence}</p>

      <p style={{ marginTop: "10px" }}>
        {data.ai?.explanation || "No explanation available"}
      </p>
    </div>
  );
}
