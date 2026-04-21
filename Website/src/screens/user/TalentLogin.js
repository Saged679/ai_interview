// ============================================================
// TalentLogin.jsx — Talent Sign In Form Page
// ============================================================
// Props:
//   onBack → go back to the split screen home
//   onSkip → skip login and go directly to MainJobFeed  ← NEW
// ============================================================

import { useState } from "react";

const styles = {

  page: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    width: "100vw",
    backgroundColor: "#f0f2f7",
    fontFamily: "'Sora', 'Segoe UI', sans-serif",
    position: "relative",
  },

  // Logo top center
  logo: {
    position: "absolute",
    top: "28px",
    left: "50%",
    transform: "translateX(-50%)",
    fontSize: "18px",
    fontWeight: "700",
    color: "#0a0f1e",
    letterSpacing: "0.5px",
  },

  // ── NEW: Skip button — top right corner ──────────────────
  skipBtn: {
    position: "absolute",
    top: "22px",
    right: "28px",
    backgroundColor: "transparent",
    border: "1px solid #d1d5db",
    borderRadius: "20px",
    padding: "7px 18px",
    fontSize: "13px",
    fontWeight: "600",
    color: "#6b7280",
    cursor: "pointer",
    transition: "border-color 0.2s, color 0.2s",
    letterSpacing: "0.2px",
  },

  // White card
  card: {
    backgroundColor: "#ffffff",
    borderRadius: "20px",
    padding: "40px 40px",
    width: "100%",
    maxWidth: "440px",
    boxShadow: "0 4px 40px rgba(0,0,0,0.08)",
  },

  heading: {
    fontSize: "clamp(24px, 3vw, 32px)",
    fontWeight: "800",
    color: "#0a0f1e",
    textAlign: "center",
    marginBottom: "8px",
  },

  subtext: {
    fontSize: "14px",
    color: "#6b7280",
    textAlign: "center",
    marginBottom: "28px",
  },

  btnGoogle: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    padding: "13px",
    borderRadius: "10px",
    border: "1px solid #e5e7eb",
    backgroundColor: "#ffffff",
    fontSize: "14px",
    fontWeight: "600",
    color: "#0a0f1e",
    cursor: "pointer",
    marginBottom: "12px",
    transition: "background 0.2s, transform 0.15s",
  },

  btnLinkedIn: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    padding: "13px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#0a66c2",
    fontSize: "14px",
    fontWeight: "600",
    color: "#ffffff",
    cursor: "pointer",
    marginBottom: "20px",
    transition: "background 0.2s, transform 0.15s",
  },

  dividerRow: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginBottom: "20px",
  },

  dividerLine: { flex: 1, height: "1px", backgroundColor: "#e5e7eb" },

  dividerText: {
    fontSize: "12px", color: "#9ca3af",
    fontWeight: "600", letterSpacing: "1px",
  },

  label: {
    display: "block",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "1px",
    textTransform: "uppercase",
    color: "#374151",
    marginBottom: "8px",
  },

  labelRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },

  forgotLink: {
    fontSize: "12px", color: "#1a6bfa",
    cursor: "pointer", fontWeight: "500", textDecoration: "none",
  },

  input: {
    width: "100%",
    padding: "13px 16px",
    borderRadius: "10px",
    border: "1px solid #e5e7eb",
    fontSize: "14px",
    color: "#0a0f1e",
    backgroundColor: "#f9fafb",
    outline: "none",
    marginBottom: "16px",
    boxSizing: "border-box",
    transition: "border-color 0.2s",
  },

  btnSignIn: {
    width: "100%",
    padding: "15px",
    borderRadius: "30px",
    border: "none",
    backgroundColor: "#1a6bfa",
    color: "#ffffff",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    marginBottom: "16px",
    transition: "background 0.2s, transform 0.15s",
    letterSpacing: "0.3px",
  },

  secureBadge: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "6px",
    fontSize: "11px",
    fontWeight: "600",
    letterSpacing: "0.8px",
    textTransform: "uppercase",
    color: "#6b7280",
  },

  registerText: {
    marginTop: "20px",
    fontSize: "14px",
    color: "#6b7280",
    textAlign: "center",
  },

  registerLink: {
    color: "#1a6bfa", fontWeight: "600",
    cursor: "pointer", textDecoration: "none",
  },

  footer: {
    position: "absolute",
    bottom: "20px",
    display: "flex",
    gap: "20px",
    alignItems: "center",
  },

  footerText: { fontSize: "10px", color: "#9ca3af", letterSpacing: "0.5px" },

  footerLink: {
    fontSize: "10px", color: "#9ca3af", letterSpacing: "1px",
    textTransform: "uppercase", fontWeight: "600",
    cursor: "pointer", textDecoration: "none",
  },
};

// ── Receives onBack and onSkip from App.js ───────────────────
export default function TalentLogin({ onBack, onSkip }) {

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");

  return (
    <div style={styles.page}>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap');
        button:hover { transform: scale(1.02); }
        input:focus  { border-color: #1a6bfa !important; background: #fff !important; }
        .skip-btn:hover { border-color: #1a6bfa !important; color: #1a6bfa !important; }
      `}</style>

      {/* Logo */}
      <div style={styles.logo}>Intelliview</div>

      {/* ✅ SKIP BUTTON — top right
          onClick calls onSkip → App.js sets currentPage to "feed"
          → MainJobFeed is shown */}
      <button
        className="skip-btn"
        style={styles.skipBtn}
        onClick={onSkip}
      >
        Skip →
      </button>

      {/* White card */}
      <div style={styles.card}>

        <h1 style={styles.heading}>Welcome Back, Talent</h1>
        <p style={styles.subtext}>Access your AI-powered career dashboard</p>

        {/* Google button */}
        <button style={styles.btnGoogle}>
          <span style={{
            width: "18px", height: "18px", background: "#000",
            borderRadius: "3px", display: "inline-block", flexShrink: 0,
          }} />
          Sign in with Google
        </button>

        {/* LinkedIn button */}
        <button style={styles.btnLinkedIn}>
          <span style={{
            width: "18px", height: "18px", background: "#fff",
            borderRadius: "3px", display: "inline-block", flexShrink: 0,
            color: "#0a66c2", fontSize: "11px", fontWeight: "900",
            lineHeight: "18px", textAlign: "center",
          }}>in</span>
          Sign in with LinkedIn
        </button>

        {/* OR divider */}
        <div style={styles.dividerRow}>
          <div style={styles.dividerLine} />
          <span style={styles.dividerText}>OR</span>
          <div style={styles.dividerLine} />
        </div>

        {/* Email */}
        <label style={styles.label}>Email Address</label>
        <input
          type="email"
          placeholder="name@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
        />

        {/* Password */}
        <div style={styles.labelRow}>
          <label style={{ ...styles.label, marginBottom: 0 }}>Password</label>
          <a style={styles.forgotLink}>Forgot Password?</a>
        </div>
        <input
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />

        {/* Sign In */}
        <button style={styles.btnSignIn}>Sign In →</button>

        {/* Secure badge */}
        <div style={styles.secureBadge}>
          <span>🛡️</span>
          <span>Secure &amp; Encrypted Session</span>
        </div>

      </div>

      {/* Register link */}
      <p style={styles.registerText}>
        New to Intelliview?{" "}
        <a style={styles.registerLink}>Create your Profile</a>
      </p>

      {/* Footer */}
      <div style={styles.footer}>
        <span style={styles.footerText}>© 2024 Intelliview AI. Secure &amp; Encrypted.</span>
        <a style={styles.footerLink}>Privacy Policy</a>
        <a style={styles.footerLink}>Terms of Service</a>
        <a style={styles.footerLink}>Security</a>
      </div>

    </div>
  );
}