const REFRESH_INTERVAL = 2000;
const MAX_NOTIFICATIONS = 50;
let staleTimeoutMinutes = 5;
let collapsedTeams = new Set();
let historyData = {};
let searchQuery = '';
let statusFilters = new Set(['working', 'idle', 'warning', 'error', 'stale']);
let previousStates = {};
let notifications = [];
let notificationPermission = 'default';
let currentData = null;

function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function formatDateTime(iso) {
    if (!iso) return 'Never';
    try {
        return new Date(iso).toLocaleString();
    } catch (e) {
        return 'Invalid date';
    }
}

function timeAgo(iso) {
    if (!iso) return 'Never';
    try {
        const ms = new Date() - new Date(iso);
        const mins = Math.floor(ms / 60000);
        const secs = Math.floor(ms / 1000);
        if (mins === 0) return `${secs} seconds ago`;
        if (mins === 1) return '1 minute ago';
        if (mins < 60) return `${mins} minutes ago`;
        const hrs = Math.floor(mins / 60);
        return hrs === 1 ? '1 hour ago' : `${hrs} hours ago`;
    } catch (e) {
        return 'Unknown';
    }
}

function toggleTeam(name) {
    collapsedTeams.has(name) ? collapsedTeams.delete(name) : collapsedTeams.add(name);
    renderDashboard();
}

function renderHistory(key, max = 20) {
    const hist = historyData[key] || [];
    if (hist.length === 0) return '<div class="history-empty">No history</div>';

    const recent = hist.slice(-max);
    const blocks = recent.map(e => {
        const ts = formatDateTime(e.timestamp);
        const ago = timeAgo(e.timestamp);
        const msg = escapeHtml(e.message || 'No message');
        const status = e.display_status || e.status || 'unknown';
        const label = e.display_label || status;
        const tip = `Status: ${label}&#10;Time: ${ago}&#10;Message: ${msg}&#10;Timestamp: ${ts}`;
        return `<div class="history-block ${status}" title="${tip}"></div>`;
    }).join('');

    return `<div class="history-timeline">${blocks}</div>`;
}

function renderRecentMessages(key, max = 5) {
    const hist = historyData[key] || [];
    if (hist.length === 0) return '<div class="recent-messages-empty">No recent messages</div>';

    const recent = hist.slice(-max).reverse();
    const items = recent.map(e => {
        const ago = timeAgo(e.timestamp);
        const msg = escapeHtml(e.message || 'No message');
        const status = e.display_status || e.status || 'unknown';
        const label = e.display_label || status;
        return `<div class="recent-message-item ${status}"><div class="recent-message-header"><span class="status-dot ${status}"></span><span class="recent-message-status">${label}</span><span class="recent-message-time">${ago}</span></div><div class="recent-message-text">${msg}</div></div>`;
    }).join('');

    return `<div class="recent-messages-list">${items}</div>`;
}

function render24hBreakdown(bd) {
    if (!bd) return '<div class="breakdown-empty">No breakdown data</div>';

    const entries = Object.entries(bd).filter(([_, p]) => p > 0).sort((a, b) => b[1] - a[1]);
    if (entries.length === 0) return '<div class="breakdown-empty">No data</div>';

    const labels = {working: 'Active', idle: 'Idle', warning: 'Warning', error: 'Error', offline: 'Offline'};
    const bars = entries.map(([st, pct]) => {
        const lbl = labels[st] || st;
        return `<div class="breakdown-bar-container"><div class="breakdown-label"><span class="status-dot ${st}"></span>${lbl}</div><div class="breakdown-bar-wrapper"><div class="breakdown-bar ${st}" style="width: ${pct}%"></div></div><div class="breakdown-percentage">${pct}%</div></div>`;
    }).join('');

    return `<div class="breakdown-24h">${bars}</div>`;
}

function renderAgentCard(ag) {
    const esc = s => escapeHtml(s).replace(/'/g, "\\'");
    return `<div class="agent-card ${ag.display_status}"><div class="agent-header"><div class="agent-id"><span class="status-dot ${ag.display_status}"></span><strong>${escapeHtml(ag.id)}</strong></div><div class="agent-header-actions"><button class="delete-btn" onclick="deleteAgent('${esc(ag.id)}', event)" title="Delete agent">✕</button><div class="status-badge ${ag.display_status}">${escapeHtml(ag.display_label)}</div></div></div><div class="agent-message">${escapeHtml(ag.status_message || 'No status message')}</div><div class="agent-recent-messages"><div class="recent-messages-label">Recent Messages:</div>${renderRecentMessages(ag.id)}</div><div class="agent-breakdown"><div class="breakdown-label-header">Last 24h Breakdown:</div>${render24hBreakdown(ag.breakdown_24h)}</div><div class="agent-history"><div class="history-label">History:</div>${renderHistory(ag.id)}</div><div class="agent-footer"><span class="checkin-time" title="${formatDateTime(ag.last_checkin)}">${timeAgo(ag.last_checkin)}</span></div></div>`;
}

function filterAgent(ag) {
    if (!statusFilters.has(ag.display_status)) return false;
    if (searchQuery && !ag.id.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
}

function renderDashboard() {
    if (!currentData) return;

    const cont = document.getElementById('agents-container');
    const teams = currentData.teams || [];
    const unassigned = currentData.unassigned_agents || [];
    const total = currentData.agents ? currentData.agents.length : 0;

    if (total === 0) {
        cont.innerHTML = '<div class="no-agents">No agents registered yet</div>';
        return;
    }

    let html = '';
    let visible = 0;

    teams.forEach(tm => {
        const filtered = tm.agents.filter(filterAgent);
        if (filtered.length === 0) return;

        visible += filtered.length;
        const collapsed = collapsedTeams.has(tm.name);
        const chevron = collapsed ? '▶' : '▼';
        const key = `team:${tm.name}`;
        const esc = s => escapeHtml(s).replace(/'/g, "\\'");

        html += `<div class="team-section"><div class="team-header ${tm.status}"><div class="team-info" onclick="toggleTeam('${esc(tm.name)}')"><span class="team-chevron">${chevron}</span><span class="status-dot ${tm.status}"></span><h2 class="team-name">${escapeHtml(tm.name)}</h2><span class="team-count">(${filtered.length} agent${filtered.length !== 1 ? 's' : ''})</span></div><div class="team-header-right"><button class="delete-btn team-delete-btn" onclick="deleteTeam('${esc(tm.name)}', event)" title="Delete team and all agents">✕</button><div class="status-badge ${tm.status}">${escapeHtml(tm.label)}</div></div></div><div class="team-history-section"><div class="history-label">Team History:</div>${renderHistory(key, 30)}</div><div class="team-agents ${collapsed ? 'collapsed' : ''}"><div class="agents-grid">${filtered.map(renderAgentCard).join('')}</div></div></div>`;
    });

    const filtUnassigned = unassigned.filter(filterAgent);
    if (filtUnassigned.length > 0) {
        visible += filtUnassigned.length;
        html += `<div class="team-section"><div class="team-header unassigned"><div class="team-info"><h2 class="team-name">Unassigned Agents</h2><span class="team-count">(${filtUnassigned.length} agent${filtUnassigned.length !== 1 ? 's' : ''})</span></div></div><div class="team-agents"><div class="agents-grid">${filtUnassigned.map(renderAgentCard).join('')}</div></div></div>`;
    }

    cont.innerHTML = visible === 0 ? '<div class="no-agents">No agents match the current filters</div>' : html;
}

async function updateHistory() {
    try {
        const resp = await fetch('/api/history');
        historyData = await resp.json();
    } catch (e) {
        console.error('Error fetching history:', e);
    }
}

async function updateAgents() {
    try {
        const [agResp, histResp] = await Promise.all([fetch('/api/agents'), fetch('/api/history')]);
        const data = await agResp.json();
        historyData = await histResp.json();

        const total = data.agents ? data.agents.length : 0;
        const counts = {working: 0, idle: 0, warning: 0, error: 0, stale: 0};

        if (data.agents) {
            data.agents.forEach(ag => {
                const st = ag.display_status;
                if (counts.hasOwnProperty(st)) counts[st]++;
            });
        }

        document.getElementById('agent-count').textContent = `${total} agent${total !== 1 ? 's' : ''}`;
        document.getElementById('last-update').textContent = `Last update: ${new Date().toLocaleTimeString()}`;

        Object.keys(counts).forEach(st => {
            const el = document.getElementById(`count-${st}`);
            if (el) el.textContent = `(${counts[st]})`;
        });

        if (data.agents) detectStateChanges(data.agents);

        currentData = data;
        renderDashboard();
    } catch (e) {
        console.error('Error fetching agents:', e);
        document.getElementById('agents-container').innerHTML = '<div class="error">Error loading agents. Retrying...</div>';
    }
}

function escapeHtml(txt) {
    const div = document.createElement('div');
    div.textContent = txt;
    return div.innerHTML;
}

async function deleteAgent(id, evt) {
    if (evt) evt.stopPropagation();
    if (!confirm(`Are you sure you want to delete agent "${id}"?`)) return;

    try {
        const resp = await fetch(`/api/agents/${encodeURIComponent(id)}`, {method: 'DELETE'});
        const res = await resp.json();
        if (res.success) await updateAgents();
        else alert(`Failed to delete agent: ${res.message}`);
    } catch (e) {
        console.error('Error deleting agent:', e);
        alert('Error deleting agent. Please try again.');
    }
}

async function deleteTeam(name, evt) {
    if (evt) evt.stopPropagation();

    const tm = currentData.teams.find(t => t.name === name);
    const cnt = tm ? tm.agent_count : 0;
    const msg = `Are you sure you want to delete team "${name}" and all ${cnt} agent${cnt !== 1 ? 's' : ''} in it?`;
    if (!confirm(msg)) return;

    try {
        const resp = await fetch(`/api/teams/${encodeURIComponent(name)}`, {method: 'DELETE'});
        const res = await resp.json();
        if (res.success) {
            collapsedTeams.delete(name);
            await updateAgents();
        } else {
            alert(`Failed to delete team: ${res.message}`);
        }
    } catch (e) {
        console.error('Error deleting team:', e);
        alert('Error deleting team. Please try again.');
    }
}

async function loadConfig() {
    try {
        const resp = await fetch('/api/config');
        const cfg = await resp.json();
        staleTimeoutMinutes = cfg.stale_timeout_minutes || 5;
    } catch (e) {
        console.error('Error loading config:', e);
    }
}

function setupEventListeners() {
    const search = document.getElementById('search-input');
    if (search) {
        search.addEventListener('input', e => {
            searchQuery = e.target.value.trim();
            renderDashboard();
        });
    }

    const checks = document.querySelectorAll('.status-filters input[type="checkbox"]');
    checks.forEach(cb => {
        cb.addEventListener('change', e => {
            const st = e.target.value;
            e.target.checked ? statusFilters.add(st) : statusFilters.delete(st);
            renderDashboard();
        });
    });
}

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(p => notificationPermission = p);
    } else if ('Notification' in window) {
        notificationPermission = Notification.permission;
    }
}

function loadNotifications() {
    try {
        const stored = localStorage.getItem('agent-notifications');
        if (stored) {
            notifications = JSON.parse(stored);
            updateNotificationBadge();
            renderNotificationList();
        }
    } catch (e) {
        console.error('Error loading notifications:', e);
        notifications = [];
    }
}

function saveNotifications() {
    try {
        if (notifications.length > MAX_NOTIFICATIONS) {
            notifications = notifications.slice(-MAX_NOTIFICATIONS);
        }
        localStorage.setItem('agent-notifications', JSON.stringify(notifications));
    } catch (e) {
        console.error('Error saving notifications:', e);
    }
}

function createNotification(aid, newSt, oldSt, msg) {
    const notif = {
        id: Date.now() + Math.random(),
        agentId: aid,
        newStatus: newSt,
        oldStatus: oldSt,
        message: msg,
        timestamp: new Date().toISOString(),
        read: false
    };

    notifications.unshift(notif);
    saveNotifications();
    updateNotificationBadge();
    renderNotificationList();

    if ('Notification' in window && Notification.permission === 'granted') {
        const title = `Agent ${aid}: ${newSt.toUpperCase()}`;
        const body = msg || `Status changed from ${oldSt} to ${newSt}`;

        try {
            const bn = new Notification(title, {
                body: body,
                icon: '/static/favicon.ico',
                tag: aid,
                requireInteraction: newSt === 'error'
            });
            bn.onclick = () => {
                window.focus();
                toggleNotificationPanel(true);
                bn.close();
            };
        } catch (e) {
            console.error('Error showing browser notification:', e);
        }
    }
}

function detectStateChanges(agents) {
    if (!agents || agents.length === 0) return;

    agents.forEach(ag => {
        const curr = ag.display_status;
        const prev = previousStates[ag.id];

        if (prev && prev !== curr) {
            if (curr === 'error' || curr === 'stale') {
                createNotification(ag.id, curr, prev, ag.status_message || `Agent transitioned to ${curr}`);
            }
        }

        previousStates[ag.id] = curr;
    });
}

function toggleNotificationPanel(forceOpen = false) {
    const panel = document.getElementById('notification-panel');
    const isHidden = panel.classList.contains('hidden');

    if (forceOpen || isHidden) {
        panel.classList.remove('hidden');
        notifications.forEach(n => n.read = true);
        saveNotifications();
        updateNotificationBadge();
        renderNotificationList();
    } else {
        panel.classList.add('hidden');
    }
}

function clearAllNotifications() {
    if (confirm('Clear all notifications?')) {
        notifications = [];
        saveNotifications();
        updateNotificationBadge();
        renderNotificationList();
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    const unread = notifications.filter(n => !n.read).length;

    if (unread > 0) {
        badge.textContent = unread > 99 ? '99+' : unread;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function renderNotificationList() {
    const list = document.getElementById('notification-list');

    if (notifications.length === 0) {
        list.innerHTML = '<div class="no-notifications">No notifications</div>';
        return;
    }

    list.innerHTML = notifications.map(n => {
        const ago = timeAgo(n.timestamp);
        const stClass = n.newStatus;
        const rdClass = n.read ? 'read' : 'unread';

        return `<div class="notification-item ${stClass} ${rdClass}"><div class="notification-header"><span class="status-dot ${stClass}"></span><strong>${escapeHtml(n.agentId)}</strong><span class="notification-time">${ago}</span></div><div class="notification-message">${escapeHtml(n.message)}</div><div class="notification-status-change">${escapeHtml(n.oldStatus)} → ${escapeHtml(n.newStatus)}</div></div>`;
    }).join('');
}

document.addEventListener('click', e => {
    const panel = document.getElementById('notification-panel');
    const btn = document.getElementById('notification-button');

    if (!panel.classList.contains('hidden') && !panel.contains(e.target) && !btn.contains(e.target)) {
        toggleNotificationPanel();
    }
});

initTheme();
loadConfig();
loadNotifications();
requestNotificationPermission();
updateAgents();
setInterval(updateAgents, REFRESH_INTERVAL);
setupEventListeners();
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
