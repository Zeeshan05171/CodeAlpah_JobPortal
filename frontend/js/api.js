/* ===========================================================
   JOBPORTAL — API CLIENT
   Thin wrapper around fetch() that attaches JWT auth headers,
   handles the DRF pagination envelope, and centralises the
   base URL so every page talks to the same backend.
   =========================================================== */

const API_BASE = (function () {
  // Same-origin by default; override by setting window.__JOBPORTAL_API__
  // before this script loads (see index.html for an example).
  if (window.__JOBPORTAL_API__) return window.__JOBPORTAL_API__;
  return "http://127.0.0.1:8000";
})();

const Storage = {
  getTokens() {
    const raw = localStorage.getItem("jp_tokens");
    return raw ? JSON.parse(raw) : null;
  },
  setTokens(tokens) {
    localStorage.setItem("jp_tokens", JSON.stringify(tokens));
  },
  clearTokens() {
    localStorage.removeItem("jp_tokens");
    localStorage.removeItem("jp_user");
  },
  getUser() {
    const raw = localStorage.getItem("jp_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(user) {
    localStorage.setItem("jp_user", JSON.stringify(user));
  },
};

async function apiRequest(path, { method = "GET", body, isForm = false, auth = true, params } = {}) {
  let url = `${API_BASE}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    if (qs) url += `?${qs}`;
  }

  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";

  if (auth) {
    const tokens = Storage.getTokens();
    if (tokens?.access) headers["Authorization"] = `Bearer ${tokens.access}`;
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  // Transparent token refresh on 401
  if (res.status === 401 && auth) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const tokens = Storage.getTokens();
      headers["Authorization"] = `Bearer ${tokens.access}`;
      const retry = await fetch(url, { method, headers, body: body ? (isForm ? body : JSON.stringify(body)) : undefined });
      return parseResponse(retry);
    }
  }

  return parseResponse(res);
}

async function parseResponse(res) {
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok) {
    const error = new Error(extractErrorMessage(data) || `Request failed (${res.status})`);
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
}

function extractErrorMessage(data) {
  if (!data) return null;
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  const firstKey = Object.keys(data)[0];
  if (firstKey) {
    const val = data[firstKey];
    const msg = Array.isArray(val) ? val[0] : val;
    return `${firstKey === "non_field_errors" ? "" : firstKey + ": "}${msg}`;
  }
  return null;
}

async function tryRefreshToken() {
  const tokens = Storage.getTokens();
  if (!tokens?.refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/api/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh }),
    });
    if (!res.ok) throw new Error("refresh failed");
    const data = await res.json();
    Storage.setTokens({ ...tokens, access: data.access });
    return true;
  } catch (e) {
    Storage.clearTokens();
    return false;
  }
}

/* ---------------------------------------------------------
   Domain-specific helpers
   --------------------------------------------------------- */

const Auth = {
  isLoggedIn() {
    return !!Storage.getTokens()?.access;
  },
  currentUser() {
    return Storage.getUser();
  },
  async register(payload) {
    const data = await apiRequest("/api/auth/register/", { method: "POST", body: payload, auth: false });
    Storage.setTokens(data.tokens);
    Storage.setUser(data.user);
    return data.user;
  },
  async login(username, password) {
    const data = await apiRequest("/api/auth/login/", { method: "POST", body: { username, password }, auth: false });
    Storage.setTokens(data.tokens);
    Storage.setUser(data.user);
    return data.user;
  },
  async refreshMe() {
    const user = await apiRequest("/api/auth/me/");
    Storage.setUser(user);
    return user;
  },
  logout() {
    Storage.clearTokens();
    window.location.href = "index.html";
  },
};

const JobsAPI = {
  list(params) {
    return apiRequest("/api/listings/", { params, auth: false });
  },
  myJobs(params) {
    return apiRequest("/api/listings/my_jobs/", { params });
  },
  get(slug) {
    return apiRequest(`/api/listings/${slug}/`, { auth: Auth.isLoggedIn() });
  },
  create(payload) {
    return apiRequest("/api/listings/", { method: "POST", body: payload });
  },
  update(slug, payload) {
    return apiRequest(`/api/listings/${slug}/`, { method: "PATCH", body: payload });
  },
  remove(slug) {
    return apiRequest(`/api/listings/${slug}/`, { method: "DELETE" });
  },
  applicants(slug) {
    return apiRequest(`/api/listings/${slug}/applicants/`);
  },
};

const ResumesAPI = {
  list() {
    return apiRequest("/api/resumes/");
  },
  upload(formData) {
    return apiRequest("/api/resumes/", { method: "POST", body: formData, isForm: true });
  },
  remove(id) {
    return apiRequest(`/api/resumes/${id}/`, { method: "DELETE" });
  },
};

const ApplicationsAPI = {
  mine() {
    return apiRequest("/api/applications/");
  },
  apply(payload) {
    return apiRequest("/api/applications/", { method: "POST", body: payload });
  },
  updateStatus(id, status) {
    return apiRequest(`/api/applications/${id}/status_update/`, { method: "PATCH", body: { status } });
  },
};

const NotificationsAPI = {
  list() {
    return apiRequest("/api/notifications/");
  },
  markRead(id) {
    return apiRequest(`/api/notifications/${id}/mark_read/`, { method: "PATCH" });
  },
  markAllRead() {
    return apiRequest(`/api/notifications/mark_all_read/`, { method: "PATCH" });
  },
};

const StatsAPI = {
  employer() {
    return apiRequest("/api/stats/employer/");
  },
};

const ProfileAPI = {
  employer(payload) {
    if (payload) return apiRequest("/api/auth/profile/employer/", { method: "PATCH", body: payload });
    return apiRequest("/api/auth/profile/employer/");
  },
  candidate(payload) {
    if (payload) return apiRequest("/api/auth/profile/candidate/", { method: "PATCH", body: payload });
    return apiRequest("/api/auth/profile/candidate/");
  },
};
