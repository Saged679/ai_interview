// ============================================================
// App.js — ROUTER WITH BROWSER HISTORY
// ============================================================
//
// HOW IT WORKS:
// Instead of just useState, we now use TWO things together:
//
//   1. useState         → tells React which page to SHOW
//   2. history.pushState → tells the BROWSER to record a step
//                          in its history (so back button works)
//
// When the user clicks the browser Back button:
//   → browser fires the "popstate" event
//   → we listen for it with useEffect
//   → we read which page to show from the URL state
//   → we call setCurrentPage() to update the screen
//
// NAVIGATION MAP:
//   "home"         → IntelliviewLogin
//   "talent"       → TalentLogin
//   "feed"         → MainJobFeed
//   "enterprise"   → EnterpriseLogin
//   "orgDashboard" → OrganizationDashboard
//   "portal"       → EnterprisePortal
//
// ============================================================

import { useState, useEffect } from "react";

import IntelliviewLogin      from "./screens/IntelliviewLogin";
import TalentLogin           from "./screens/user/TalentLogin";
import MainJobFeed           from "./screens/user/MainJobFeed";
import EnterpriseLogin       from "./screens/organisation/EnterpriseLogin";
import OrganizationDashboard from "./screens/organisation/OrganizationDashBoard";
import EnterprisePortal      from "./screens/organisation/EnterprisePortal";

export default function App() {

  // ── Current page state ────────────────────────────────────
  // Start on "home", but check if the browser already has a
  // saved page in history (e.g. user refreshed mid-session)
  const [currentPage, setCurrentPage] = useState(() => {
    // window.history.state holds the page we saved via pushState
    // If it exists, restore it — otherwise start at "home"
    return window.history.state?.page || "home";
  });

  // ── Listen for browser Back / Forward button ──────────────
  useEffect(() => {
    // This function runs every time the user clicks Back or Forward
    const handlePopState = (event) => {
      // event.state is what we saved with pushState
      // If it has a page, go there — otherwise fall back to home
      const page = event.state?.page || "home";
      setCurrentPage(page);  // update React to show the right screen
    };

    // Register the listener when the component mounts
    window.addEventListener("popstate", handlePopState);

    // Clean up the listener when the component unmounts
    return () => window.removeEventListener("popstate", handlePopState);
  }, []); // empty [] = only run once on mount

  // ── Navigate function ─────────────────────────────────────
  // Call this instead of setCurrentPage directly.
  // It BOTH updates React state AND pushes to browser history.
  const navigate = (page) => {
    // pushState(stateObject, title, url)
    // - stateObject: we store { page } so popstate can read it
    // - title: ignored by most browsers, pass ""
    // - url: shown in the address bar (optional, keeps it clean)
    window.history.pushState({ page }, "", `#${page}`);

    // Then update React so the new screen renders
    setCurrentPage(page);
  };

  // ── Render the correct page ───────────────────────────────
  switch (currentPage) {

    case "talent":
      return (
        <TalentLogin
          onBack={() => navigate("home")}
          onSkip={() => navigate("feed")}
        />
      );

    case "feed":
      return <MainJobFeed onBack={() => navigate("home")} />;

    case "enterprise":
      return (
        <EnterpriseLogin
          onBack={() => navigate("home")}
          onSkip={() => navigate("orgDashboard")}
        />
      );

    case "orgDashboard":
      return (
        <OrganizationDashboard
          onBack={() => navigate("enterprise")}
          onPostJob={() => navigate("portal")}
        />
      );

    case "portal":
      return (
        <EnterprisePortal
          onBack={() => navigate("orgDashboard")}
        />
      );

    default: // "home"
      return (
        <IntelliviewLogin
          onGetStarted={() => navigate("talent")}
          onEnterprise={() => navigate("enterprise")}
        />
      );
  }
}