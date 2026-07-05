/* ===========================================================
   JOBPORTAL — SHARED UI LOGIC
   Renders the nav bar based on auth/role state, wires up the
   notifications dropdown, and holds small formatting helpers
   reused across every page.
   =========================================================== */

const JOB_TYPE_LABELS = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  internship: "Internship",
  remote: "Remote",
};

const EXPERIENCE_LABELS = {
  entry: "Entry level",
  mid: "Mid level",
  senior: "Senior level",
  lead: "Lead / Principal",
};

const STATUS_LABELS = {
  pending: "Pending",
  reviewed: "Reviewed",
  shortlisted: "Shortlisted",
  interview: "Interview",
  accepted: "Accepted",
  rejected: "Rejected",
};

function escapeHtml(str = "") {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatSalary(min, max) {
  if (!min && !max) return "Salary not disclosed";
  const fmt = (n) => `PKR ${Number(n).toLocaleString()}`;
  if (min && max) return `${fmt(min)} – ${fmt(max)}`;
  return fmt(min || max);
}

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

function companyInitials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

function toast(msg, type = "success") {
  let el = document.getElementById("jp-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "jp-toast";
    el.style.cssText = `
      position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
      z-index:200; padding:13px 22px; border-radius:8px; font-family:'Space Grotesk',sans-serif;
      font-size:.9rem; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,.25); transition:opacity .25s ease;
    `;
    document.body.appendChild(el);
  }
  el.style.background = type === "error" ? "#C1553C" : "#2F6F5E";
  el.style.color = "#fff";
  el.textContent = msg;
  el.style.opacity = "1";
  clearTimeout(el._t);
  el._t = setTimeout(() => (el.style.opacity = "0"), 3200);
}

/* ---------------------------------------------------------
   Nav bar rendering
   --------------------------------------------------------- */
function renderNav(activePage) {
  const mount = document.getElementById("topnav");
  if (!mount) return;

  const user = Auth.currentUser();
  const loggedIn = Auth.isLoggedIn();

  const links = [
    { href: "index.html", label: "Home", key: "home" },
    { href: "jobs.html", label: "Browse jobs", key: "jobs" },
  ];
  if (loggedIn && user?.role === "employer") {
    links.push({ href: "employer-dashboard.html", label: "Employer dashboard", key: "employer" });
  }
  if (loggedIn && user?.role === "candidate") {
    links.push({ href: "candidate-dashboard.html", label: "My applications", key: "candidate" });
  }

  const linkHtml = links
    .map(
      (l) => `<a href="${l.href}" class="${activePage === l.key ? "active" : ""}">${l.label}</a>`
    )
    .join("");

  const rightHtml = loggedIn
    ? `
      <button class="notif-btn" id="notifBtn" aria-label="Notifications">
        🔔<span class="notif-dot" id="notifDot"></span>
      </button>
      <div class="notif-panel" id="notifPanel"></div>
      <a href="${user.role === "employer" ? "employer-dashboard.html" : "candidate-dashboard.html"}" class="btn btn-outline-light btn-sm">${escapeHtml(user.username)}</a>
      <button class="btn btn-primary btn-sm" id="logoutBtn">Log out</button>
    `
    : `
      <a href="login.html" class="btn btn-outline-light btn-sm">Log in</a>
      <a href="register.html" class="btn btn-primary btn-sm">Get started</a>
    `;

  mount.innerHTML = `
    <div class="topnav-inner">
      <a href="index.html" class="brand">JobPortal <span class="tag">PK</span></a>
      <nav class="navlinks">${linkHtml}</nav>
      <div class="nav-right">${rightHtml}</div>
    </div>
  `;

  if (loggedIn) {
    document.getElementById("logoutBtn").addEventListener("click", () => Auth.logout());
    wireNotifications();
  }
}

async function wireNotifications() {
  const btn = document.getElementById("notifBtn");
  const panel = document.getElementById("notifPanel");
  const dot = document.getElementById("notifDot");
  if (!btn) return;

  async function load() {
    try {
      const data = await NotificationsAPI.list();
      const items = data.results || data;
      const unread = items.filter((n) => !n.is_read).length;
      dot.classList.toggle("show", unread > 0);
      panel.innerHTML = items.length
        ? items
            .slice(0, 8)
            .map(
              (n) => `
              <div class="notif-item ${n.is_read ? "" : "unread"}" data-id="${n.id}">
                <div>${escapeHtml(n.message)}</div>
                <div class="t">${timeAgo(n.created_at)}</div>
              </div>`
            )
            .join("")
        : `<div class="notif-item">No notifications yet.</div>`;
    } catch (e) {
      panel.innerHTML = `<div class="notif-item">Couldn't load notifications.</div>`;
    }
  }

  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) {
      await load();
      NotificationsAPI.markAllRead().then(() => dot.classList.remove("show"));
    }
  });
  document.addEventListener("click", (e) => {
    if (!panel.contains(e.target) && e.target !== btn) panel.classList.remove("open");
  });

  load();
}

/* Redirect helpers used by dashboard pages */
function requireAuth(role) {
  if (!Auth.isLoggedIn()) {
    window.location.href = "login.html";
    return false;
  }
  const user = Auth.currentUser();
  if (role && user?.role !== role) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}
