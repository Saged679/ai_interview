// ============================================================
// OrganizationDashboard.js — Organization Home Screen
// ============================================================
// Save as: OrganizationDashboard.js (use .js NOT .jsx)
//
// Shown after clicking Skip on EnterpriseLogin.
// Layout:
//   - Left sidebar (nav links)
//   - Center (stats, recent candidates, ongoing recruitment)
//   - Right (quick actions + AI Talent Insights)
//
// Props:
//   onPostJob → navigate to EnterprisePortal (Post New Job form)
//
// ---- BACKEND NOTES ----
// TODO: Stats (24 jobs, 158 interviews, 42 candidates) → GET /api/org/stats
// TODO: Recent candidates list → GET /api/candidates?sort=match&limit=3
// TODO: Ongoing recruitment cards → GET /api/jobs?status=active
// TODO: AI Talent Insights → GET /api/ai/insights
// ============================================================

import { useState } from "react";

export default function OrganizationDashboard({ onPostJob, onBack }) {

  // ── Active nav item state ──────────────────────────────────
  const [activeNav, setActiveNav] = useState("Jobs");

  // ── Colors ────────────────────────────────────────────────
  const green     = "#1a6b45";
  const greenSoft = "#e8f5ee";
  const navy      = "#0d1f1a";
  const gray100   = "#f1f5f2";
  const gray200   = "#dde5e0";
  const gray400   = "#8fa89a";
  const gray600   = "#4a6357";
  const white     = "#ffffff";
  const dark      = "#1a2520";

  // ── Static data (replace with API calls later) ─────────────
  // TODO: Replace with real data from backend API
  const stats = [
    { icon: "💼", label: "Active Job Posts",        value: "24",  trend: "+12%",   trendUp: true  },
    { icon: "🎯", label: "Pending AI Interviews",   value: "158", trend: "Steady", trendUp: null  },
    { icon: "⭐", label: "Top Matched Candidates",  value: "42",  trend: "+5%",    trendUp: true  },
  ];

  // TODO: Fetch from GET /api/candidates?sort=match&limit=3
  const candidates = [
    { name: "Elena Rodriguez", role: "Senior Full-Stack Developer",  match: 98, status: "SELECTED", statusColor: "#22c55e", statusBg: "#dcfce7" },
    { name: "Marcus Chen",     role: "Principal Product Designer",   match: 94, status: "IN REVIEW", statusColor: "#f97316", statusBg: "#ffedd5" },
    { name: "Sarah J. Miller", role: "DevOps Engineer",              match: 91, status: "ON HOLD",   statusColor: "#6b7280", statusBg: "#f3f4f6" },
  ];

  // TODO: Fetch from GET /api/jobs?status=active
  const jobs = [
    { icon: "</>",  label: "ACTIVE",  labelColor: green,    title: "Senior React Developer",  dept: "Engineering", model: "Remote",          applicants: 49, time: "2d ago" },
    { icon: "◎",    label: "ACTIVE",  labelColor: green,    title: "Lead UX Researcher",       dept: "Design",      model: "San Francisco, CA", applicants: 12, time: "5d ago" },
    { icon: "🛡",   label: "URGENT",  labelColor: "#f97316", title: "Cybersecurity Lead",      dept: "Security",    model: "Hybrid",            applicants: 85, time: "12h ago" },
  ];

  // Avatar initials helper
  const initials = (name) => name.split(" ").map(n => n[0]).join("").slice(0, 2);

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: gray100, fontFamily: "'Sora', 'Segoe UI', sans-serif", color: navy }}>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        button { cursor: pointer; font-family: 'Sora', sans-serif; }
        button:hover { opacity: 0.85; }
      `}</style>

      {/* ════════════════════════════════════════════════════
          LEFT SIDEBAR
      ════════════════════════════════════════════════════ */}
      <div style={{ width: "180px", flexShrink: 0, backgroundColor: white, borderRight: `1px solid ${gray200}`, display: "flex", flexDirection: "column", padding: "20px 0", position: "sticky", top: 0, height: "100vh" }}>

        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "0 16px 20px", borderBottom: `1px solid ${gray100}`, marginBottom: "12px" }}>
          <div style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: greenSoft, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px", flexShrink: 0 }}>🏢</div>
          <div>
            <div style={{ fontSize: "12px", fontWeight: "800", color: navy, lineHeight: 1.2 }}>Pro-Tech<br/>Enterprise</div>
            <div style={{ fontSize: "9px", color: gray400, textTransform: "uppercase", letterSpacing: "0.5px", marginTop: "2px" }}>Recruitment Portal</div>
          </div>
        </div>

        {/* Nav items */}
        {[
          { icon: "💼", label: "Jobs"       },
          { icon: "👥", label: "Candidates" },
          { icon: "📊", label: "Analytics"  },
          { icon: "⚙️", label: "Settings"   },
        ].map(item => (
          <div
            key={item.label}
            onClick={() => setActiveNav(item.label)}
            style={{
              display: "flex", alignItems: "center", gap: "10px",
              padding: "10px 16px", fontSize: "13px", marginBottom: "2px", cursor: "pointer",
              fontWeight:      activeNav === item.label ? "700"            : "500",
              color:           activeNav === item.label ? green            : gray600,
              backgroundColor: activeNav === item.label ? greenSoft        : "transparent",
              borderLeft:      activeNav === item.label ? `3px solid ${green}` : "3px solid transparent",
            }}
          >
            <span>{item.icon}</span>{item.label}
          </div>
        ))}

        {/* Bottom links */}
        <div style={{ marginTop: "auto", borderTop: `1px solid ${gray100}`, paddingTop: "12px" }}>
          {/* TODO: Link to support docs */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "10px 16px", fontSize: "13px", color: gray400, cursor: "pointer" }}>
            <span>❓</span> Help Center
          </div>
          {/* TODO: Call auth signout + redirect to home */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "10px 16px", fontSize: "13px", color: gray400, cursor: "pointer" }}>
            <span>🚪</span> Log Out
          </div>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
          MAIN CONTENT
      ════════════════════════════════════════════════════ */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>

        {/* ── TOP BAR ─────────────────────────────────────── */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "0 24px", height: "54px", backgroundColor: white, borderBottom: `1px solid ${gray200}`, position: "sticky", top: 0, zIndex: 50 }}>

          {/* Search bar */}
          {/* TODO: Wire to GET /api/search?q= for global search */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", backgroundColor: gray100, border: `1px solid ${gray200}`, borderRadius: "10px", padding: "8px 14px", flex: 1, maxWidth: "400px" }}>
            <span style={{ color: gray400, fontSize: "14px" }}>🔍</span>
            <input placeholder="Search candidates, jobs, or reports..." style={{ border: "none", background: "transparent", outline: "none", fontSize: "13px", color: gray600, width: "100%", fontFamily: "'Sora', sans-serif" }} />
          </div>

          {/* Right icons */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginLeft: "auto" }}>
            {/* TODO: Notifications bell → GET /api/notifications */}
            <div style={{ width: "34px", height: "34px", borderRadius: "50%", border: `1px solid ${gray200}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "15px", cursor: "pointer" }}>🔔</div>
            {/* TODO: Messages icon → link to messages page */}
            <div style={{ width: "34px", height: "34px", borderRadius: "50%", border: `1px solid ${gray200}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "15px", cursor: "pointer" }}>💬</div>
            {/* TODO: User avatar → pull from auth context */}
            <div style={{ width: "34px", height: "34px", borderRadius: "50%", backgroundColor: green, color: white, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "700", fontSize: "13px", cursor: "pointer" }}>AR</div>
            <div style={{ width: "34px", height: "34px", borderRadius: "50%", border: `1px solid ${gray200}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "15px", cursor: "pointer" }}>⚙️</div>
          </div>
        </div>

        {/* ── PAGE BODY ────────────────────────────────────── */}
        <div style={{ display: "flex", gap: "20px", padding: "28px 24px", alignItems: "flex-start", flex: 1 }}>

          {/* ══ CENTER CONTENT ════════════════════════════ */}
          <div style={{ flex: 1, minWidth: 0 }}>

            {/* Page header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
              <div>
                <h1 style={{ fontSize: "26px", fontWeight: "800", color: navy, marginBottom: "4px" }}>Organization Overview</h1>
                <p style={{ fontSize: "13px", color: gray400 }}>Real-time recruitment intelligence and active pipeline health.</p>
              </div>

              {/* ✅ POST NEW JOB BUTTON — navigates to EnterprisePortal */}
              <button
                onClick={onPostJob}
                style={{ display: "flex", alignItems: "center", gap: "8px", padding: "12px 20px", borderRadius: "12px", border: "none", backgroundColor: green, color: white, fontSize: "13px", fontWeight: "700", flexShrink: 0 }}
              >
                <span style={{ fontSize: "18px", fontWeight: "300" }}>+</span> Post New Job
              </button>
            </div>

            {/* ── STATS CARDS ──────────────────────────── */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px", marginBottom: "28px" }}>
              {stats.map((stat, i) => (
                <div key={i} style={{ backgroundColor: white, borderRadius: "14px", padding: "20px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)" }}>

                  {/* Icon + trend badge row */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                    <div style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: greenSoft, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px" }}>
                      {stat.icon}
                    </div>
                    {/* Trend badge */}
                    <span style={{
                      fontSize: "11px", fontWeight: "700", padding: "3px 8px", borderRadius: "20px",
                      backgroundColor: stat.trendUp === true ? "#dcfce7" : stat.trendUp === false ? "#fee2e2" : "#f1f5f2",
                      color:           stat.trendUp === true ? "#16a34a" : stat.trendUp === false ? "#dc2626" : gray400,
                    }}>
                      {stat.trendUp === true ? "▲ " : stat.trendUp === false ? "▼ " : "— "}{stat.trend}
                    </span>
                  </div>

                  {/* Big number */}
                  <div style={{ fontSize: "36px", fontWeight: "800", color: navy, lineHeight: 1, marginBottom: "6px" }}>{stat.value}</div>
                  <div style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.8px", color: gray400 }}>{stat.label}</div>
                </div>
              ))}
            </div>

            {/* ── RECENT HIGH-MATCH CANDIDATES ─────────── */}
            <div style={{ backgroundColor: white, borderRadius: "16px", padding: "20px 24px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)", marginBottom: "24px" }}>

              {/* Section header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
                <div style={{ fontSize: "15px", fontWeight: "700", color: navy }}>Recent High-Match Activity</div>
                {/* TODO: Navigate to full candidates list page */}
                <button style={{ fontSize: "12px", fontWeight: "600", color: green, background: "none", border: "none" }}>View All Candidates</button>
              </div>

              {/* Candidate rows */}
              {candidates.map((c, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: "14px", padding: "14px 0", borderBottom: i < candidates.length - 1 ? `1px solid ${gray100}` : "none" }}>

                  {/* Avatar circle with initials */}
                  <div style={{ width: "42px", height: "42px", borderRadius: "50%", backgroundColor: i === 0 ? "#dbeafe" : i === 1 ? "#fce7f3" : "#fef9c3", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "700", fontSize: "13px", color: navy, flexShrink: 0 }}>
                    {initials(c.name)}
                  </div>

                  {/* Name + role */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "14px", fontWeight: "600", color: navy }}>{c.name}</div>
                    <div style={{ fontSize: "12px", color: gray400 }}>{c.role} · <span style={{ color: green, fontWeight: "600" }}>{c.match}% Match</span></div>
                  </div>

                  {/* Status badge */}
                  <span style={{ fontSize: "10px", fontWeight: "700", letterSpacing: "0.8px", padding: "4px 10px", borderRadius: "20px", backgroundColor: c.statusBg, color: c.statusColor, flexShrink: 0 }}>
                    {c.status}
                  </span>

                  {/* Three-dot menu */}
                  {/* TODO: onClick → show context menu (View Profile, Schedule Interview, Archive) */}
                  <button style={{ background: "none", border: "none", color: gray400, fontSize: "18px", padding: "0 4px" }}>⋯</button>
                </div>
              ))}
            </div>

            {/* ── ONGOING RECRUITMENT ──────────────────── */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div style={{ fontSize: "15px", fontWeight: "700", color: navy }}>Ongoing Recruitment</div>
                {/* TODO: Filter icon → show filter dropdown */}
                <button style={{ background: "none", border: `1px solid ${gray200}`, borderRadius: "8px", padding: "6px 10px", color: gray400, fontSize: "14px" }}>⚡</button>
              </div>

              {/* Job cards grid — 3 columns */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px" }}>
                {jobs.map((job, i) => (
                  <div key={i} style={{ backgroundColor: white, borderRadius: "14px", padding: "18px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)", cursor: "pointer" }}>

                    {/* Icon + status badge */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                      <div style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: greenSoft, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "14px", fontWeight: "700", color: green }}>
                        {job.icon}
                      </div>
                      <span style={{ fontSize: "10px", fontWeight: "700", letterSpacing: "0.8px", color: job.labelColor, backgroundColor: job.labelColor === green ? greenSoft : "#fff7ed", padding: "3px 8px", borderRadius: "20px" }}>
                        {job.label}
                      </span>
                    </div>

                    {/* Job title */}
                    <div style={{ fontSize: "14px", fontWeight: "700", color: navy, marginBottom: "4px" }}>{job.title}</div>
                    <div style={{ fontSize: "12px", color: gray400, marginBottom: "14px" }}>{job.dept} · {job.model}</div>

                    {/* Footer: applicants + time */}
                    <div style={{ display: "flex", gap: "16px", fontSize: "12px", color: gray400, borderTop: `1px solid ${gray100}`, paddingTop: "12px" }}>
                      <span>👥 {job.applicants} Applicants</span>
                      <span>🕐 {job.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>{/* end center content */}

          {/* ══ RIGHT SIDEBAR ════════════════════════════ */}
          <div style={{ width: "200px", flexShrink: 0, display: "flex", flexDirection: "column", gap: "14px" }}>

            {/* Quick Actions card */}
            <div style={{ backgroundColor: white, borderRadius: "16px", padding: "18px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: "11px", fontWeight: "700", letterSpacing: "1px", textTransform: "uppercase", color: gray400, marginBottom: "14px" }}>Quick Actions</div>

              {/* 2x2 action grid */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>

                {/* New Job — navigates to post job form */}
                <button
                  onClick={onPostJob}
                  style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "6px", padding: "14px 8px", borderRadius: "12px", border: `1px solid ${gray200}`, backgroundColor: "#f8fafc", fontSize: "12px", fontWeight: "600", color: gray600 }}
                >
                  <span style={{ fontSize: "20px" }}>📝</span> New Job
                </button>

                {/* Add Team */}
                {/* TODO: onClick → navigate to team management page */}
                <button style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "6px", padding: "14px 8px", borderRadius: "12px", border: `1px solid ${gray200}`, backgroundColor: "#f8fafc", fontSize: "12px", fontWeight: "600", color: gray600 }}>
                  <span style={{ fontSize: "20px" }}>👥</span> Add Team
                </button>

                {/* Generate Report */}
                {/* TODO: onClick → POST /api/reports/generate → download PDF */}
                <button style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "6px", padding: "14px 8px", borderRadius: "12px", border: `1px solid ${gray200}`, backgroundColor: "#f8fafc", fontSize: "12px", fontWeight: "600", color: gray600 }}>
                  <span style={{ fontSize: "20px" }}>📊</span> Generate Report
                </button>

                {/* Ad Campaign */}
                {/* TODO: onClick → navigate to ad campaign creator */}
                <button style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "6px", padding: "14px 8px", borderRadius: "12px", border: `1px solid ${gray200}`, backgroundColor: "#f8fafc", fontSize: "12px", fontWeight: "600", color: gray600 }}>
                  <span style={{ fontSize: "20px" }}>📣</span> Ad Campaign
                </button>

              </div>
            </div>

            {/* AI Talent Insights dark card */}
            {/* TODO: Insights text → GET /api/ai/insights → replace static strings */}
            <div style={{ borderRadius: "16px", padding: "20px", background: "linear-gradient(160deg, #1a2520 0%, #0d3322 100%)", color: white }}>

              {/* Header */}
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", fontWeight: "700", color: "#22c55e", marginBottom: "16px" }}>
                <span>✦</span> AI Talent Insights
              </div>

              {/* Insight 1: Market Trend */}
              <div style={{ marginBottom: "16px" }}>
                <div style={{ fontSize: "10px", fontWeight: "700", letterSpacing: "0.8px", textTransform: "uppercase", color: "rgba(255,255,255,0.45)", marginBottom: "6px" }}>Market Trend</div>
                <p style={{ fontSize: "12px", color: "rgba(255,255,255,0.75)", lineHeight: 1.6 }}>
                  Demand for <span style={{ color: "#22c55e", fontWeight: "600" }}>Cloud Architects</span> in your region has increased by 18% this month.
                </p>
              </div>

              {/* Insight 2: Hiring Speed */}
              <div style={{ marginBottom: "18px" }}>
                <div style={{ fontSize: "10px", fontWeight: "700", letterSpacing: "0.8px", textTransform: "uppercase", color: "rgba(255,255,255,0.45)", marginBottom: "6px" }}>Hiring Speed</div>
                <p style={{ fontSize: "12px", color: "rgba(255,255,255,0.75)", lineHeight: 1.6 }}>
                  Your time-to-hire is <span style={{ color: "#22c55e", fontWeight: "600" }}>4 days faster</span> than the industry average.
                </p>
              </div>

              {/* CTA button */}
              {/* TODO: onClick → navigate to full AI Intelligence Suite page */}
              <button style={{ width: "100%", padding: "10px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.2)", backgroundColor: "rgba(255,255,255,0.08)", color: white, fontSize: "12px", fontWeight: "600" }}>
                Open Intelligence Suite
              </button>
            </div>

          </div>{/* end right sidebar */}

        </div>{/* end page body */}
      </div>{/* end main */}
    </div>
  );
}