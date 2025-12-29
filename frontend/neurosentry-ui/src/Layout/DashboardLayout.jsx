import MatrixRain from "../components/MatrixRain";
import Stats from "../components/Stats";
import LogsTable from "../components/LogsTable";

export default function DashboardLayout() {
  return (
    <div style={{ height: "100vh", background: "black" }}>
      <MatrixRain />

      <div
        style={{
          position: "absolute",
          inset: 20,
          display: "grid",
          gridTemplateColumns: "1fr 2fr",
          gap: "20px",
          zIndex: 5
        }}
      >
        <Stats />
        <LogsTable />
      </div>
    </div>
  );
}
