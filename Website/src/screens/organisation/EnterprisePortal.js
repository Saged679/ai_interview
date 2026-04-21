// ============================================================
// EnterprisePortal.jsx — Organization Recruitment Dashboard
// ============================================================
// FIXED: Removed all function-based styles (e.g. s.navItem(active))
// All styles are now plain objects. Active/inactive states are
// handled inline using spread + conditional objects in JSX.
// ============================================================

import { useState } from "react";

// All styles as plain objects — no functions
const s = {
  page: {
    display: "flex",
    minHeight: "100vh",
    backgroundColor: "#f1f5f2",
    fontFamily: "'Sora', 'Segoe UI', sans-serif",
    color: "#111c17",
  },

  // ── LEFT SIDEBAR ───────────────────────────────────────────
  sidebar: {
    width: "180px",
    flexShrink: 0,
    backgroundColor: "#ffffff",
    borderRight: "1px solid #dde5e0",
    display: "flex",
    flexDirection: "column",
    padding: "20px 0",
    position: "sticky",
    top: 0,
    height: "100vh",
  },

  brand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "0 16px 20px",
    borderBottom: "1px solid #f1f5f2",
    marginBottom: "12px",
  },

  brandIcon: {
    width: "36px",
    height: "36px",
    borderRadius: "10px",
    backgroundColor: "#e8f5ee",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "18px",
    flexShrink: 0,
  },

  brandName: { fontSize: "13px", fontWeight: "800", color: "#0d1f1a", lineHeight: 1.2 },
  brandSub:  { fontSize: "10px", color: "#8fa89a", fontWeight: "500", textTransform: "uppercase", letterSpacing: "0.5px" },

  // Base nav item style
  navItem: {
    display: "flex", alignItems: "center", gap: "10px",
    padding: "10px 16px", fontSize: "13px", fontWeight: "500",
    color: "#4a6357", backgroundColor: "transparent",
    borderLeft: "3px solid transparent", cursor: "pointer", marginBottom: "2px",
  },

  // Active nav item overrides
  navItemActive: {
    fontWeight: "700", color: "#1a6b45",
    backgroundColor: "#e8f5ee", borderLeft: "3px solid #1a6b45",
  },

  navIcon: { fontSize: "16px" },

  sidebarBottom: { marginTop: "auto", borderTop: "1px solid #f1f5f2", padding: "12px 0 0" },

  // ── TOP BAR ────────────────────────────────────────────────
  main: { flex: 1, display: "flex", flexDirection: "column", minWidth: 0 },

  topbar: {
    display: "flex", alignItems: "center", gap: "12px",
    padding: "0 28px", height: "54px", backgroundColor: "#ffffff",
    borderBottom: "1px solid #dde5e0", position: "sticky", top: 0, zIndex: 50,
  },

  searchBar: {
    display: "flex", alignItems: "center", gap: "8px",
    backgroundColor: "#f1f5f2", border: "1px solid #dde5e0",
    borderRadius: "10px", padding: "8px 14px", flex: 1, maxWidth: "380px",
  },

  searchInput: {
    border: "none", background: "transparent", outline: "none",
    fontSize: "13px", color: "#4a6357", width: "100%", fontFamily: "'Sora', sans-serif",
  },

  topbarRight: { display: "flex", alignItems: "center", gap: "12px", marginLeft: "auto" },

  topbarIcon: {
    width: "34px", height: "34px", borderRadius: "50%",
    border: "1px solid #dde5e0", backgroundColor: "#ffffff",
    display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "15px",
  },

  userChip: { display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" },

  userAvatar: {
    width: "34px", height: "34px", borderRadius: "50%",
    backgroundColor: "#1a6b45", color: "#ffffff",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontWeight: "700", fontSize: "14px",
  },

  userName: { fontSize: "13px", fontWeight: "600", color: "#0d1f1a" },
  userRole: { fontSize: "11px", color: "#8fa89a" },

  // ── CONTENT ────────────────────────────────────────────────
  content: { display: "flex", gap: "20px", padding: "24px", alignItems: "flex-start", flex: 1 },
  formArea: { flex: 1, minWidth: 0 },

  backLink: {
    display: "flex", alignItems: "center", gap: "6px",
    fontSize: "12px", fontWeight: "600", color: "#8fa89a",
    textTransform: "uppercase", letterSpacing: "0.8px", cursor: "pointer", marginBottom: "12px",
  },

  pageTitle: { fontSize: "28px", fontWeight: "800", color: "#0d1f1a", marginBottom: "4px" },
  pageDesc:  { fontSize: "13px", color: "#8fa89a", marginBottom: "24px" },

  // ── STEP ROW ───────────────────────────────────────────────
  stepsRow: { display: "flex", gap: "0", marginBottom: "24px", alignItems: "flex-start" },

  stepCircleActive: {
    width: "28px", height: "28px", borderRadius: "50%",
    backgroundColor: "#1a6b45", color: "#ffffff",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "12px", fontWeight: "800", flexShrink: 0,
  },

  stepCircleInactive: {
    width: "28px", height: "28px", borderRadius: "50%",
    backgroundColor: "#dde5e0", color: "#8fa89a",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "12px", fontWeight: "800", flexShrink: 0,
  },

  stepLineActive:   { flex: 1, height: "2px", backgroundColor: "#1a6b45", marginTop: 0, marginLeft: "4px", marginRight: "4px" },
  stepLineInactive: { flex: 1, height: "2px", backgroundColor: "#dde5e0", marginTop: 0, marginLeft: "4px", marginRight: "4px" },

  stepLabelActive:   { fontSize: "13px", fontWeight: "700", color: "#0d1f1a", marginLeft: "2px", marginTop: "8px" },
  stepLabelInactive: { fontSize: "13px", fontWeight: "500", color: "#8fa89a", marginLeft: "2px", marginTop: "8px" },
  stepSub: { fontSize: "11px", color: "#8fa89a", marginLeft: "2px" },

  // ── FORM CARDS ─────────────────────────────────────────────
  formCard: {
    backgroundColor: "#ffffff", borderRadius: "16px", padding: "24px",
    marginBottom: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.05)",
    borderLeft: "4px solid #1a6b45",
  },

  cardTitle: {
    display: "flex", alignItems: "center", gap: "8px",
    fontSize: "15px", fontWeight: "700", color: "#0d1f1a", marginBottom: "20px",
  },

  fieldLabel: {
    fontSize: "11px", fontWeight: "700", letterSpacing: "0.8px",
    textTransform: "uppercase", color: "#4a6357", marginBottom: "7px", display: "block",
  },

  textInput: {
    width: "100%", padding: "11px 14px", borderRadius: "8px",
    border: "1px solid #dde5e0", backgroundColor: "#f8fafc",
    fontSize: "13px", color: "#0d1f1a", outline: "none",
    fontFamily: "'Sora', sans-serif", marginBottom: "16px", boxSizing: "border-box",
  },

  twoCol: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" },

  select: {
    width: "100%", padding: "11px 14px", borderRadius: "8px",
    border: "1px solid #dde5e0", backgroundColor: "#f8fafc",
    fontSize: "13px", color: "#0d1f1a", outline: "none",
    fontFamily: "'Sora', sans-serif", cursor: "pointer",
  },

  workModelRow: { display: "flex", gap: "6px", marginBottom: "16px" },

  // Work model button — base
  workModelBtn: {
    padding: "8px 16px", borderRadius: "8px",
    border: "1px solid #dde5e0", backgroundColor: "#ffffff",
    color: "#4a6357", fontSize: "12px", fontWeight: "600", cursor: "pointer",
  },

  // Work model button — active override
  workModelBtnActive: {
    border: "1px solid #1a6b45", backgroundColor: "#e8f5ee", color: "#1a6b45",
  },

  locationWrap: { position: "relative", marginBottom: "0" },
  locationIcon: { position: "absolute", left: "12px", top: "12px", fontSize: "14px", color: "#8fa89a" },

  locationInput: {
    width: "100%", padding: "11px 14px 11px 36px", borderRadius: "8px",
    border: "1px solid #dde5e0", backgroundColor: "#f8fafc",
    fontSize: "13px", color: "#0d1f1a", outline: "none",
    fontFamily: "'Sora', sans-serif", boxSizing: "border-box",
  },

  descCard: {
    backgroundColor: "#ffffff", borderRadius: "16px", padding: "24px",
    marginBottom: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.05)",
  },

  descCardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" },

  aiBtn: {
    display: "flex", alignItems: "center", gap: "6px",
    padding: "8px 14px", borderRadius: "8px", border: "none",
    backgroundColor: "#1a6b45", color: "#ffffff", fontSize: "12px", fontWeight: "600", cursor: "pointer",
  },

  lockedArea: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", padding: "40px", color: "#8fa89a", gap: "8px",
  },

  criteriaCard: {
    backgroundColor: "#ffffff", borderRadius: "16px", padding: "24px",
    marginBottom: "20px", boxShadow: "0 2px 12px rgba(0,0,0,0.05)",
  },

  criteriaDesc: { fontSize: "13px", color: "#8fa89a", marginBottom: "16px" },

  criteriaItem: {
    display: "flex", alignItems: "center", gap: "10px",
    padding: "12px 14px", borderRadius: "8px",
    border: "1px solid #dde5e0", backgroundColor: "#f8fafc",
    marginBottom: "8px", fontSize: "13px", color: "#0d1f1a",
  },

  criteriaRemove: { marginLeft: "auto", background: "none", border: "none", cursor: "pointer", color: "#8fa89a", fontSize: "16px" },

  formFooter: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px" },

  draftBtn: {
    padding: "12px 20px", borderRadius: "10px",
    border: "1.5px solid #dde5e0", backgroundColor: "#ffffff",
    color: "#4a6357", fontSize: "13px", fontWeight: "600", cursor: "pointer",
  },

  nextBtn: {
    padding: "12px 28px", borderRadius: "10px", border: "none",
    backgroundColor: "#1a6b45", color: "#ffffff", fontSize: "13px", fontWeight: "700", cursor: "pointer",
  },

  // ── RIGHT PANEL ────────────────────────────────────────────
  rightPanel: { width: "220px", flexShrink: 0, display: "flex", flexDirection: "column", gap: "14px" },

  benchCard: {
    borderRadius: "16px", padding: "20px",
    background: "linear-gradient(135deg, #1a2520 0%, #0d3322 100%)",
    color: "#ffffff", boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
  },

  benchBadge: {
    display: "flex", alignItems: "center", gap: "6px",
    fontSize: "10px", fontWeight: "700", letterSpacing: "1px",
    textTransform: "uppercase", color: "#22c55e", marginBottom: "10px",
  },

  benchTitle: { fontSize: "17px", fontWeight: "800", marginBottom: "12px", lineHeight: 1.2 },
  benchDesc:  { fontSize: "12px", color: "rgba(255,255,255,0.65)", lineHeight: 1.6, marginBottom: "16px" },
  benchHighlight: { color: "#22c55e", fontWeight: "700" },
  benchDivider: { height: "1px", backgroundColor: "rgba(255,255,255,0.1)", margin: "14px 0" },
  benchLabel: { fontSize: "11px", color: "rgba(255,255,255,0.5)", textTransform: "uppercase", letterSpacing: "0.8px" },
  benchNum:   { fontSize: "32px", fontWeight: "800", color: "#ffffff", lineHeight: 1, marginTop: "4px" },
  progressBar: { height: "4px", borderRadius: "2px", backgroundColor: "rgba(255,255,255,0.1)", marginTop: "8px", overflow: "hidden" },
  progressFill:{ height: "100%", width: "72%", borderRadius: "2px", backgroundColor: "#22c55e" },

  settingsCard: { backgroundColor: "#ffffff", borderRadius: "16px", padding: "18px", boxShadow: "0 2px 12px rgba(0,0,0,0.05)" },
  settingsTitle: { fontSize: "11px", fontWeight: "700", letterSpacing: "1px", textTransform: "uppercase", color: "#4a6357", marginBottom: "14px" },
  settingRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px", fontSize: "13px", color: "#0d1f1a", fontWeight: "500" },

  // Toggle ON
  toggleOn:  { width: "36px", height: "20px", borderRadius: "10px", backgroundColor: "#1a6b45", position: "relative", cursor: "pointer" },
  // Toggle OFF
  toggleOff: { width: "36px", height: "20px", borderRadius: "10px", backgroundColor: "#dde5e0", position: "relative", cursor: "pointer" },
  // Knob ON (right)
  knobOn:  { position: "absolute", top: "3px", left: "19px", width: "14px", height: "14px", borderRadius: "50%", backgroundColor: "#ffffff", boxShadow: "0 1px 4px rgba(0,0,0,0.2)" },
  // Knob OFF (left)
  knobOff: { position: "absolute", top: "3px", left: "3px",  width: "14px", height: "14px", borderRadius: "50%", backgroundColor: "#ffffff", boxShadow: "0 1px 4px rgba(0,0,0,0.2)" },

  settingsNote: { fontSize: "11px", color: "#8fa89a", display: "flex", alignItems: "center", gap: "5px", marginTop: "4px" },

  hqCard: { borderRadius: "16px", overflow: "hidden", position: "relative", height: "120px", boxShadow: "0 2px 12px rgba(0,0,0,0.1)" },
  hqImg:  { width: "100%", height: "100%", objectFit: "cover", filter: "brightness(0.55)" },
  hqLabel:{ position: "absolute", bottom: "12px", left: "14px", color: "#ffffff" },
  hqName: { fontSize: "13px", fontWeight: "700" },
  hqLoc:  { fontSize: "11px", color: "rgba(255,255,255,0.7)" },
};

const NAV = [
  { icon: "💼", label: "Jobs",       active: true  },
  { icon: "👥", label: "Candidates", active: false },
  { icon: "📊", label: "Analytics",  active: false },
  { icon: "⚙️", label: "Settings",   active: false },
];

export default function EnterprisePortal({ onBack }) {
  const [workModel,    setWorkModel]    = useState("Remote");
  const [postLinkedIn, setPostLinkedIn] = useState(true);
  const [postIndeed,   setPostIndeed]   = useState(false);
  const [jobTitle,     setJobTitle]     = useState("");
  const [location,     setLocation]     = useState("");

  return (
    <div style={s.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        button:hover { opacity: 0.88; }
        input:focus, select:focus { border-color: #1a6b45 !important; background: #fff !important; outline: none; }
      `}</style>

      {/* ── LEFT SIDEBAR ──────────────────────────────────── */}
      <div style={s.sidebar}>

        <div style={s.brand}>
          <div style={s.brandIcon}>🏢</div>
          <div>
            <div style={s.brandName}>Pro-Tech Enterprise</div>
            <div style={s.brandSub}>Recruitment Portal</div>
          </div>
        </div>

        {/* Nav items — merge base + active style inline */}
        {NAV.map(item => (
          <div key={item.label} style={{ ...s.navItem, ...(item.active ? s.navItemActive : {}) }}>
            <span style={s.navIcon}>{item.icon}</span>
            {item.label}
          </div>
        ))}

        <div style={s.sidebarBottom}>
          <div style={s.navItem}><span style={s.navIcon}>❓</span> Help Center</div>
          <div style={s.navItem}><span style={s.navIcon}>🚪</span> Log Out</div>
        </div>
      </div>

      {/* ── MAIN ────────────────────────────────────────────── */}
      <div style={s.main}>

        {/* Topbar */}
        <div style={s.topbar}>
          <div style={s.searchBar}>
            <span style={{ fontSize: "14px", color: "#8fa89a" }}>🔍</span>
            <input style={s.searchInput} placeholder="Search positions, candidates..." />
          </div>
          <div style={s.topbarRight}>
            <div style={s.topbarIcon}>🔔</div>
            <div style={s.topbarIcon}>💬</div>
            <div style={s.userChip}>
              <div style={s.userAvatar}>A</div>
              <div>
                <div style={s.userName}>Alex Rivera</div>
                <div style={s.userRole}>Head of Talent</div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div style={s.content}>

          {/* ── FORM AREA ───────────────────────────────────── */}
          <div style={s.formArea}>

            <div style={s.backLink}>← Back to Dashboard</div>
            <h1 style={s.pageTitle}>Post New Job</h1>
            <p style={s.pageDesc}>Define the blueprint for your next organizational growth.</p>

            {/* Steps */}
            <div style={s.stepsRow}>
              {[
                { num: "01", label: "Job Basics",         sub: "Role identity & location", active: true  },
                { num: "02", label: "Job Description",    sub: "Scope & responsibilities", active: false },
                { num: "03", label: "Interview Criteria", sub: "AI Evaluation parameters", active: false },
              ].map((step, i) => (
                <div key={i} style={{ display: "flex", flex: 1, alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {/* Circle */}
                      <div style={step.active ? s.stepCircleActive : s.stepCircleInactive}>
                        {step.num}
                      </div>
                      {/* Connector line — skip on last item */}
                      {i < 2 && <div style={step.active ? s.stepLineActive : s.stepLineInactive} />}
                    </div>
                    <div style={step.active ? s.stepLabelActive : s.stepLabelInactive}>{step.label}</div>
                    <div style={s.stepSub}>{step.sub}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Role Essentials */}
            <div style={s.formCard}>
              <div style={s.cardTitle}><span>📋</span> Role Essentials</div>

              <label style={s.fieldLabel}>Job Title</label>
              <input
                style={s.textInput}
                placeholder="e.g. Senior Security Architect"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />

              <div style={s.twoCol}>
                <div>
                  <label style={s.fieldLabel}>Department</label>
                  <select style={s.select}>
                    <option>Engineering</option>
                    <option>Product</option>
                    <option>Design</option>
                    <option>Marketing</option>
                  </select>
                </div>
                <div>
                  <label style={s.fieldLabel}>Work Model</label>
                  <div style={s.workModelRow}>
                    {["Remote", "Hybrid", "On-site"].map(m => (
                      <button
                        key={m}
                        style={{
                          ...s.workModelBtn,
                          ...(workModel === m ? s.workModelBtnActive : {}),
                        }}
                        onClick={() => setWorkModel(m)}
                      >{m}</button>
                    ))}
                  </div>
                </div>
              </div>

              <label style={s.fieldLabel}>Primary Location</label>
              <div style={s.locationWrap}>
                <span style={s.locationIcon}>📍</span>
                <input
                  style={s.locationInput}
                  placeholder="City, Country"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>
            </div>

            {/* Job Description (locked) */}
            <div style={s.descCard}>
              <div style={s.descCardHeader}>
                <div style={s.cardTitle}><span>📄</span> Job Description</div>
                <button style={s.aiBtn}><span>✨</span> AI Assist: Generate Description</button>
              </div>
              <div style={s.lockedArea}>
                <span style={{ fontSize: "28px" }}>🔒</span>
                <span style={{ fontSize: "13px" }}>Complete Step 1 to unlock</span>
              </div>
            </div>

            {/* Interview Criteria */}
            <div style={s.criteriaCard}>
              <div style={s.cardTitle}><span>🎯</span> Interview Criteria</div>
              <p style={s.criteriaDesc}>Set specific questions or technical skills for the AI evaluation agent.</p>
              {[
                { icon: "💻", text: "Technical: Python Security Vulnerabilities" },
                { icon: "💡", text: "Soft Skills: Crisis Management & Ownership" },
              ].map((item, i) => (
                <div key={i} style={s.criteriaItem}>
                  <span>{item.icon}</span>
                  {item.text}
                  <button style={s.criteriaRemove}>⋯</button>
                </div>
              ))}
            </div>

            <div style={s.formFooter}>
              <button style={s.draftBtn}>Save Draft</button>
              <button style={s.nextBtn}>Next: Job Description →</button>
            </div>

          </div>{/* end form area */}

          {/* ── RIGHT PANEL ──────────────────────────────────── */}
          <div style={s.rightPanel}>

            {/* Market Benchmarking */}
            <div style={s.benchCard}>
              <div style={s.benchBadge}><span>🛡️</span> Security Insight</div>
              <div style={s.benchTitle}>Market Benchmarking</div>
              <p style={s.benchDesc}>
                Positions with <span style={s.benchHighlight}>"Remote"</span> status in Cybersecurity see a{" "}
                <span style={s.benchHighlight}>42% higher</span> application rate in your region.
              </p>
              <div style={s.benchDivider} />
              <div style={s.benchLabel}>Expected Applicants</div>
              <div style={s.benchNum}>850+</div>
              <div style={s.progressBar}><div style={s.progressFill} /></div>
            </div>

            {/* Post Settings */}
            <div style={s.settingsCard}>
              <div style={s.settingsTitle}>Post Settings</div>

              <div style={s.settingRow}>
                <span>Post to LinkedIn</span>
                <div
                  style={postLinkedIn ? s.toggleOn : s.toggleOff}
                  onClick={() => setPostLinkedIn(!postLinkedIn)}
                >
                  <div style={postLinkedIn ? s.knobOn : s.knobOff} />
                </div>
              </div>

              <div style={s.settingRow}>
                <span>Post to Indeed</span>
                <div
                  style={postIndeed ? s.toggleOn : s.toggleOff}
                  onClick={() => setPostIndeed(!postIndeed)}
                >
                  <div style={postIndeed ? s.knobOn : s.knobOff} />
                </div>
              </div>

              <div style={s.settingsNote}>
                <span>ℹ️</span> Posts will be active for 30 days.
              </div>
            </div>

            {/* HQ image */}
            <div style={s.hqCard}>
              <img
                src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80"
                alt="HQ"
                style={s.hqImg}
              />
              <div style={s.hqLabel}>
                <div style={s.hqName}>Pro-Tech HQ</div>
                <div style={s.hqLoc}>San Francisco, CA</div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}