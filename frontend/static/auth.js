(function () {
  const scriptUrl = document.currentScript ? document.currentScript.src : "";
  const baseUrl = scriptUrl ? new URL("..", scriptUrl) : new URL("./", window.location.href);
  const FRONTEND_ROOT =
    (baseUrl.origin || window.location.origin) +
    (baseUrl.pathname ? baseUrl.pathname.replace(/\/$/, "") : "");
  const LOGIN_PAGE = `${FRONTEND_ROOT}/index.html`;
  const USERS_PAGE = `${FRONTEND_ROOT}/users/list.html`;
  const TOKEN_KEY = "pm_token";
  const API_BASE_KEY = "pm_api_base";
  const API_BASE_DEFAULT = "http://localhost:5000";
  const API_BASE = localStorage.getItem(API_BASE_KEY) || API_BASE_DEFAULT;
  const refreshQueue = [];

  const renderers = {
    "users-list": renderUsersList,
    "projects-list": renderProjectsList,
    "project-header": renderProjectHeader,
    "tasks-list": renderTasksList,
    "form-status": renderFormStatus,
    "login-feedback": renderLoginFeedback,
    "task-prefill": renderTaskPrefill,
  };

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    if (!token) return;
    localStorage.setItem(TOKEN_KEY, token);
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  function buildApiUrl(path) {
    if (!path) return path;
    if (/^https?:\/\//i.test(path)) {
      return path;
    }
    const trimmedBase = API_BASE.replace(/\/+$/, "");
    return `${trimmedBase}${path}`;
  }

  function escapeHtml(raw) {
    return raw
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function buildPagination(meta, endpoint, targetId) {
    if (!meta || typeof meta.total !== "number" || meta.total <= meta.per_page) {
      return "";
    }
    const totalPages = Math.max(1, Math.ceil(meta.total / meta.per_page));
    const prevPage = Math.max(1, meta.page - 1);
    const nextPage = Math.min(totalPages, meta.page + 1);
    const prevDisabled = meta.page <= 1 ? " disabled" : "";
    const nextDisabled = meta.page >= totalPages ? " disabled" : "";
    return `
      <nav aria-label="Pagination" class="mt-3">
        <ul class="pagination mb-0">
          <li class="page-item${prevDisabled}">
            <button
              class="page-link"
              type="button"
              ${meta.page <= 1 ? "disabled" : ""}
              hx-get="${endpoint}?page=${prevPage}&per_page=${meta.per_page}"
              hx-target="#${targetId}"
              hx-swap="innerHTML"
            >Previous</button>
          </li>
          <li class="page-item disabled">
            <span class="page-link">Page ${meta.page} of ${totalPages}</span>
          </li>
          <li class="page-item${nextDisabled}">
            <button
              class="page-link"
              type="button"
              ${meta.page >= totalPages ? "disabled" : ""}
              hx-get="${endpoint}?page=${nextPage}&per_page=${meta.per_page}"
              hx-target="#${targetId}"
              hx-swap="innerHTML"
            >Next</button>
          </li>
        </ul>
      </nav>
    `;
  }

  function safeMeta(meta, fallbackLength) {
    if (!meta) {
      return { page: 1, per_page: fallbackLength || 0, total: fallbackLength || 0 };
    }
    return meta;
  }

  function renderUsersList(payload) {
    const collection = payload.data || [];
    const meta = safeMeta(payload.meta, collection.length);
    const rows =
      collection.length === 0
        ? `<tr><td colspan="4" class="text-center text-muted py-4">No users found.</td></tr>`
        : collection
            .map((user) => {
              const editUrl = `edit.html?id=${encodeURIComponent(user.id)}`;
              return `
                <tr>
                  <td>${escapeHtml(user.name || "")}</td>
                  <td>${escapeHtml(user.email || "")}</td>
                  <td><span class="badge bg-secondary text-uppercase">${escapeHtml(user.role || "")}</span></td>
                  <td class="text-end">
                    <a
                      class="btn btn-outline-secondary btn-sm me-2"
                      href="${editUrl}"
                      title="Edit user"
                      aria-label="Edit user"
                    >
                      <i class="bi bi-pencil"></i>
                    </a>
                    <button
                      class="btn btn-outline-danger btn-sm"
                      type="button"
                      hx-delete="/users/${encodeURIComponent(user.id)}"
                      hx-target="#users-alert"
                      hx-swap="innerHTML"
                      hx-confirm="Delete this user?"
                    >
                      <i class="bi bi-x-lg"></i>
                      <span class="visually-hidden">Delete user</span>
                    </button>
                  </td>
                </tr>`;
            })
            .join("");
    const pagination = buildPagination(meta, "/users", "users-list");
    return `
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1 class="h4 mb-0">Users</h1>
        <a class="btn btn-primary btn-sm" href="create.html">Create User</a>
      </div>
      <div
        id="users-alert"
        class="mb-3"
        data-render="form-status"
        data-refresh="#users-list"
        data-refresh-endpoint="/users?page=${meta.page}&per_page=${meta.per_page}"
      ></div>
      <div class="table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Email</th>
              <th scope="col">Role</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${pagination}
    `;
  }

  function renderProjectsList(payload) {
    const collection = payload.data || [];
    const meta = safeMeta(payload.meta, collection.length);
    const rows =
      collection.length === 0
        ? `<tr><td colspan="4" class="text-center text-muted py-4">No projects yet.</td></tr>`
        : collection
            .map((project) => {
              const detailUrl = `detail.html?id=${encodeURIComponent(project.id)}`;
              const editUrl = `edit.html?id=${encodeURIComponent(project.id)}`;
              return `
                <tr>
                  <td>
                    <a href="${detailUrl}" class="link-primary fw-semibold">${escapeHtml(project.name || "")}</a>
                  </td>
                  <td>${escapeHtml(project.description || "")}</td>
                  <td>${project.created_at ? new Date(project.created_at).toLocaleString() : ""}</td>
                  <td class="text-end">
                    <a
                      class="btn btn-outline-secondary btn-sm me-2"
                      href="${editUrl}"
                      title="Edit project"
                      aria-label="Edit project"
                    >
                      <i class="bi bi-pencil"></i>
                    </a>
                    <button
                      class="btn btn-outline-danger btn-sm"
                      type="button"
                      hx-delete="/projects/${encodeURIComponent(project.id)}"
                      hx-target="#projects-alert"
                      hx-swap="innerHTML"
                      hx-confirm="Delete this project?"
                    >
                      <i class="bi bi-x-lg"></i>
                      <span class="visually-hidden">Delete project</span>
                    </button>
                  </td>
                </tr>`;
            })
            .join("");
    const pagination = buildPagination(meta, "/projects", "projects-list");
    return `
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1 class="h4 mb-0">Projects</h1>
        <a class="btn btn-primary btn-sm" href="create.html">Create Project</a>
      </div>
      <div
        id="projects-alert"
        class="mb-3"
        data-render="form-status"
        data-refresh="#projects-list"
        data-refresh-endpoint="/projects?page=${meta.page}&per_page=${meta.per_page}"
      ></div>
      <div class="table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Description</th>
              <th scope="col">Created</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${pagination}
    `;
  }

  function renderProjectHeader(payload) {
    const project = payload.data || {};
    return `
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-3">
        <div>
          <h1 class="h4 mb-2">${escapeHtml(project.name || "Project")}</h1>
          <p class="mb-0 text-muted">${escapeHtml(project.description || "No description provided.")}</p>
        </div>
        <div class="text-end small text-muted">
          <div>Created: ${project.created_at ? new Date(project.created_at).toLocaleString() : "—"}</div>
          <div>Updated: ${project.updated_at ? new Date(project.updated_at).toLocaleString() : "—"}</div>
        </div>
      </div>
    `;
  }

  function renderTasksList(payload, target) {
    const projectId = target.dataset.projectId;
    const collection = payload.data || [];
    const meta = safeMeta(payload.meta, collection.length);
    const rows =
      collection.length === 0
        ? `<tr><td colspan="5" class="text-center text-muted py-4">No tasks found.</td></tr>`
        : collection
            .map((task) => {
              const editUrl = `../tasks/edit.html?id=${encodeURIComponent(task.id)}&projectId=${encodeURIComponent(projectId || "")}`;
              return `
                <tr>
                  <td>${escapeHtml(task.title || "")}</td>
                  <td>${escapeHtml(task.status || "")}</td>
                  <td>${task.due_date ? new Date(task.due_date).toLocaleDateString() : "—"}</td>
                  <td>${task.assigned_to != null ? escapeHtml(String(task.assigned_to)) : "—"}</td>
                  <td class="text-end">
                    <a class="btn btn-outline-secondary btn-sm" href="${editUrl}">Edit</a>
                  </td>
                </tr>`;
            })
            .join("");
    const pagination = buildPagination(meta, `/projects/${projectId}/tasks`, target.id);
    return `
      <div class="table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Status</th>
              <th scope="col">Due Date</th>
              <th scope="col">Assignee</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${pagination}
    `;
  }

  function renderFormStatus(payload, target, xhr) {
    const isError = xhr.status >= 400 || payload.error;
    const message =
      payload.message ||
      (isError ? "Request failed. Please review the errors and try again." : "Saved successfully.");
    const details =
      payload.messages && typeof payload.messages === "object"
        ? Object.entries(payload.messages)
            .map(([field, errors]) => `<li><strong>${escapeHtml(field)}:</strong> ${escapeHtml([].concat(errors).join(", "))}</li>`)
            .join("")
        : "";
    if (!isError) {
      const refreshTargetSelector = target.dataset.refresh;
      const refreshEndpoint = target.dataset.refreshEndpoint;
      if (refreshTargetSelector && refreshEndpoint) {
        enqueueRefresh(refreshTargetSelector, refreshEndpoint);
      }
      if (target.dataset.resetForm === "true") {
        const form = target.closest("form");
        if (form) {
          form.reset();
        }
      }
      const redirectUrl = target.dataset.redirect;
      if (redirectUrl) {
        window.setTimeout(() => {
          window.location.href = redirectUrl;
        }, 600);
      }
    }
    return `
      <div class="alert ${isError ? "alert-danger" : "alert-success"}" role="alert">
        <div>${escapeHtml(message)}</div>
        ${details ? `<ul class="mt-2 mb-0 small">${details}</ul>` : ""}
      </div>
    `;
  }

  function renderLoginFeedback(payload, _target, xhr) {
    const isError = xhr.status >= 400 || payload.error;
    const message =
      payload.message ||
      (isError ? "Login failed. Double-check your credentials." : "Login successful. Redirecting…");
    return `
      <div class="alert ${isError ? "alert-danger" : "alert-success"}" role="alert">
        ${escapeHtml(message)}
      </div>
    `;
  }

  function renderTaskPrefill(payload, target) {
    const taskId = target.dataset.taskId;
    const formSelector = target.dataset.prefillForm || "";
    const form = formSelector ? document.querySelector(formSelector) : null;
    if (!taskId || !form) {
      return `<div class="alert alert-warning" role="alert">Unable to load task details.</div>`;
    }

    const task = findTaskInPayload(payload, taskId);
    if (!task) {
      return `<div class="alert alert-warning" role="alert">Task ${escapeHtml(String(taskId))} not found.</div>`;
    }

    setFormField(form, "title", task.title || "");
    setFormField(form, "status", task.status || "todo");
    setFormField(form, "description", task.description || "");
    setFormField(form, "assigned_to", task.assigned_to != null ? String(task.assigned_to) : "");
    setFormField(form, "due_date", formatDateForInput(task.due_date));

    target.classList.add("d-none");
    return "";
  }

  function findTaskInPayload(payload, taskId) {
    const normalizedId = String(taskId);
    const pools = [];

    if (Array.isArray(payload)) {
      pools.push(payload);
    }

    if (payload && typeof payload === "object") {
      if (Array.isArray(payload.data)) {
        pools.push(payload.data);
      }
      if (payload.data && Array.isArray(payload.data.tasks)) {
        pools.push(payload.data.tasks);
      }
      if (Array.isArray(payload.tasks)) {
        pools.push(payload.tasks);
      }
    }

    for (const pool of pools) {
      const match = pool.find((item) => String(item.id) === normalizedId);
      if (match) {
        return match;
      }
    }
    return null;
  }

  function setFormField(form, name, value) {
    const input = form.querySelector(`[name="${name}"]`);
    if (input) {
      input.value = value ?? "";
    }
  }

  function formatDateForInput(value) {
    if (!value) return "";
    try {
      return value.slice(0, 10);
    } catch {
      return "";
    }
  }

  function enqueueRefresh(selector, endpoint) {
    refreshQueue.push({ selector, endpoint });
  }

  function refreshTarget(selector, endpoint) {
    if (!window.htmx) return;
    const element = document.querySelector(selector);
    if (!element) return;
    htmx.ajax("GET", endpoint, { target: element, swap: "innerHTML" });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const logoutButton = document.getElementById("logout-btn");
    if (logoutButton) {
      logoutButton.addEventListener("click", () => {
        clearToken();
        window.location.href = LOGIN_PAGE;
      });
    }
  });

  if (document.body) {
    document.body.addEventListener("htmx:configRequest", (event) => {
      const { detail } = event;
      const originalPath = detail.path || "";
      const verb = detail.verb ? detail.verb.toUpperCase() : "GET";
      const isLogin = /\/login$/.test(originalPath) && verb === "POST";

      detail.headers = detail.headers || {};
      if (isLogin) {
        const params = detail.parameters || {};
        const username = params.email || params.username || "";
        const password = params.password || "";
        const encoded = btoa(`${username}:${password}`);
        detail.headers["Authorization"] = `Basic ${encoded}`;
        detail.parameters = {};
      } else {
        const token = getToken();
        if (token) {
          detail.headers["Authorization"] = `Bearer ${token}`;
        }
      }

      detail.path = buildApiUrl(originalPath);
      detail.headers["Accept"] = "application/json";
      if (!isLogin && verb !== "GET") {
        detail.headers["Content-Type"] = "application/json";
      } else if (isLogin) {
        delete detail.headers["Content-Type"];
      }
    });

    document.body.addEventListener("htmx:beforeSwap", (event) => {
      const { detail } = event;
      const xhr = detail.xhr;
      if (!xhr) return;
      const contentType = xhr.getResponseHeader("Content-Type") || "";
      if (!contentType.includes("application/json")) return;
      let payload;
      try {
        payload = JSON.parse(xhr.responseText || "{}");
      } catch {
        return;
      }
      const target = detail.target;
      const rendererName = target && target.dataset ? target.dataset.render : null;
      if (rendererName && renderers[rendererName]) {
        detail.serverResponse = renderers[rendererName](payload, target, xhr);
        detail.shouldSwap = true;
        detail.isError = false;
      } else if (payload.message) {
        detail.serverResponse = `<div class="alert alert-info" role="alert">${escapeHtml(payload.message)}</div>`;
      }
    });

    document.body.addEventListener("htmx:afterSwap", () => {
      if (!refreshQueue.length) return;
      while (refreshQueue.length) {
        const { selector, endpoint } = refreshQueue.shift();
        refreshTarget(selector, endpoint);
      }
    });

    document.body.addEventListener("htmx:afterRequest", (event) => {
      const { detail } = event;
      const xhr = detail.xhr;
      if (!xhr) return;
      const path = detail.requestConfig ? detail.requestConfig.path || "" : "";
      if (path.endsWith("/login") && xhr.status === 200) {
        try {
          const payload = JSON.parse(xhr.responseText || "{}");
          const token = payload.access_token || payload.token || (payload.data && payload.data.token);
          if (token) {
            setToken(token);
            window.location.href = USERS_PAGE;
          }
        } catch {
          // ignore parse errors
        }
      }
    });

    document.body.addEventListener("htmx:responseError", (event) => {
      const { xhr } = event.detail;
      if (xhr && xhr.status === 401) {
        clearToken();
        if (!window.location.pathname.endsWith("/index.html")) {
          window.location.href = LOGIN_PAGE;
        }
      }
    });
  }

  window.pmAuth = {
    getToken,
    setToken,
    clearToken,
    buildApiUrl,
    FRONTEND_ROOT,
    LOGIN_PAGE,
    USERS_PAGE,
  };
})();
