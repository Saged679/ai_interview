// ============================================================
// IntelliviewLogin.jsx — Split Screen Home Page
// ============================================================
// Props:
//   onGetStarted → navigate to TalentLogin
//   onSkip       → navigate to MainJobFeed (NEW)
// ============================================================

import { useState } from "react";

const styles = {
  page: {
    display: "flex",
    height: "100vh",
    width: "100vw",
    fontFamily: "'Sora', 'Segoe UI', sans-serif",
    overflow: "hidden",
    backgroundColor: "#0a0f1e",
  },
  logo: {
    position: "absolute", top: "22px", left: "36px", zIndex: 10,
    color: "#ffffff", fontWeight: "700", fontSize: "20px", letterSpacing: "0.5px",
  },

  panel: {
    position: "relative", flex: 1, display: "flex",
    flexDirection: "column", justifyContent: "flex-end",
    padding: "40px 44px", overflow: "hidden", cursor: "pointer",
    transition: "flex 0.5s ease",
  },
  panelHover: { flex: 1.08 },
  bgImage: {
    position: "absolute", inset: 0, width: "100%", height: "100%",
    objectFit: "cover", objectPosition: "center top", zIndex: 0,
    filter: "brightness(0.55)", transition: "filter 0.4s",
  },
  overlay: {
    position: "absolute", inset: 0,
    background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 50%, transparent 100%)",
    zIndex: 1,
  },
  content: { position: "relative", zIndex: 2 },
  badge: {
    display: "inline-block", backgroundColor: "rgba(255,255,255,0.15)",
    backdropFilter: "blur(8px)", border: "1px solid rgba(255,255,255,0.25)",
    borderRadius: "20px", padding: "4px 14px", fontSize: "11px",
    fontWeight: "700", letterSpacing: "1.5px", color: "#ffffff",
    marginBottom: "14px", textTransform: "uppercase",
  },
  heading: {
    fontSize: "clamp(32px, 4vw, 52px)", fontWeight: "800",
    color: "#ffffff", lineHeight: 1.1, marginBottom: "16px",
  },
  subtext: {
    fontSize: "clamp(12px, 1.1vw, 14px)", color: "rgba(255,255,255,0.75)",
    lineHeight: 1.6, marginBottom: "28px", maxWidth: "320px",
  },
  buttonRow: { display: "flex", gap: "12px", marginBottom: "36px", flexWrap: "wrap" },
  btnPrimary: {
    backgroundColor: "#1a6bfa", color: "#ffffff", border: "none",
    borderRadius: "10px", padding: "13px 24px", fontSize: "14px",
    fontWeight: "600", cursor: "pointer", transition: "background 0.2s, transform 0.15s",
  },
  btnSecondary: {
    backgroundColor: "rgba(255,255,255,0.1)", color: "#ffffff",
    border: "1px solid rgba(255,255,255,0.3)", borderRadius: "10px",
    padding: "13px 24px", fontSize: "14px", fontWeight: "600",
    cursor: "pointer", backdropFilter: "blur(6px)", transition: "background 0.2s, transform 0.15s",
  },
  btnWhite: {
    backgroundColor: "#ffffff", color: "#0a0f1e", border: "none",
    borderRadius: "10px", padding: "13px 24px", fontSize: "14px",
    fontWeight: "600", cursor: "pointer", transition: "background 0.2s, transform 0.15s",
  },
  statsRow: { display: "flex", gap: "32px" },
  statNumber: { fontSize: "22px", fontWeight: "700", color: "#ffffff", lineHeight: 1 },
  statLabel: {
    fontSize: "10px", fontWeight: "600", letterSpacing: "1px",
    color: "rgba(255,255,255,0.55)", textTransform: "uppercase", marginTop: "4px",
  },
  divider: {
    position: "absolute", top: "50%", left: "50%",
    transform: "translate(-50%, -50%)", zIndex: 20,
    width: "1px", height: "60%", background: "rgba(255,255,255,0.15)",
  },
  footer: {
    position: "absolute", bottom: "18px", left: "50%",
    transform: "translateX(-50%)", zIndex: 10,
    display: "flex", gap: "24px", whiteSpace: "nowrap",
  },
  footerLink: {
    fontSize: "10px", fontWeight: "600", letterSpacing: "1px",
    color: "rgba(255,255,255,0.45)", textTransform: "uppercase",
    textDecoration: "none", cursor: "pointer",
  },
  aiPill: {
    position: "absolute", bottom: "48px", left: "50%",
    transform: "translateX(-50%)", zIndex: 10,
    display: "flex", alignItems: "center", gap: "8px",
    backgroundColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)",
    border: "1px solid rgba(255,255,255,0.2)", borderRadius: "30px",
    padding: "8px 20px", color: "#ffffff", fontSize: "12px",
    fontWeight: "500", whiteSpace: "nowrap",
  },
  dot: {
    width: "8px", height: "8px", borderRadius: "50%",
    backgroundColor: "#22c55e", animation: "pulse 2s infinite",
  },
};

// Accepts onGetStarted and onEnterprise from App.js
export default function IntelliviewLogin({ onGetStarted, onEnterprise }) {

  const [hoveredPanel, setHoveredPanel] = useState(null);

  return (
    <div style={styles.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap');
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50%       { opacity: 0.5; transform: scale(1.4); }
        }
        button:hover { transform: scale(1.03); }
      `}</style>

      {/* Logo */}
      <div style={styles.logo}>Intelliview</div>

      {/* LEFT PANEL */}
      <div
        style={{ ...styles.panel, ...(hoveredPanel === "talent" ? styles.panelHover : {}) }}
        onMouseEnter={() => setHoveredPanel("talent")}
        onMouseLeave={() => setHoveredPanel(null)}
      >
        <img
          src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=900&q=80"
          alt="Talent"
          style={{ ...styles.bgImage, filter: hoveredPanel === "talent" ? "brightness(0.65)" : "brightness(0.55)" }}
        />
        <div style={styles.overlay} />
        <div style={styles.content}>
          <div style={styles.badge}>Individual</div>
          <h1 style={styles.heading}>Sign in as<br />Talent</h1>
          <p style={styles.subtext}>
            Unleash your potential with AI-driven interview insights and connect with global opportunities.
          </p>
          <div style={styles.buttonRow}>
            <button style={styles.btnPrimary} onClick={onGetStarted}>
              Get Started →
            </button>
            <button style={styles.btnSecondary}>Resume Profile</button>
          </div>
          <div style={styles.statsRow}>
            <div>
              <div style={styles.statNumber}>450k+</div>
              <div style={styles.statLabel}>Matches Made</div>
            </div>
            <div>
              <div style={styles.statNumber}>92%</div>
              <div style={styles.statLabel}>Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.divider} />

      {/* RIGHT PANEL */}
      <div
        style={{ ...styles.panel, ...(hoveredPanel === "org" ? styles.panelHover : {}) }}
        onMouseEnter={() => setHoveredPanel("org")}
        onMouseLeave={() => setHoveredPanel(null)}
      >
        <img
          src="https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=900&q=80"
          alt="Enterprise"
          style={{ ...styles.bgImage, filter: hoveredPanel === "org" ? "brightness(0.65)" : "brightness(0.55)" }}
        />
        <div style={styles.overlay} />
        <div style={styles.content}>
          <div style={{ ...styles.badge, marginLeft: "auto", display: "table" }}>Enterprise</div>
          <h1 style={styles.heading}>Sign in as<br />Organization</h1>
          <p style={styles.subtext}>
            Scale your hiring with precision. Identify top 1% talent using advanced behavioral analytics.
          </p>
          <div style={styles.buttonRow}>
            <button style={styles.btnSecondary}>Request Demo</button>
            {/* ✅ This button now navigates to EnterpriseLogin page */}
            <button style={styles.btnWhite} onClick={onEnterprise}>🏢 Enterprise Login</button>
          </div>
          <div style={styles.statsRow}>
            <div>
              <div style={styles.statNumber}>2.4k+</div>
              <div style={styles.statLabel}>Global Clients</div>
            </div>
            <div>
              <div style={styles.statNumber}>15m</div>
              <div style={styles.statLabel}>Avg. Hire Time</div>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.aiPill}>
        <span>🤖</span>
        <span>AI Decision Core Active</span>
        <div style={styles.dot} />
      </div>

      <div style={styles.footer}>
        <a style={styles.footerLink}>Privacy Policy</a>
        <a style={styles.footerLink}>Terms of Service</a>
        <a style={styles.footerLink}>Security</a>
      </div>
    </div>
  );
}