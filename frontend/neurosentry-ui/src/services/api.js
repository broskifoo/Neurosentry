const API = "http://localhost:8000";

export const fetchStats = async () => {
  const res = await fetch(`${API}/stats`);
  return res.json();
};

export const fetchLogs = async () => {
  const res = await fetch(`${API}/alerts`);
  return res.json();
};
