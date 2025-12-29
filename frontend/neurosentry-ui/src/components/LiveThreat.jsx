import { useEffect, useState } from "react";
import { fetchLatest } from "../services/api";

export default function LiveThreat() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchLatest().then(setData);

    const id = setInterval(() => {
      fetchLatest().then(setData);
    }, 3000);

    return () => clearInterval(id);
  }, []);

  if (!data) return null;

  return (
    <div style={{
      border: "1px solid #00ffff",
      padding: "20px",
      width: "420px",
      background: "rgba(0,0,0,0.7)",
      borderRadius: "10px"
    }}>
      <h2>{data.ai.title}</h2>
      <p><b>Severity:</b> {data.ai.severity}</p>
      <p><b>Confidence:</b> {data.confidence}</p>
      <p>{data.ai.explanation}</p>

      <pre style={{ fontSize: "12px", opacity: 0.7 }}>
        {data.ai.window}
      </pre>
    </div>
  );
}

