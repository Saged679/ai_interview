// ============================================================
// MainJobFeed.jsx — Main Dashboard Page
// ============================================================
// NEW: Clicking "Intelliview Now" on any job card opens a
// modal popup called "Application Setup" which has:
//   - Step progress bar (3 steps)
//   - CV upload area (PDF only, drag & drop or browse)
//   - Portfolio URL input
//   - Cover note textarea (optional)
//   - "Save as Draft" and "Next Step: AI Briefing" buttons
// ============================================================

import { useState, useRef } from "react";

const C = {
  blue:     "#1a6bfa",
  blueDark: "#1558d6",
  navy:     "#0a0f1e",
  gray50:   "#f8f9fc",
  gray100:  "#f1f3f8",
  gray200:  "#e5e8f0",
  gray400:  "#9ca3af",
  gray600:  "#4b5563",
  gray900:  "#111827",
  white:    "#ffffff",
};

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: C.gray100,
    fontFamily: "'Sora', 'Segoe UI', sans-serif",
    color: C.gray900,
  },

  // ── NAVBAR ─────────────────────────────────────────────────
  navbar: {
    backgroundColor: C.white,
    borderBottom: `1px solid ${C.gray200}`,
    display: "flex", alignItems: "center",
    padding: "0 28px", height: "58px", gap: "28px",
    position: "sticky", top: 0, zIndex: 100,
    boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
  },
  navLogo: { fontSize: "20px", fontWeight: "800", color: C.blue, letterSpacing: "-0.5px", marginRight: "8px", flexShrink: 0 },
  navLinks: { display: "flex", gap: "4px", flex: 1 },
  navLink: {
    padding: "6px 14px", fontSize: "13px", fontWeight: "500", color: C.gray600,
    borderRadius: "8px", cursor: "pointer", border: "none", backgroundColor: "transparent",
  },
  navLinkActive: { color: C.blue, fontWeight: "700", borderBottom: `2px solid ${C.blue}`, borderRadius: "0" },
  searchBar: {
    display: "flex", alignItems: "center", gap: "8px",
    backgroundColor: C.gray100, border: `1px solid ${C.gray200}`,
    borderRadius: "10px", padding: "8px 14px", width: "220px", flexShrink: 0,
  },
  searchInput: { border: "none", background: "transparent", outline: "none", fontSize: "13px", color: C.gray600, width: "100%", fontFamily: "'Sora', sans-serif" },
  navIcons: { display: "flex", alignItems: "center", gap: "12px", marginLeft: "8px" },
  iconBtn: { width: "36px", height: "36px", borderRadius: "50%", border: `1px solid ${C.gray200}`, backgroundColor: C.white, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "16px" },
  avatar: { width: "36px", height: "36px", borderRadius: "50%", backgroundColor: C.blue, display: "flex", alignItems: "center", justifyContent: "center", color: C.white, fontWeight: "700", fontSize: "14px", cursor: "pointer" },

  // ── BODY ───────────────────────────────────────────────────
  body: { display: "flex", maxWidth: "1100px", margin: "0 auto", padding: "24px 16px", gap: "20px", alignItems: "flex-start" },

  // ── LEFT SIDEBAR ───────────────────────────────────────────
  leftSidebar: { width: "210px", flexShrink: 0, display: "flex", flexDirection: "column", gap: "14px" },
  profileCard: { backgroundColor: C.white, borderRadius: "16px", overflow: "hidden", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  profileBanner: { height: "64px", backgroundColor: C.blue },
  profileAvatarWrap: { display: "flex", flexDirection: "column", alignItems: "center", padding: "0 16px 16px", marginTop: "-28px" },
  profileAvatarImg: { width: "56px", height: "56px", borderRadius: "50%", border: `3px solid ${C.white}`, backgroundColor: "#c7d2fe", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "22px" },
  profileName: { fontSize: "15px", fontWeight: "700", color: C.gray900, marginTop: "8px", textAlign: "center" },
  profileTitle: { fontSize: "12px", color: C.gray400, textAlign: "center", marginTop: "2px", lineHeight: 1.4 },
  profileStats: { borderTop: `1px solid ${C.gray100}`, padding: "12px 16px", display: "flex", flexDirection: "column", gap: "8px" },
  profileStatRow: { display: "flex", justifyContent: "space-between", fontSize: "12px" },
  profileStatLabel: { color: C.gray600 },
  profileStatValue: { color: C.blue, fontWeight: "700" },
  scoreCard: { backgroundColor: C.white, borderRadius: "16px", padding: "18px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  scoreTitle: { fontSize: "12px", fontWeight: "700", color: C.gray600, letterSpacing: "0.5px", marginBottom: "8px", textTransform: "uppercase" },
  scoreBig: { fontSize: "40px", fontWeight: "800", color: C.gray900, lineHeight: 1 },
  scoreMax: { fontSize: "14px", color: C.gray400, fontWeight: "500" },
  scoreDesc: { fontSize: "12px", color: C.gray600, marginTop: "8px", lineHeight: 1.5 },
  improveBtn: { marginTop: "14px", width: "100%", padding: "9px", borderRadius: "10px", border: `1px solid ${C.blue}`, backgroundColor: "transparent", color: C.blue, fontSize: "12px", fontWeight: "700", cursor: "pointer" },

  // ── FEED ───────────────────────────────────────────────────
  feed: { flex: 1, display: "flex", flexDirection: "column", gap: "14px", minWidth: 0 },
  composerCard: { backgroundColor: C.white, borderRadius: "16px", padding: "16px 20px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  composerTop: { display: "flex", alignItems: "center", gap: "12px", marginBottom: "14px" },
  composerAvatar: { width: "40px", height: "40px", borderRadius: "50%", backgroundColor: "#c7d2fe", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px", flexShrink: 0 },
  composerInput: { flex: 1, padding: "10px 16px", borderRadius: "30px", border: `1px solid ${C.gray200}`, backgroundColor: C.gray50, fontSize: "13px", color: C.gray400, outline: "none", cursor: "pointer", fontFamily: "'Sora', sans-serif" },
  composerActions: { display: "flex", gap: "8px", borderTop: `1px solid ${C.gray100}`, paddingTop: "12px" },
  composerActionBtn: { display: "flex", alignItems: "center", gap: "6px", padding: "7px 14px", borderRadius: "8px", border: "none", backgroundColor: "transparent", color: C.gray600, fontSize: "13px", fontWeight: "500", cursor: "pointer" },
  jobCard: { backgroundColor: C.white, borderRadius: "16px", padding: "20px 24px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  jobCardTop: { display: "flex", alignItems: "flex-start", gap: "14px", marginBottom: "12px" },
  jobIcon: { width: "46px", height: "46px", borderRadius: "12px", backgroundColor: C.gray100, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "22px", flexShrink: 0 },
  jobInfo: { flex: 1, minWidth: 0 },
  jobTitle: { fontSize: "16px", fontWeight: "700", color: C.gray900, marginBottom: "3px" },
  jobMeta: { fontSize: "13px", color: C.gray600 },
  jobBadgeRow: { display: "flex", alignItems: "center", gap: "8px", marginTop: "8px" },
  badge: (color, bg) => ({ display: "inline-block", backgroundColor: bg, color, fontSize: "10px", fontWeight: "700", letterSpacing: "0.8px", textTransform: "uppercase", padding: "3px 10px", borderRadius: "20px" }),
  jobTime: { fontSize: "12px", color: C.gray400 },
  jobDesc: { fontSize: "13px", color: C.gray600, lineHeight: 1.6, marginBottom: "16px" },
  jobActions: { display: "flex", gap: "10px", alignItems: "center" },
  intelliviewBtn: { flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "12px", borderRadius: "30px", border: "none", backgroundColor: C.blue, color: C.white, fontSize: "13px", fontWeight: "700", cursor: "pointer", transition: "background 0.2s" },
  applyBtn: { padding: "12px 24px", borderRadius: "30px", border: `1.5px solid ${C.gray200}`, backgroundColor: C.white, color: C.gray900, fontSize: "13px", fontWeight: "600", cursor: "pointer" },
  bookmarkBtn: { padding: "10px", borderRadius: "10px", border: "none", backgroundColor: "transparent", cursor: "pointer", fontSize: "18px", color: C.gray400 },

  // ── RIGHT SIDEBAR ──────────────────────────────────────────
  rightSidebar: { width: "220px", flexShrink: 0, display: "flex", flexDirection: "column", gap: "14px" },
  recommendCard: { backgroundColor: C.white, borderRadius: "16px", padding: "18px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  recommendTitle: { fontSize: "13px", fontWeight: "700", color: C.gray900, marginBottom: "16px", display: "flex", justifyContent: "space-between", alignItems: "center" },
  recommendItem: { display: "flex", gap: "10px", marginBottom: "14px", alignItems: "flex-start" },
  recommendIcon: { width: "32px", height: "32px", borderRadius: "8px", backgroundColor: C.gray100, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", flexShrink: 0 },
  recommendName: { fontSize: "13px", fontWeight: "600", color: C.gray900, lineHeight: 1.3 },
  recommendParticipants: { fontSize: "11px", color: C.gray400, marginTop: "1px" },
  startPrepLink: { fontSize: "11px", color: C.blue, fontWeight: "600", cursor: "pointer", marginTop: "3px", display: "block" },
  viewAllBtn: { fontSize: "12px", color: C.blue, fontWeight: "600", cursor: "pointer", marginTop: "4px", textAlign: "center", display: "block" },
  sidebarFooter: { backgroundColor: C.white, borderRadius: "16px", padding: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" },
  sidebarFooterLinks: { display: "flex", flexWrap: "wrap", gap: "6px 12px", marginBottom: "12px" },
  sidebarFooterLink: { fontSize: "11px", color: C.gray400, cursor: "pointer", textDecoration: "none" },
  sidebarBrand: { display: "flex", alignItems: "center", gap: "6px", marginTop: "8px", fontSize: "11px", color: C.gray400 },
  sidebarBrandLogo: { fontSize: "13px", fontWeight: "800", color: C.blue },

  // ══════════════════════════════════════════════════════════
  // ── MODAL STYLES ──────────────────────────────────────────
  // ══════════════════════════════════════════════════════════

  // Dark overlay that covers the whole screen behind the modal
  modalOverlay: {
    position: "fixed",           // stays in place even when scrolling
    inset: 0,                    // covers top, right, bottom, left
    backgroundColor: "rgba(0,0,0,0.45)",
    backdropFilter: "blur(3px)", // blurs the background
    zIndex: 200,                 // above everything else
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
  },

  // The white modal box itself
  modalBox: {
    backgroundColor: C.white,
    borderRadius: "20px",
    width: "100%",
    maxWidth: "520px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
    overflow: "hidden",
    animation: "modalIn 0.2s ease",
  },

  // Top bar inside modal: company icon + job info + close button
  modalHeader: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
    padding: "20px 24px 16px",
    borderBottom: `1px solid ${C.gray100}`,
  },

  // Company icon square
  modalCompanyIcon: {
    width: "42px",
    height: "42px",
    borderRadius: "10px",
    backgroundColor: C.navy,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "20px",
    flexShrink: 0,
  },

  modalJobTitle: {
    fontSize: "15px",
    fontWeight: "700",
    color: C.gray900,
    lineHeight: 1.2,
  },

  modalJobMeta: {
    fontSize: "11px",
    fontWeight: "600",
    letterSpacing: "0.8px",
    textTransform: "uppercase",
    color: C.gray400,
    marginTop: "2px",
  },

  // X close button top right
  modalCloseBtn: {
    marginLeft: "auto",
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    border: "none",
    backgroundColor: C.gray100,
    cursor: "pointer",
    fontSize: "16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: C.gray600,
    flexShrink: 0,
  },

  // ── STEP PROGRESS BAR ─────────────────────────────────────
  // 3 colored bars showing which step you're on
  stepsRow: {
    display: "flex",
    gap: "6px",
    padding: "16px 24px 0",
  },

  // Each step bar (colored = active, gray = inactive)
  stepBar: (active) => ({
    flex: 1,
    height: "4px",
    borderRadius: "2px",
    backgroundColor: active ? C.blue : C.gray200,
  }),

  // ── MODAL BODY (scrollable content) ───────────────────────
  modalBody: {
    padding: "20px 24px 24px",
    overflowY: "auto",
    maxHeight: "60vh",
  },

  modalSectionTitle: {
    fontSize: "22px",
    fontWeight: "800",
    color: C.gray900,
    marginBottom: "6px",
  },

  modalSectionDesc: {
    fontSize: "13px",
    color: C.gray600,
    lineHeight: 1.5,
    marginBottom: "24px",
  },

  // Label above each field
  fieldLabel: {
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "1px",
    textTransform: "uppercase",
    color: C.gray600,
    marginBottom: "8px",
    display: "block",
  },

  // ── CV UPLOAD DROPZONE ─────────────────────────────────────
  dropzone: (isDragging) => ({
    border: `2px dashed ${isDragging ? C.blue : C.gray200}`,
    borderRadius: "12px",
    backgroundColor: isDragging ? "#eff6ff" : C.gray50,
    padding: "32px 20px",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "20px",
    transition: "all 0.2s",
  }),

  dropzoneIcon: {
    fontSize: "32px",
    marginBottom: "10px",
    display: "block",
    color: C.blue,
  },

  dropzoneText: {
    fontSize: "14px",
    color: C.gray600,
    fontWeight: "500",
  },

  dropzoneBrowse: {
    color: C.blue,
    fontWeight: "700",
    textDecoration: "underline",
    cursor: "pointer",
  },

  dropzoneHint: {
    fontSize: "11px",
    color: C.gray400,
    marginTop: "6px",
    display: "block",
  },

  // Uploaded file pill shown after file is selected
  filePill: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    backgroundColor: "#eff6ff",
    border: `1px solid #bfdbfe`,
    borderRadius: "10px",
    padding: "10px 14px",
    marginBottom: "20px",
  },

  filePillName: {
    fontSize: "13px",
    fontWeight: "600",
    color: C.blue,
    flex: 1,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },

  filePillRemove: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: C.gray400,
    fontSize: "16px",
    padding: 0,
  },

  // ── URL + TEXTAREA INPUTS ──────────────────────────────────
  urlInputWrap: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    border: `1px solid ${C.gray200}`,
    borderRadius: "10px",
    backgroundColor: C.gray50,
    padding: "11px 14px",
    marginBottom: "20px",
  },

  urlInput: {
    border: "none",
    background: "transparent",
    outline: "none",
    fontSize: "13px",
    color: C.gray900,
    width: "100%",
    fontFamily: "'Sora', sans-serif",
  },

  textarea: {
    width: "100%",
    minHeight: "100px",
    border: `1px solid ${C.gray200}`,
    borderRadius: "10px",
    backgroundColor: C.gray50,
    padding: "12px 14px",
    fontSize: "13px",
    color: C.gray900,
    fontFamily: "'Sora', sans-serif",
    outline: "none",
    resize: "vertical",          // user can resize vertically only
    lineHeight: 1.5,
    boxSizing: "border-box",
  },

  // ── MODAL FOOTER (buttons) ────────────────────────────────
  modalFooter: {
    display: "flex",
    gap: "12px",
    padding: "16px 24px",
    borderTop: `1px solid ${C.gray100}`,
    alignItems: "center",
  },

  draftBtn: {
    padding: "12px 20px",
    borderRadius: "10px",
    border: `1.5px solid ${C.gray200}`,
    backgroundColor: C.white,
    color: C.gray600,
    fontSize: "13px",
    fontWeight: "600",
    cursor: "pointer",
  },

  nextBtn: {
    flex: 1,
    padding: "13px",
    borderRadius: "30px",
    border: "none",
    backgroundColor: C.blue,
    color: C.white,
    fontSize: "14px",
    fontWeight: "700",
    cursor: "pointer",
    transition: "background 0.2s",
  },
};

// ── Job data ──────────────────────────────────────────────────
const JOBS = [
  { id: 1, icon: "🏗️", title: "Lead Product Architect",  company: "Vortex Systems",  location: "Menlo Park, CA (Remote)", badge: { text: "AI MATCO: 98%",  color: "#1a6bfa", bg: "#eff6ff" }, time: "2 hours ago",  desc: "We are looking for a visionary Lead Product Architect to join our Core Intelligence team. You will be responsible for scaling our neural inference engine that powers millions of real-time interactions daily." },
  { id: 2, icon: "👥", title: "Senior UX Engineer",       company: "Creative Logic",  location: "London, UK (Hybrid)",    badge: { text: "SKILLS MATCO",   color: "#7c3aed", bg: "#f5f3ff" }, time: "5 hours ago",  desc: "Bridge the gap between design and engineering. Work with our world-class design system to build accessible, high-performance web applications using React, Tailwind, and Framer Motion." },
  { id: 3, icon: "☁️", title: "Cloud Infrastructure Lead", company: "Aether Cloud",   location: "Austin, TX",             badge: { text: "TOP PICK",       color: "#059669", bg: "#ecfdf5" }, time: "Yesterday",    desc: "Join our elite DevOps squad and manage global-scale Kubernetes clusters. We're migrating to a next-gen mesh architecture and need a leader who breathes YAML and Terraform." },
];

const RECOMMENDATIONS = [
  { icon: "💻", name: "Backend Architecture",   participants: "1.2k participants" },
  { icon: "🎨", name: "Product Design Ethics",  participants: "850 participants" },
  { icon: "📐", name: "System Scalability",     participants: "3.4k participants" },
];

// ─────────────────────────────────────────────────────────────
export default function MainJobFeed({ onBack }) {
  const [activeNav, setActiveNav] = useState("Intelliviews");
  const [savedJobs, setSavedJobs] = useState(new Set());

  // ── MODAL STATE ───────────────────────────────────────────
  // selectedJob holds the job object for the open modal (null = closed)
  const [selectedJob, setSelectedJob] = useState(null);

  // Form fields inside the modal
  const [cvFile,       setCvFile]       = useState(null);    // the uploaded PDF file
  const [portfolioUrl, setPortfolioUrl] = useState("");      // portfolio link
  const [coverNote,    setCoverNote]    = useState("");      // cover note text
  const [isDragging,   setIsDragging]   = useState(false);  // drag-over state

  // Hidden file input ref — we trigger it when user clicks the dropzone
  const fileInputRef = useRef(null);

  // Open modal for a specific job
  const openModal = (job) => {
    setSelectedJob(job);
    setCvFile(null);        // reset form each time
    setPortfolioUrl("");
    setCoverNote("");
  };

  // Close modal
  const closeModal = () => setSelectedJob(null);

  // Handle file selected from input or drag-drop
  const handleFile = (file) => {
    if (file && file.type === "application/pdf") {
      setCvFile(file);
    } else {
      alert("Please upload a PDF file only.");
    }
  };

  // Drag-and-drop handlers
  const onDragOver  = (e) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = ()  => setIsDragging(false);
  const onDrop      = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const toggleSave = (id) => {
    setSavedJobs(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div style={styles.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        button:hover { opacity: 0.88; }
        @keyframes modalIn {
          from { opacity: 0; transform: scale(0.95) translateY(10px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
      `}</style>

      {/* ══ NAVBAR ════════════════════════════════════════════ */}
      <nav style={styles.navbar}>
        <span style={styles.navLogo}>Intelliview</span>
        <div style={styles.navLinks}>
          {["Feed", "Intelliviews", "Messages", "Profile"].map(link => (
            <button key={link} style={{ ...styles.navLink, ...(activeNav === link ? styles.navLinkActive : {}) }} onClick={() => setActiveNav(link)}>
              {link}
            </button>
          ))}
        </div>
        <div style={styles.searchBar}>
          <span style={{ color: C.gray400, fontSize: "14px" }}>🔍</span>
          <input style={styles.searchInput} placeholder="Search for opportunities..." />
        </div>
        <div style={styles.navIcons}>
          <div style={styles.iconBtn}>🔔</div>
          <div style={styles.iconBtn}>⚙️</div>
          <div style={styles.avatar}>A</div>
        </div>
      </nav>

      {/* ══ BODY ══════════════════════════════════════════════ */}
      <div style={styles.body}>

        {/* LEFT SIDEBAR */}
        <div style={styles.leftSidebar}>
          <div style={styles.profileCard}>
            <div style={styles.profileBanner} />
            <div style={styles.profileAvatarWrap}>
              <div style={styles.profileAvatarImg}>🧑‍💻</div>
              <div style={styles.profileName}>Alex Chen</div>
              <div style={styles.profileTitle}>Senior Fullstack Developer at TechFlow</div>
            </div>
            <div style={styles.profileStats}>
              <div style={styles.profileStatRow}>
                <span style={styles.profileStatLabel}>Profile views</span>
                <span style={styles.profileStatValue}>142</span>
              </div>
              <div style={styles.profileStatRow}>
                <span style={styles.profileStatLabel}>Post Impressions</span>
                <span style={styles.profileStatValue}>1,024</span>
              </div>
            </div>
          </div>
          <div style={styles.scoreCard}>
            <div style={styles.scoreTitle}>AI Talent Score</div>
            <div><span style={styles.scoreBig}>92</span><span style={styles.scoreMax}> /100</span></div>
            <p style={styles.scoreDesc}>Your profile matches 92% of top AI engineering roles currently open.</p>
            <button style={styles.improveBtn}>Improve Score</button>
          </div>
        </div>

        {/* CENTER FEED */}
        <div style={styles.feed}>

          {/* Composer */}
          <div style={styles.composerCard}>
            <div style={styles.composerTop}>
              <div style={styles.composerAvatar}>🧑‍💻</div>
              <input style={styles.composerInput} placeholder="Start a post, try AI assistance..." readOnly />
            </div>
            <div style={styles.composerActions}>
              {[["🖼️", "Media"], ["📅", "Event"], ["✏️", "Write article"]].map(([icon, label]) => (
                <button key={label} style={styles.composerActionBtn}><span>{icon}</span> {label}</button>
              ))}
            </div>
          </div>

          {/* Job cards */}
          {JOBS.map(job => (
            <div key={job.id} style={styles.jobCard}>
              <div style={styles.jobCardTop}>
                <div style={styles.jobIcon}>{job.icon}</div>
                <div style={styles.jobInfo}>
                  <div style={styles.jobTitle}>{job.title}</div>
                  <div style={styles.jobMeta}>{job.company} • {job.location}</div>
                  <div style={styles.jobBadgeRow}>
                    <span style={styles.badge(job.badge.color, job.badge.bg)}>{job.badge.text}</span>
                    <span style={styles.jobTime}>• {job.time}</span>
                  </div>
                </div>
                <button style={{ ...styles.bookmarkBtn, color: savedJobs.has(job.id) ? C.blue : C.gray400 }} onClick={() => toggleSave(job.id)}>
                  {savedJobs.has(job.id) ? "🔖" : "🏷️"}
                </button>
              </div>
              <p style={styles.jobDesc}>{job.desc}</p>
              <div style={styles.jobActions}>
                {/* ✅ Clicking this opens the modal for THIS specific job */}
                <button style={styles.intelliviewBtn} onClick={() => openModal(job)}>
                  <span>🎯</span> Intelliview Now
                </button>
                <button style={styles.applyBtn}>Apply</button>
              </div>
            </div>
          ))}

        </div>{/* end feed */}

        {/* RIGHT SIDEBAR */}
        <div style={styles.rightSidebar}>
          <div style={styles.recommendCard}>
            <div style={styles.recommendTitle}>
              <span>Recommended Intelliviews</span>
              <span style={{ fontSize: "16px", cursor: "pointer", color: C.gray400 }}>ℹ️</span>
            </div>
            {RECOMMENDATIONS.map((rec, i) => (
              <div key={i} style={styles.recommendItem}>
                <div style={styles.recommendIcon}>{rec.icon}</div>
                <div>
                  <div style={styles.recommendName}>{rec.name}</div>
                  <div style={styles.recommendParticipants}>{rec.participants}</div>
                  <a style={styles.startPrepLink}>+ Start Prep</a>
                </div>
              </div>
            ))}
            <a style={styles.viewAllBtn}>View all recommendations</a>
          </div>
          <div style={styles.sidebarFooter}>
            <div style={styles.sidebarFooterLinks}>
              {["About", "Accessibility", "Help Center", "Privacy & Terms", "Ad Choices", "Advertising", "Business Services"].map(link => (
                <a key={link} style={styles.sidebarFooterLink}>{link}</a>
              ))}
            </div>
            <div style={styles.sidebarBrand}>
              <span style={styles.sidebarBrandLogo}>Intelliview</span>
              <span>Intelliview Corporation © 2024</span>
            </div>
          </div>
        </div>

      </div>{/* end body */}

      {/* ══════════════════════════════════════════════════════
          MODAL — only renders when selectedJob is not null
      ══════════════════════════════════════════════════════ */}
      {selectedJob && (
        // Clicking the dark overlay closes the modal
        <div style={styles.modalOverlay} onClick={closeModal}>

          {/* Clicking inside the box does NOT close it */}
          <div style={styles.modalBox} onClick={(e) => e.stopPropagation()}>

            {/* ── MODAL HEADER ────────────────────────────── */}
            <div style={styles.modalHeader}>
              {/* Company icon */}
              <div style={styles.modalCompanyIcon}>{selectedJob.icon}</div>

              {/* Job title + company info */}
              <div>
                <div style={styles.modalJobTitle}>Application Setup</div>
                <div style={styles.modalJobMeta}>
                  {selectedJob.company} • {selectedJob.title}
                </div>
              </div>

              {/* Close button */}
              <button style={styles.modalCloseBtn} onClick={closeModal}>✕</button>
            </div>

            {/* ── STEP PROGRESS BAR ─────────────────────── */}
            {/* 3 bars: first is blue (active), rest are gray */}
            <div style={styles.stepsRow}>
              <div style={styles.stepBar(true)}  />   {/* Step 1: active (Upload Assets) */}
              <div style={styles.stepBar(false)} />   {/* Step 2: inactive */}
              <div style={styles.stepBar(false)} />   {/* Step 3: inactive */}
            </div>

            {/* ── MODAL BODY ────────────────────────────── */}
            <div style={styles.modalBody}>

              <div style={styles.modalSectionTitle}>Upload Assets</div>
              <p style={styles.modalSectionDesc}>
                To proceed with the AI-led interview, please provide your current CV and portfolio link.
              </p>

              {/* ── CV UPLOAD ─────────────────────────── */}
              <label style={styles.fieldLabel}>Curriculum Vitae (PDF)</label>

              {/* Hidden real file input — triggered by clicking dropzone */}
              <input
                type="file"
                accept=".pdf"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={(e) => handleFile(e.target.files[0])}
              />

              {/* Show dropzone if no file uploaded yet */}
              {!cvFile ? (
                <div
                  style={styles.dropzone(isDragging)}
                  onDragOver={onDragOver}
                  onDragLeave={onDragLeave}
                  onDrop={onDrop}
                  onClick={() => fileInputRef.current.click()} // open file picker
                >
                  <span style={styles.dropzoneIcon}>☁️</span>
                  <div style={styles.dropzoneText}>
                    Drop your CV here or{" "}
                    <span style={styles.dropzoneBrowse}>browse</span>
                  </div>
                  <span style={styles.dropzoneHint}>Max file size 5MB • PDF only</span>
                </div>
              ) : (
                // Once a file is selected, show its name in a pill
                <div style={styles.filePill}>
                  <span>📄</span>
                  <span style={styles.filePillName}>{cvFile.name}</span>
                  {/* Remove button clears the file */}
                  <button style={styles.filePillRemove} onClick={() => setCvFile(null)}>✕</button>
                </div>
              )}

              {/* ── PORTFOLIO URL ──────────────────────── */}
              <label style={styles.fieldLabel}>Portfolio URL</label>
              <div style={styles.urlInputWrap}>
                <span style={{ fontSize: "16px" }}>🌐</span>
                <input
                  type="url"
                  placeholder="https://behance.net/yourname"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  style={styles.urlInput}
                />
              </div>

              {/* ── COVER NOTE ─────────────────────────── */}
              <label style={styles.fieldLabel}>Cover Note (Optional)</label>
              <textarea
                placeholder="Tell the AI what makes you a great fit for this specific role..."
                value={coverNote}
                onChange={(e) => setCoverNote(e.target.value)}
                style={styles.textarea}
              />

            </div>{/* end modal body */}

            {/* ── MODAL FOOTER ──────────────────────────── */}
            <div style={styles.modalFooter}>
              <button style={styles.draftBtn} onClick={closeModal}>
                Save as Draft
              </button>
              <button style={styles.nextBtn}>
                Next Step: AI Briefing →
              </button>
            </div>

          </div>{/* end modal box */}
        </div> // end overlay
      )}

    </div> // end page
  );
}