// ============================================================
// EnterpriseLogin.jsx — Organization Login Page
// ============================================================
// Shown when clicking "Enterprise Login" on the split screen.
// Design: clean white card on a soft green-tinted background,
// green accent color throughout (Pro-Tech Enterprise branding)
//
// Props:
//   onSkip → navigate to EnterprisePortal (the dashboard)
//   onBack → go back to home split screen
// ============================================================

import { useState } from "react";

const G = {
  green:      "#1a6b45",
  greenLight: "#22c55e",
  greenBg:    "#f0faf4",
  greenSoft:  "#e8f5ee",
  navy:       "#0d1f1a",
  gray50:     "#f8fafc",
  gray100:    "#f1f5f3",
  gray200:    "#dde5e0",
  gray400:    "#8fa89a",
  gray600:    "#4a6357",
  gray900:    "#111c17",
  white:      "#ffffff",
};

const s = {
  // Full page — soft gradient background (top-left mint, rest white)
  page: {
    minHeight: "100vh",
    width: "100vw",
    background: "linear-gradient(135deg, #d4f0e4 0%, #edfaf3 25%, #ffffff 60%)",
    fontFamily: "'Sora', 'Segoe UI', sans-serif",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    padding: "40px 20px",
  },

  // "Organization Login" page label top-left
  pageLabel: {
    position: "absolute",
    top: "20px",
    left: "28px",
    fontSize: "12px",
    fontWeight: "600",
    color: G.gray400,
    letterSpacing: "0.5px",
  },

  // Skip button top-right
  skipBtn: {
    position: "absolute",
    top: "18px",
    right: "28px",
    backgroundColor: "transparent",
    border: `1px solid ${G.gray200}`,
    borderRadius: "20px",
    padding: "7px 18px",
    fontSize: "13px",
    fontWeight: "600",
    color: G.gray600,
    cursor: "pointer",
    transition: "border-color 0.2s, color 0.2s",
  },

  // Green shield icon at top center
  iconWrap: {
    width: "64px",
    height: "64px",
    borderRadius: "18px",
    backgroundColor: G.greenSoft,
    border: `1px solid #b6e8cd`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "28px",
    marginBottom: "20px",
    boxShadow: "0 4px 16px rgba(26,107,69,0.12)",
  },

  // Company name heading
  companyName: {
    fontSize: "clamp(26px, 3vw, 34px)",
    fontWeight: "800",
    color: G.navy,
    textAlign: "center",
    marginBottom: "8px",
    letterSpacing: "-0.5px",
  },

  // "Secure Organization Gateway" subtitle
  subtitle: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "12px",
    fontWeight: "700",
    letterSpacing: "1.2px",
    textTransform: "uppercase",
    color: G.gray400,
    marginBottom: "32px",
  },

  // White form card
  card: {
    backgroundColor: G.white,
    borderRadius: "20px",
    padding: "32px 36px",
    width: "100%",
    maxWidth: "420px",
    boxShadow: "0 4px 32px rgba(0,0,0,0.07)",
  },

  // SSO button (light blue-gray)
  ssoBtn: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    padding: "15px",
    borderRadius: "12px",
    border: "none",
    backgroundColor: "#eaf1fb",
    color: G.navy,
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "24px",
    transition: "background 0.2s",
  },

  ssoIcon: {
    width: "32px",
    height: "32px",
    borderRadius: "8px",
    backgroundColor: "#d4e4f7",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "16px",
  },

  // OR divider
  dividerRow: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginBottom: "24px",
  },
  dividerLine: { flex: 1, height: "1px", backgroundColor: G.gray200 },
  dividerText: {
    fontSize: "11px", fontWeight: "700", letterSpacing: "1.5px",
    textTransform: "uppercase", color: G.gray400,
  },

  // Field label
  label: {
    display: "block",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "1px",
    textTransform: "uppercase",
    color: G.gray600,
    marginBottom: "8px",
  },

  // Input wrapper (icon + input together)
  inputWrap: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    backgroundColor: G.gray50,
    border: `1px solid ${G.gray200}`,
    borderRadius: "10px",
    padding: "12px 14px",
    marginBottom: "18px",
    transition: "border-color 0.2s",
  },

  inputIcon: { fontSize: "16px", flexShrink: 0, color: G.gray400 },

  input: {
    border: "none",
    background: "transparent",
    outline: "none",
    fontSize: "14px",
    color: G.navy,
    width: "100%",
    fontFamily: "'Sora', sans-serif",
  },

  // Password row: label + FORGOT? link side by side
  passwordLabelRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },

  forgotLink: {
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "0.8px",
    color: G.green,
    cursor: "pointer",
    textTransform: "uppercase",
  },

  // Eye icon inside password field
  eyeBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "16px",
    color: G.gray400,
    padding: 0,
    flexShrink: 0,
  },

  // Big green Sign In button
  signInBtn: {
    width: "100%",
    padding: "15px",
    borderRadius: "12px",
    border: "none",
    backgroundColor: G.green,
    color: G.white,
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    marginTop: "4px",
    marginBottom: "0",
    transition: "background 0.2s",
    letterSpacing: "0.3px",
  },

  // "New to the network?" text
  registerText: {
    marginTop: "22px",
    fontSize: "14px",
    color: G.gray400,
    textAlign: "center",
  },

  registerLink: {
    color: G.green,
    fontWeight: "700",
    cursor: "pointer",
    textDecoration: "none",
  },

  // Footer links row
  footer: {
    marginTop: "36px",
    display: "flex",
    alignItems: "center",
    gap: "14px",
    flexWrap: "wrap",
    justifyContent: "center",
  },

  footerLink: {
    fontSize: "11px",
    fontWeight: "600",
    letterSpacing: "0.8px",
    textTransform: "uppercase",
    color: G.gray400,
    cursor: "pointer",
    textDecoration: "none",
  },

  footerDot: { color: G.gray400, fontSize: "6px" },

  // "All Systems Operational" status pill
  statusPill: {
    marginTop: "16px",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    backgroundColor: G.greenSoft,
    border: `1px solid #b6e8cd`,
    borderRadius: "20px",
    padding: "6px 16px",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "0.8px",
    textTransform: "uppercase",
    color: G.green,
  },

  statusDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    backgroundColor: G.greenLight,
    animation: "pulse 2s infinite",
  },
};

export default function EnterpriseLogin({ onSkip, onBack }) {
  const [orgId,     setOrgId]     = useState("");
  const [email,     setEmail]     = useState("");
  const [password,  setPassword]  = useState("");
  const [showPass,  setShowPass]  = useState(false); // toggle password visibility

  return (
    <div style={s.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        button:hover { opacity: 0.88; transform: scale(1.01); }
        input:focus + * { border-color: #1a6b45; }
        .inp-wrap:focus-within { border-color: #1a6b45 !important; background: #fff !important; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.4)} }
      `}</style>

      {/* Page label */}
      <div style={s.pageLabel}>Organization Login</div>

      {/* Skip button → goes to Enterprise Portal dashboard */}
      <button style={s.skipBtn} onClick={onSkip}>Skip →</button>

      {/* Shield icon */}
      <div style={s.iconWrap}>🛡️</div>

      {/* Company name */}
      <h1 style={s.companyName}>Pro-Tech Enterprise</h1>

      {/* Subtitle */}
      <div style={s.subtitle}>
        <span>🔒</span>
        <span>Secure Organization Gateway</span>
      </div>

      {/* Form card */}
      <div style={s.card}>

        {/* SSO button */}
        <button style={s.ssoBtn}>
          <div style={s.ssoIcon}>🔑</div>
          Sign in with SSO (Okta/Google Workspace)
        </button>

        {/* OR divider */}
        <div style={s.dividerRow}>
          <div style={s.dividerLine} />
          <span style={s.dividerText}>Or access via credentials</span>
          <div style={s.dividerLine} />
        </div>

        {/* Organization ID field */}
        <label style={s.label}>Organization ID / Tax ID</label>
        <div className="inp-wrap" style={s.inputWrap}>
          <span style={s.inputIcon}>🏢</span>
          <input
            style={s.input}
            placeholder="e.g. ORG-998234"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
          />
        </div>

        {/* Work Email field */}
        <label style={s.label}>Work Email</label>
        <div className="inp-wrap" style={s.inputWrap}>
          <span style={s.inputIcon}>✉️</span>
          <input
            type="email"
            style={s.input}
            placeholder="name@pro-tech.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        {/* Password field */}
        <div style={s.passwordLabelRow}>
          <label style={{ ...s.label, marginBottom: 0 }}>Password</label>
          <a style={s.forgotLink}>Forgot?</a>
        </div>
        <div className="inp-wrap" style={s.inputWrap}>
          <span style={s.inputIcon}>🔒</span>
          <input
            type={showPass ? "text" : "password"}
            style={s.input}
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {/* Toggle show/hide password */}
          <button style={s.eyeBtn} onClick={() => setShowPass(!showPass)}>
            {showPass ? "🙈" : "👁️"}
          </button>
        </div>

        {/* Sign In button */}
        <button style={s.signInBtn}>Sign In →</button>

      </div>

      {/* Register link */}
      <p style={s.registerText}>
        New to the network?{" "}
        <a style={s.registerLink}>Register your Organization</a>
      </p>

      {/* Footer links */}
      <div style={s.footer}>
        <a style={s.footerLink}>Privacy Protocol</a>
        <span style={s.footerDot}>●</span>
        <a style={s.footerLink}>Terms of Access</a>
        <span style={s.footerDot}>●</span>
        <a style={s.footerLink}>Trust Center</a>
      </div>

      {/* Status pill */}
      <div style={s.statusPill}>
        <div style={s.statusDot} />
        All Systems Operational · V4.2.0
      </div>

    </div>
  );
}