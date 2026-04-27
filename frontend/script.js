const API_URL = "http://127.0.0.1:8000/chat";
const STORAGE_KEY = "ai_recipe_chat_sessions";

const state = {
    sessions: [],
    activeSessionId: null
};

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");
const historyList = document.getElementById("chat-history");
const newChatBtn = document.getElementById("new-chat-btn");
const toggleSidebarBtn = document.getElementById("toggle-sidebar");
const sidebar = document.getElementById("sidebar");

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function uid() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function saveSessions() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.sessions));
}

function loadSessions() {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        state.sessions = Array.isArray(saved) ? saved : [];
    } catch {
        state.sessions = [];
    }

    if (!state.sessions.length) {
        createNewSession();
        return;
    }

    state.activeSessionId = state.sessions[0].id;
    renderHistory();
    renderActiveSession();
}

function getActiveSession() {
    return state.sessions.find((session) => session.id === state.activeSessionId);
}

function getSessionTitle(text) {
    const normalized = text.trim();
    return normalized.length > 36 ? `${normalized.slice(0, 36)}...` : normalized;
}

function createNewSession() {
    const session = {
        id: uid(),
        title: "New Chat",
        createdAt: Date.now(),
        messages: []
    };

    state.sessions.unshift(session);
    state.activeSessionId = session.id;
    saveSessions();
    renderHistory();
    renderActiveSession();
    input.focus();
}

function deleteSession(sessionId) {
    const index = state.sessions.findIndex((s) => s.id === sessionId);
    if (index === -1) {
        return;
    }

    state.sessions.splice(index, 1);
    saveSessions();

    if (state.activeSessionId === sessionId) {
        if (state.sessions.length > 0) {
            state.activeSessionId = state.sessions[0].id;
        } else {
            createNewSession();
            return;
        }
    }

    renderHistory();
    renderActiveSession();
}

function renderHistory() {
    historyList.innerHTML = "";

    state.sessions.forEach((session) => {
        const item = document.createElement("li");
        const btn = document.createElement("button");

        btn.type = "button";
        btn.className = `chat-history-item ${session.id === state.activeSessionId ? "active" : ""}`;

        const titleSpan = document.createElement("span");
        titleSpan.className = "chat-history-item-title";
        titleSpan.innerHTML = `<i class="fa-regular fa-message"></i> ${escapeHtml(session.title)}`;

        btn.appendChild(titleSpan);

        btn.addEventListener("click", (e) => {
            if (e.target.closest(".chat-history-item-delete")) {
                return;
            }
            state.activeSessionId = session.id;
            renderHistory();
            renderActiveSession();
            sidebar.classList.remove("open");
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "chat-history-item-delete";
        deleteBtn.title = "Delete chat";
        deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        deleteBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            deleteSession(session.id);
        });

        btn.appendChild(deleteBtn);
        item.appendChild(btn);
        historyList.appendChild(item);
    });
}

function appendMessageBubble(role, html) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = html;

    row.appendChild(bubble);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function renderActiveSession() {
    chatBox.innerHTML = "";
    const session = getActiveSession();

    if (!session || !session.messages.length) {
        chatBox.innerHTML = `
            <div class="empty-state">
                <h2>Ask for recipes, ingredients, and cooking steps.</h2>
                <p>Try: "I have paneer, onion and tomato. What can I cook?"</p>
            </div>
        `;
        return;
    }

    session.messages.forEach((message) => {
        appendMessageBubble(message.role, message.html);
    });
}

function parseSection(text, name) {
    const regex = new RegExp(`${name}:(.*?)(?=\\n[A-Za-z ]+:|$)`, "is");
    const match = text.match(regex);
    return match ? match[1].trim() : "";
}

function normalizeLines(block) {
    return block
        .split("\n")
        .map((line) => line.replace(/^[-*\d.)\s]+/, "").trim())
        .filter(Boolean);
}

function normalizeMissing(missingText) {
    if (!missingText || /^none$/i.test(missingText.trim())) {
        return [];
    }

    return missingText
        .split(/[\n,]/)
        .map((item) => item.replace(/^[-*\s]+/, "").trim())
        .filter(Boolean);
}

function buildBotResponse(answer) {
    const lower = answer.toLowerCase();
    if (lower.includes("out of domain")) {
        return `<p>${escapeHtml(answer)}</p>`;
    }

    const recipeName = parseSection(answer, "Recipe Name") || "Suggested Recipe";
    const ingredients = normalizeLines(parseSection(answer, "Ingredients"));
    const steps = normalizeLines(parseSection(answer, "Steps"));
    const missing = normalizeMissing(parseSection(answer, "Missing Ingredients"));

    const missingSet = new Set(missing.map((item) => item.toLowerCase()));

    const ingredientList = ingredients.length
        ? ingredients
              .map((item) => {
                  const isMissing = missingSet.has(item.toLowerCase());
                  const cls = isMissing ? "ingredient-missing" : "ingredient-available";
                  return `<li class="${cls}">${escapeHtml(item)}</li>`;
              })
              .join("")
        : `<li>${escapeHtml("No ingredient details available")}</li>`;

    const stepList = steps.length
        ? steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")
        : `<li>${escapeHtml("No preparation steps available")}</li>`;

    const missingBlock = missing.length
        ? `
            <h4>Missing Ingredients</h4>
            <ul>
                ${missing.map((item) => `<li class="ingredient-missing">${escapeHtml(item)}</li>`).join("")}
            </ul>
        `
        : "";

    return `
        <div class="bot-card">
            <h3>${escapeHtml(recipeName)}</h3>
            <h4>Ingredients</h4>
            <ul>${ingredientList}</ul>
            <h4>Steps</h4>
            <ol>${stepList}</ol>
            ${missingBlock}
        </div>
    `;
}

function createThinkingRow() {
    const row = document.createElement("div");
    row.className = "message-row bot";
    row.innerHTML = `
        <div class="bubble">
            <div class="thinking">
                <span class="spinner"></span>
                Thinking...
            </div>
        </div>
    `;
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
    return row;
}

async function sendMessage() {
    const message = input.value.trim();
    if (!message) {
        return;
    }

    const session = getActiveSession();
    if (!session) {
        createNewSession();
    }

    const active = getActiveSession();
    if (active.title === "New Chat") {
        active.title = getSessionTitle(message);
    }

    const userHtml = `<p>${escapeHtml(message)}</p>`;
    active.messages.push({ role: "user", html: userHtml });
    input.value = "";
    renderHistory();
    renderActiveSession();
    const thinkingRow = createThinkingRow();
    saveSessions();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: message })
        });

        if (!response.ok) {
            throw new Error("Request failed");
        }

        const data = await response.json();
        const botHtml = buildBotResponse(data.answer || "No response received.");

        thinkingRow.remove();
        active.messages.push({ role: "bot", html: botHtml });
        appendMessageBubble("bot", botHtml);
        saveSessions();
    } catch {
        thinkingRow.remove();
        const errorHtml = "<p>Error: server not responding. Please check if backend is running.</p>";
        active.messages.push({ role: "bot", html: errorHtml });
        appendMessageBubble("bot", errorHtml);
        saveSessions();
    }
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

newChatBtn.addEventListener("click", createNewSession);

toggleSidebarBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
});

loadSessions();