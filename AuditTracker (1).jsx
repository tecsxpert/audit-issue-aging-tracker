import { useState, useEffect, useRef } from "react";

// ── Seed Data — Smart Farming Solutions (ESP32-CAM · NodeMCU · Python · MobileNetV2) ──
const SEED_ISSUES = [
  // ESP32-CAM
  { id: "SFS-001", title: "ESP32-CAM – Image Capture Fails Under Low Light Conditions", owner: "Ravi K.", category: "ESP32-CAM", status: "Overdue", age: 91, risk: "Critical", remDate: "2026-02-10" },
  { id: "SFS-002", title: "ESP32-CAM – Wi-Fi Reconnection Loop After Power Cycle", owner: "Priya T.", category: "ESP32-CAM", status: "Open", age: 44, risk: "High", remDate: "2026-05-22" },
  { id: "SFS-003", title: "ESP32-CAM – JPEG Frame Corruption at 1600×1200 Resolution", owner: "Ravi K.", category: "ESP32-CAM", status: "In Review", age: 27, risk: "High", remDate: "2026-06-02" },
  { id: "SFS-004", title: "ESP32-CAM – OV2640 Lens Fogging in High-Humidity Field Conditions", owner: "Meena R.", category: "ESP32-CAM", status: "Open", age: 13, risk: "Medium", remDate: "2026-06-20" },

  // NodeMCU Sensors
  { id: "SFS-005", title: "NodeMCU – DHT11 Temperature Readings Drift ±4°C After 6 Hours", owner: "Suresh P.", category: "NodeMCU & Sensors", status: "Overdue", age: 103, risk: "Critical", remDate: "2026-01-28" },
  { id: "SFS-006", title: "NodeMCU – Capacitive Soil Moisture Sensor Returns 0% When Dry", owner: "Ananya M.", category: "NodeMCU & Sensors", status: "Open", age: 38, risk: "High", remDate: "2026-05-28" },
  { id: "SFS-007", title: "NodeMCU – Serial Data Drops During Simultaneous Multi-Sensor Read", owner: "Suresh P.", category: "NodeMCU & Sensors", status: "In Review", age: 21, risk: "Medium", remDate: "2026-06-10" },
  { id: "SFS-008", title: "NodeMCU – Flash Memory Wear from Continuous Sensor Logging", owner: "Kiran J.", category: "NodeMCU & Sensors", status: "Open", age: 9, risk: "Low", remDate: "2026-06-28" },

  // Python Backend
  { id: "SFS-009", title: "Python Server – Sensor Data Ingestion Drops Packets Under Load", owner: "Deepa N.", category: "Python Backend", status: "Overdue", age: 78, risk: "Critical", remDate: "2026-03-05" },
  { id: "SFS-010", title: "Python – MQTT Subscribe Callback Blocks Main Thread (Deadlock)", owner: "Arjun K.", category: "Python Backend", status: "Open", age: 33, risk: "High", remDate: "2026-05-30" },
  { id: "SFS-011", title: "Python – Serial Port Not Released on Crash (NodeMCU Disconnect)", owner: "Deepa N.", category: "Python Backend", status: "In Review", age: 18, risk: "Medium", remDate: "2026-06-14" },
  { id: "SFS-012", title: "Python – No Authentication on Local REST API Endpoints", owner: "Arjun K.", category: "Python Backend", status: "Overdue", age: 86, risk: "Critical", remDate: "2026-02-20" },

  // MobileNetV2 Disease Detection
  { id: "SFS-013", title: "MobileNetV2 – Crop Disease False Positive Rate 34% on Yellowing Leaves", owner: "Divya P.", category: "MobileNetV2 Disease Detection", status: "Open", age: 47, risk: "High", remDate: "2026-05-20" },
  { id: "SFS-014", title: "MobileNetV2 – Model Confidence <50% for Early-Stage Blight Detection", owner: "Divya P.", category: "MobileNetV2 Disease Detection", status: "In Review", age: 31, risk: "High", remDate: "2026-06-01" },
  { id: "SFS-015", title: "MobileNetV2 – Inference Timeout When ESP32-CAM Image is Blurry", owner: "Vijay L.", category: "MobileNetV2 Disease Detection", status: "Closed", age: 62, risk: "Medium", remDate: "2026-03-18" },
  { id: "SFS-016", title: "MobileNetV2 – Training Dataset Lacks Night-Time Crop Images", owner: "Vijay L.", category: "MobileNetV2 Disease Detection", status: "Open", age: 11, risk: "Medium", remDate: "2026-06-22" },

  // CSV Crop Recommendation
  { id: "SFS-017", title: "CSV Recommender – Incorrect Crop Suggested for pH 4.5–5.0 Soil Range", owner: "Lakshmi D.", category: "CSV Crop Recommendation", status: "Overdue", age: 69, risk: "Critical", remDate: "2026-03-12" },
  { id: "SFS-018", title: "CSV Recommender – No Fallback When Sensor N/P/K Values Are Null", owner: "Lakshmi D.", category: "CSV Crop Recommendation", status: "Open", age: 24, risk: "High", remDate: "2026-06-08" },
  { id: "SFS-019", title: "CSV Recommender – Duplicate Crop Entries Causing Ambiguous Results", owner: "Sneha C.", category: "CSV Crop Recommendation", status: "Closed", age: 55, risk: "Low", remDate: "2026-03-28" },

  // Motor Control
  { id: "SFS-020", title: "Motor Control – Remote OFF Command Ignored When Wi-Fi Signal Weak", owner: "Mohan R.", category: "Motor Control", status: "Overdue", age: 94, risk: "Critical", remDate: "2026-02-01" },
  { id: "SFS-021", title: "Motor Control – Relay Module Stays ON After NodeMCU Reboot", owner: "Mohan R.", category: "Motor Control", status: "Open", age: 41, risk: "High", remDate: "2026-05-25" },
  { id: "SFS-022", title: "Motor Control – No Dry-Run Protection When Water Tank is Empty", owner: "Ramesh V.", category: "Motor Control", status: "In Review", age: 29, risk: "High", remDate: "2026-06-04" },
  { id: "SFS-023", title: "Motor Control – Manual Override Bypasses Automation Schedule Silently", owner: "Ramesh V.", category: "Motor Control", status: "Open", age: 16, risk: "Medium", remDate: "2026-06-18" },

  // Moisture Automation
  { id: "SFS-024", title: "Moisture Automation – Motor Triggers at Wrong Threshold After Calibration Reset", owner: "Pooja S.", category: "Moisture Automation", status: "Overdue", age: 82, risk: "Critical", remDate: "2026-02-25" },
  { id: "SFS-025", title: "Moisture Automation – Rapid ON/OFF Cycling When Sensor Near Threshold", owner: "Pooja S.", category: "Moisture Automation", status: "Open", age: 36, risk: "High", remDate: "2026-05-26" },
  { id: "SFS-026", title: "Moisture Automation – No Hysteresis Logic Implemented in NodeMCU Firmware", owner: "Nikhil G.", category: "Moisture Automation", status: "In Review", age: 22, risk: "High", remDate: "2026-06-08" },
  { id: "SFS-027", title: "Moisture Automation – Automation Disabled Silently When Sensor Reads Error", owner: "Nikhil G.", category: "Moisture Automation", status: "Open", age: 8, risk: "Medium", remDate: "2026-06-30" },
];

const SEED_LOG = [
  { id: 1, user: "Mohan R.", action: "escalated issue", target: "Motor Remote OFF Command Ignored (94d overdue)", time: "09:41 AM", icon: "⚑", color: "#993C1D", bg: "#fee2e2" },
  { id: 2, user: "Vijay L.", action: "closed issue", target: "MobileNetV2 – Inference Timeout on Blurry Image", time: "09:15 AM", icon: "✓", color: "#3B6D11", bg: "#dcfce7" },
  { id: 3, user: "System", action: "escalation alert sent for", target: "Python API – No Auth on REST Endpoints (86d overdue)", time: "08:00 AM", icon: "⚑", color: "#993C1D", bg: "#fee2e2" },
  { id: 4, user: "Divya P.", action: "updated status → In Review", target: "MobileNetV2 – Low Confidence on Early-Stage Blight", time: "Yesterday", icon: "✎", color: "#1B4F8A", bg: "#dbeafe" },
  { id: 5, user: "Pooja S.", action: "opened issue", target: "Moisture Automation – Wrong Threshold After Calibration", time: "Yesterday", icon: "+", color: "#3B6D11", bg: "#dcfce7" },
  { id: 6, user: "Sneha C.", action: "closed issue", target: "CSV Recommender – Duplicate Crop Entries", time: "2 days ago", icon: "✓", color: "#3B6D11", bg: "#dcfce7" },
];

// ── Helpers ────────────────────────────────────────────────────────────────
const STATUS_STYLES = {
  Overdue:   { bg: "#fee2e2", color: "#991b1b", dot: "#ef4444" },
  Open:      { bg: "#fef9c3", color: "#854d0e", dot: "#eab308" },
  "In Review": { bg: "#dbeafe", color: "#1e40af", dot: "#3b82f6" },
  Closed:    { bg: "#dcfce7", color: "#166534", dot: "#22c55e" },
};

const RISK_STYLES = {
  Critical: { bg: "#fee2e2", color: "#991b1b" },
  High:     { bg: "#ffedd5", color: "#9a3412" },
  Medium:   { bg: "#fef9c3", color: "#854d0e" },
  Low:      { bg: "#dcfce7", color: "#166534" },
};

function Badge({ label, styles }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      fontSize: 11, fontWeight: 600, padding: "3px 9px",
      borderRadius: 20, background: styles.bg, color: styles.color,
      whiteSpace: "nowrap"
    }}>
      {styles.dot && <span style={{ width: 6, height: 6, borderRadius: "50%", background: styles.dot, display: "inline-block" }} />}
      {label}
    </span>
  );
}

function AgeBar({ age }) {
  const pct = Math.min((age / 120) * 100, 100);
  const color = age > 90 ? "#ef4444" : age > 60 ? "#f97316" : age > 30 ? "#eab308" : "#3b82f6";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ width: 60, height: 5, background: "#f1f5f9", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>{age}d</span>
    </div>
  );
}

function KpiCard({ label, value, sub, valueColor, animate }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    if (!animate) { setDisplay(value); return; }
    let start = 0;
    const step = Math.ceil(value / 30);
    const t = setInterval(() => {
      start += step;
      if (start >= value) { setDisplay(value); clearInterval(t); }
      else setDisplay(start);
    }, 30);
    return () => clearInterval(t);
  }, [value]);

  return (
    <div style={{
      background: "#fff", border: "0.5px solid #e2e8f0",
      borderRadius: 12, padding: "18px 20px",
      transition: "box-shadow 0.2s",
    }}
      onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 20px rgba(27,79,138,0.1)"}
      onMouseLeave={e => e.currentTarget.style.boxShadow = "none"}
    >
      <div style={{ fontSize: 11, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color: valueColor || "#0f172a", fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{display}</div>
      <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 6 }}>{sub}</div>
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────────────
export default function App() {
  const [issues, setIssues] = useState(SEED_ISSUES);
  const [log, setLog] = useState(SEED_LOG);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("dashboard");
  const [form, setForm] = useState({ title: "", owner: "", category: "ESP32-CAM", risk: "High", status: "Open", remDate: "" });
  const [toast, setToast] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiReport, setAiReport] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const nextId = useRef(28);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const filteredIssues = issues.filter(i => {
    const matchStatus = filter === "all" || i.status === filter;
    const matchSearch = i.title.toLowerCase().includes(search.toLowerCase()) ||
      i.owner.toLowerCase().includes(search.toLowerCase()) ||
      i.id.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const kpis = {
    total: issues.length,
    overdue: issues.filter(i => i.status === "Overdue").length,
    avgAge: Math.round(issues.filter(i => i.status !== "Closed").reduce((s, i) => s + i.age, 0) /
      Math.max(issues.filter(i => i.status !== "Closed").length, 1)),
    closed: issues.filter(i => i.status === "Closed").length,
  };

  const ageBuckets = [
    { label: "0–15d",  count: issues.filter(i => i.age <= 15).length,   color: "#3b82f6" },
    { label: "16–30d", count: issues.filter(i => i.age > 15 && i.age <= 30).length, color: "#3b82f6" },
    { label: "31–60d", count: issues.filter(i => i.age > 30 && i.age <= 60).length, color: "#f97316" },
    { label: "61–90d", count: issues.filter(i => i.age > 60 && i.age <= 90).length, color: "#f97316" },
    { label: "90d+",   count: issues.filter(i => i.age > 90).length,    color: "#ef4444" },
  ];
  const maxBucket = Math.max(...ageBuckets.map(b => b.count), 1);

  const createIssue = () => {
    if (!form.title.trim() || !form.owner.trim()) {
      showToast("Title and Owner are required.", "error"); return;
    }
    const id = `SFS-${String(nextId.current).padStart(3, "0")}`;
    nextId.current++;
    const newIssue = { id, ...form, age: 0, remDate: form.remDate || "2026-06-30" };
    setIssues(prev => [newIssue, ...prev]);
    setLog(prev => [{ id: Date.now(), user: form.owner, action: "created issue", target: form.title, time: "Just now", icon: "+", color: "#3B6D11", bg: "#dcfce7" }, ...prev]);
    setForm({ title: "", owner: "", category: "ESP32-CAM", risk: "High", status: "Open", remDate: "" });
    showToast(`Issue ${id} created successfully!`);
    setActiveTab("issues");
  };

  const closeIssue = (id) => {
    setIssues(prev => prev.map(i => i.id === id ? { ...i, status: "Closed" } : i));
    const iss = issues.find(i => i.id === id);
    setLog(prev => [{ id: Date.now(), user: "You", action: "closed issue", target: iss.title, time: "Just now", icon: "✓", color: "#3B6D11", bg: "#dcfce7" }, ...prev]);
    showToast(`${id} marked as Closed.`);
    setSelectedIssue(null);
  };

  const generateAiReport = async () => {
    setAiLoading(true);
    setAiReport(null);
    await new Promise(r => setTimeout(r, 1800));
    setAiReport({
      summary: `${kpis.overdue} issues are critically overdue across your smart farming stack. The most urgent risks are: unauthenticated Python REST endpoints (86d), motor relay staying ON after NodeMCU reboot (94d), and wrong moisture threshold triggering motor post-calibration reset (82d). Average open issue age is ${kpis.avgAge} days across ${kpis.total} issues.`,
      recommendations: [
        { priority: "HIGH", text: "Add API key or token auth to all Python REST endpoints immediately — currently any device on the local network can trigger motor control or read sensor data." },
        { priority: "HIGH", text: "Implement a safe-state default in NodeMCU firmware so the relay resets to OFF on every boot, preventing unintended motor run after power loss." },
        { priority: "HIGH", text: "Add hysteresis logic to moisture automation — define separate ON threshold (e.g. <30%) and OFF threshold (e.g. >45%) to stop rapid relay cycling near the boundary." },
        { priority: "MED",  text: "Retrain MobileNetV2 with night-time and early-stage disease images to reduce the 34% false positive rate and improve sub-50% confidence scores on blight." },
        { priority: "LOW",  text: "Fix CSV crop recommender null-handling for missing N/P/K sensor values and remove duplicate crop entries causing ambiguous recommendations." },
      ],
    });
    setAiLoading(false);
  };

  const exportCsv = () => {
    const rows = [["ID","Title","Owner","Category","Status","Age (days)","Risk","Remediation Date"]];
    issues.forEach(i => rows.push([i.id, i.title, i.owner, i.category, i.status, i.age, i.risk, i.remDate]));
    const csv = rows.map(r => r.join(",")).join("\n");
    const a = document.createElement("a"); a.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csv);
    a.download = "audit_issues.csv"; a.click();
    showToast("CSV exported successfully!");
  };

  const NAV_TABS = [
    { id: "dashboard", label: "Dashboard" },
    { id: "issues",    label: `Issues (${issues.length})` },
    { id: "create",    label: "Create Issue" },
    { id: "log",       label: "Audit Log" },
  ];

  const panelStyle = {
    background: "#fff", border: "0.5px solid #e2e8f0",
    borderRadius: 12, overflow: "hidden",
  };

  const btnPrimary = {
    background: "#1B4F8A", color: "#fff", border: "none",
    padding: "9px 20px", borderRadius: 8,
    fontSize: 13, fontWeight: 600, cursor: "pointer",
    display: "inline-flex", alignItems: "center", gap: 6,
    fontFamily: "inherit", transition: "opacity 0.15s",
  };

  const inputStyle = {
    background: "#f8fafc", border: "0.5px solid #cbd5e1",
    borderRadius: 8, padding: "8px 12px",
    fontSize: 13, color: "#0f172a", width: "100%",
    fontFamily: "inherit", outline: "none",
  };

  return (
    <div style={{ fontFamily: "'Syne', sans-serif", background: "#f8fafc", minHeight: "100vh", color: "#0f172a" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Topbar */}
      <div style={{ background: "#fff", borderBottom: "0.5px solid #e2e8f0", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 56, position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ background: "#1B4F8A", color: "#fff", fontSize: 10, fontWeight: 700, letterSpacing: "0.1em", padding: "4px 8px", borderRadius: 5 }}>SFS · TOOL-125</div>
          <span style={{ fontSize: 15, fontWeight: 700, color: "#0f172a" }}>Smart Farming — Audit Issue Aging Tracker</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button onClick={exportCsv} style={{ background: "transparent", border: "0.5px solid #cbd5e1", padding: "6px 14px", borderRadius: 8, fontSize: 12, cursor: "pointer", color: "#64748b", display: "flex", alignItems: "center", gap: 5, fontFamily: "inherit" }}>
            ↓ Export CSV
          </button>
          <div style={{ width: 34, height: 34, borderRadius: "50%", background: "#dbeafe", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#1e40af" }}>AD</div>
        </div>
      </div>

      {/* Nav Tabs */}
      <div style={{ background: "#fff", borderBottom: "0.5px solid #e2e8f0", padding: "0 24px", display: "flex", gap: 4 }}>
        {NAV_TABS.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
            background: "transparent", border: "none",
            padding: "12px 16px", fontSize: 13, cursor: "pointer",
            fontFamily: "inherit", fontWeight: activeTab === t.id ? 600 : 400,
            color: activeTab === t.id ? "#1B4F8A" : "#64748b",
            borderBottom: activeTab === t.id ? "2px solid #1B4F8A" : "2px solid transparent",
            transition: "color 0.15s",
          }}>{t.label}</button>
        ))}
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 24px 48px" }}>

        {/* ── Dashboard ── */}
        {activeTab === "dashboard" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14 }}>
              <KpiCard label="Total Issues" value={kpis.total} sub="all categories" animate />
              <KpiCard label="Overdue" value={kpis.overdue} sub="past remediation date" valueColor="#dc2626" animate />
              <KpiCard label="Avg Age (days)" value={kpis.avgAge} sub="open issues" animate />
              <KpiCard label="Closed" value={kpis.closed} sub="resolved & verified" valueColor="#16a34a" animate />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 16 }}>
              {/* Status breakdown */}
              <div style={panelStyle}>
                <div style={{ padding: "14px 20px", borderBottom: "0.5px solid #e2e8f0", fontWeight: 600, fontSize: 13 }}>Status Overview</div>
                <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
                  {["Overdue","Open","In Review","Closed"].map(s => {
                    const cnt = issues.filter(i => i.status === s).length;
                    const pct = Math.round((cnt / issues.length) * 100);
                    const st = STATUS_STYLES[s];
                    return (
                      <div key={s} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ width: 80, fontSize: 12, color: "#64748b", flexShrink: 0 }}>{s}</div>
                        <div style={{ flex: 1, height: 10, background: "#f1f5f9", borderRadius: 5, overflow: "hidden" }}>
                          <div style={{ width: `${pct}%`, height: "100%", background: st.dot, borderRadius: 5, transition: "width 0.8s ease" }} />
                        </div>
                        <div style={{ width: 36, fontSize: 12, color: "#64748b", textAlign: "right", fontFamily: "'DM Mono', monospace" }}>{cnt}</div>
                        <div style={{ width: 36, fontSize: 11, color: "#94a3b8", textAlign: "right", fontFamily: "'DM Mono', monospace" }}>{pct}%</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Age distribution */}
              <div style={panelStyle}>
                <div style={{ padding: "14px 20px", borderBottom: "0.5px solid #e2e8f0", fontWeight: 600, fontSize: 13 }}>Age Distribution</div>
                <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
                  {ageBuckets.map(b => (
                    <div key={b.label} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12 }}>
                      <div style={{ width: 48, color: "#64748b", flexShrink: 0, textAlign: "right" }}>{b.label}</div>
                      <div style={{ flex: 1, height: 10, background: "#f1f5f9", borderRadius: 5, overflow: "hidden" }}>
                        <div style={{ width: `${(b.count / maxBucket) * 100}%`, height: "100%", background: b.color, borderRadius: 5 }} />
                      </div>
                      <div style={{ width: 20, fontFamily: "'DM Mono',monospace", color: "#64748b" }}>{b.count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Report */}
            <div style={panelStyle}>
              <div style={{ padding: "14px 20px", borderBottom: "0.5px solid #e2e8f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#3b82f6", animation: "pulse 2s infinite" }} />
                  <span style={{ fontWeight: 600, fontSize: 13 }}>AI Analysis</span>
                  <span style={{ fontSize: 10, background: "#dbeafe", color: "#1e40af", padding: "2px 8px", borderRadius: 10, fontWeight: 600 }}>LLaMA-3.3-70b via Groq</span>
                </div>
                <button onClick={generateAiReport} style={{ ...btnPrimary, padding: "7px 16px", fontSize: 12 }} disabled={aiLoading}>
                  {aiLoading ? "Generating…" : "Generate Report"}
                </button>
              </div>
              <div style={{ padding: 20 }}>
                {!aiReport && !aiLoading && (
                  <div style={{ color: "#94a3b8", fontSize: 13, textAlign: "center", padding: "24px 0" }}>
                    Click "Generate Report" to get AI-powered analysis of your audit portfolio.
                  </div>
                )}
                {aiLoading && (
                  <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "20px 0" }}>
                    <div style={{ width: 20, height: 20, border: "2px solid #dbeafe", borderTop: "2px solid #1B4F8A", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                    <span style={{ fontSize: 13, color: "#64748b" }}>Analyzing {issues.length} smart farming audit records with LLaMA-3.3-70b…</span>
                  </div>
                )}
                {aiReport && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <div style={{ background: "#f8fafc", borderRadius: 8, padding: 14, fontSize: 13, color: "#334155", lineHeight: 1.6 }}>
                      <strong style={{ color: "#0f172a" }}>Summary: </strong>{aiReport.summary}
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      {aiReport.recommendations.map((r, i) => {
                        const pillStyle = r.priority === "HIGH"
                          ? { bg: "#fee2e2", color: "#991b1b" }
                          : r.priority === "MED"
                          ? { bg: "#ffedd5", color: "#9a3412" }
                          : { bg: "#dcfce7", color: "#166534" };
                        return (
                          <div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                            <span style={{ fontSize: 10, padding: "3px 8px", borderRadius: 20, fontWeight: 700, background: pillStyle.bg, color: pillStyle.color, whiteSpace: "nowrap", marginTop: 2 }}>{r.priority}</span>
                            <span style={{ fontSize: 13, color: "#475569", lineHeight: 1.5 }}>{r.text}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── Issues Table ── */}
        {activeTab === "issues" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <input
                value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search issues, owners, IDs…"
                style={{ ...inputStyle, width: 280 }}
              />
              {["all","Open","Overdue","In Review","Closed"].map(s => (
                <button key={s} onClick={() => setFilter(s)} style={{
                  padding: "7px 14px", borderRadius: 20, fontSize: 12, cursor: "pointer",
                  fontFamily: "inherit", fontWeight: filter === s ? 600 : 400,
                  background: filter === s ? "#1B4F8A" : "#fff",
                  color: filter === s ? "#fff" : "#64748b",
                  border: `0.5px solid ${filter === s ? "#1B4F8A" : "#cbd5e1"}`,
                  transition: "all 0.15s",
                }}>{s === "all" ? "All" : s}</button>
              ))}
              <span style={{ marginLeft: "auto", fontSize: 12, color: "#94a3b8" }}>{filteredIssues.length} issues</span>
            </div>

            <div style={panelStyle}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ background: "#f8fafc" }}>
                    {["ID","Issue Title","Owner","Category","Status","Age","Risk","Action"].map(h => (
                      <th key={h} style={{ padding: "11px 16px", textAlign: "left", fontWeight: 500, fontSize: 11, color: "#94a3b8", letterSpacing: "0.06em", borderBottom: "0.5px solid #e2e8f0", whiteSpace: "nowrap" }}>{h.toUpperCase()}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredIssues.map((issue, idx) => (
                    <tr key={issue.id} style={{ borderBottom: idx < filteredIssues.length - 1 ? "0.5px solid #f1f5f9" : "none", transition: "background 0.15s" }}
                      onMouseEnter={e => e.currentTarget.style.background = "#f8fafc"}
                      onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                    >
                      <td style={{ padding: "12px 16px", fontFamily: "'DM Mono',monospace", fontSize: 12, color: "#1B4F8A", fontWeight: 600 }}>{issue.id}</td>
                      <td style={{ padding: "12px 16px", maxWidth: 220 }}>
                        <div style={{ fontWeight: 500, fontSize: 13 }}>{issue.title}</div>
                        <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>{issue.category}</div>
                      </td>
                      <td style={{ padding: "12px 16px", fontSize: 12, color: "#475569" }}>{issue.owner}</td>
                      <td style={{ padding: "12px 16px", fontSize: 11, color: "#64748b" }}>{issue.category}</td>
                      <td style={{ padding: "12px 16px" }}><Badge label={issue.status} styles={STATUS_STYLES[issue.status]} /></td>
                      <td style={{ padding: "12px 16px" }}><AgeBar age={issue.age} /></td>
                      <td style={{ padding: "12px 16px" }}><Badge label={issue.risk} styles={RISK_STYLES[issue.risk]} /></td>
                      <td style={{ padding: "12px 16px" }}>
                        <div style={{ display: "flex", gap: 6 }}>
                          <button onClick={() => setSelectedIssue(issue)} style={{ background: "#f1f5f9", border: "none", padding: "5px 10px", borderRadius: 6, fontSize: 11, cursor: "pointer", color: "#475569", fontFamily: "inherit" }}>View</button>
                          {issue.status !== "Closed" && (
                            <button onClick={() => closeIssue(issue.id)} style={{ background: "#dcfce7", border: "none", padding: "5px 10px", borderRadius: 6, fontSize: 11, cursor: "pointer", color: "#166534", fontFamily: "inherit" }}>Close</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredIssues.length === 0 && (
                <div style={{ padding: "40px", textAlign: "center", color: "#94a3b8", fontSize: 13 }}>No issues found matching your filters.</div>
              )}
            </div>
          </div>
        )}

        {/* ── Create Issue ── */}
        {activeTab === "create" && (
          <div style={{ maxWidth: 640 }}>
            <div style={panelStyle}>
              <div style={{ padding: "16px 20px", borderBottom: "0.5px solid #e2e8f0", fontWeight: 600, fontSize: 14 }}>Create New Audit Issue</div>
              <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>ISSUE TITLE *</label>
                    <input style={inputStyle} value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} placeholder="e.g. Soil Sensor Accuracy Deviation" />
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>OWNER *</label>
                    <input style={inputStyle} value={form.owner} onChange={e => setForm(p => ({ ...p, owner: e.target.value }))} placeholder="Assigned to" />
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>CATEGORY</label>
                    <select style={inputStyle} value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))}>
                      {["ESP32-CAM","NodeMCU & Sensors","Python Backend","MobileNetV2 Disease Detection","CSV Crop Recommendation","Motor Control","Moisture Automation"].map(c => <option key={c}>{c}</option>)}
                    </select>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>RISK LEVEL</label>
                    <select style={inputStyle} value={form.risk} onChange={e => setForm(p => ({ ...p, risk: e.target.value }))}>
                      {["Critical","High","Medium","Low"].map(r => <option key={r}>{r}</option>)}
                    </select>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>STATUS</label>
                    <select style={inputStyle} value={form.status} onChange={e => setForm(p => ({ ...p, status: e.target.value }))}>
                      {["Open","In Review"].map(s => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    <label style={{ fontSize: 11, color: "#64748b", fontWeight: 500 }}>REMEDIATION DATE</label>
                    <input type="date" style={inputStyle} value={form.remDate} onChange={e => setForm(p => ({ ...p, remDate: e.target.value }))} />
                  </div>
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 4 }}>
                  <button onClick={() => setForm({ title: "", owner: "", category: "ESP32-CAM", risk: "High", status: "Open", remDate: "" })}
                    style={{ background: "transparent", border: "0.5px solid #cbd5e1", padding: "9px 18px", borderRadius: 8, fontSize: 13, cursor: "pointer", color: "#64748b", fontFamily: "inherit" }}>
                    Clear
                  </button>
                  <button onClick={createIssue} style={btnPrimary}>+ Create Issue</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Audit Log ── */}
        {activeTab === "log" && (
          <div style={panelStyle}>
            <div style={{ padding: "14px 20px", borderBottom: "0.5px solid #e2e8f0", fontWeight: 600, fontSize: 13 }}>Activity Log</div>
            <div>
              {log.map((entry, i) => (
                <div key={entry.id} style={{ display: "flex", gap: 14, padding: "14px 20px", borderBottom: i < log.length - 1 ? "0.5px solid #f1f5f9" : "none", alignItems: "flex-start" }}>
                  <div style={{ width: 30, height: 30, borderRadius: "50%", background: entry.bg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0, color: entry.color }}>{entry.icon}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, color: "#334155", lineHeight: 1.5 }}>
                      <strong style={{ color: "#0f172a" }}>{entry.user}</strong> {entry.action} <em style={{ color: "#1B4F8A" }}>{entry.target}</em>
                    </div>
                    <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 3, fontFamily: "'DM Mono',monospace" }}>{entry.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Issue Detail Modal */}
      {selectedIssue && (
        <div onClick={() => setSelectedIssue(null)} style={{ position: "fixed", inset: 0, background: "rgba(15,23,42,0.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200, padding: 20 }}>
          <div onClick={e => e.stopPropagation()} style={{ background: "#fff", borderRadius: 14, width: "100%", maxWidth: 500, overflow: "hidden", boxShadow: "0 20px 60px rgba(0,0,0,0.15)" }}>
            <div style={{ padding: "16px 20px", borderBottom: "0.5px solid #e2e8f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 13, fontWeight: 600, color: "#1B4F8A" }}>{selectedIssue.id}</span>
              <button onClick={() => setSelectedIssue(null)} style={{ background: "none", border: "none", fontSize: 18, cursor: "pointer", color: "#94a3b8" }}>×</button>
            </div>
            <div style={{ padding: 20 }}>
              <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>{selectedIssue.title}</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[
                  ["Owner", selectedIssue.owner],
                  ["Category", selectedIssue.category],
                  ["Age", `${selectedIssue.age} days`],
                  ["Remediation Date", selectedIssue.remDate],
                ].map(([l, v]) => (
                  <div key={l}>
                    <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 3 }}>{l.toUpperCase()}</div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{v}</div>
                  </div>
                ))}
                <div>
                  <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 3 }}>STATUS</div>
                  <Badge label={selectedIssue.status} styles={STATUS_STYLES[selectedIssue.status]} />
                </div>
                <div>
                  <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 3 }}>RISK</div>
                  <Badge label={selectedIssue.risk} styles={RISK_STYLES[selectedIssue.risk]} />
                </div>
              </div>
              <div style={{ display: "flex", gap: 10, marginTop: 20, justifyContent: "flex-end" }}>
                <button onClick={() => setSelectedIssue(null)} style={{ background: "transparent", border: "0.5px solid #cbd5e1", padding: "8px 16px", borderRadius: 8, fontSize: 13, cursor: "pointer", color: "#64748b", fontFamily: "inherit" }}>Close</button>
                {selectedIssue.status !== "Closed" && (
                  <button onClick={() => closeIssue(selectedIssue.id)} style={btnPrimary}>Mark as Closed</button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 300,
          background: toast.type === "error" ? "#dc2626" : "#1B4F8A",
          color: "#fff", padding: "12px 18px", borderRadius: 10,
          fontSize: 13, fontWeight: 500, display: "flex", alignItems: "center", gap: 8,
          boxShadow: "0 8px 30px rgba(0,0,0,0.15)", fontFamily: "'Syne',sans-serif",
          animation: "slideUp 0.3s ease",
        }}>
          {toast.type === "error" ? "✕" : "✓"} {toast.msg}
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes spin { to{transform:rotate(360deg)} }
        @keyframes slideUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
        * { box-sizing: border-box; }
        input:focus, select:focus { outline: 2px solid #1B4F8A; outline-offset: 1px; }
      `}</style>
    </div>
  );
}
