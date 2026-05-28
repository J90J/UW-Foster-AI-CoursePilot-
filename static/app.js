const form      = document.querySelector("#chat-form");
const input     = document.querySelector("#message-input");
const messages  = document.querySelector("#messages");
const statusEl  = document.querySelector("#status");
const welcome   = document.querySelector("#welcome");

const history = []; // {role, content} — kept in memory for the session

const ASSISTANT_LABEL = "AI";
const USER_LABEL = "You";

function hideWelcome() {
  if (welcome) welcome.style.display = "none";
}

function addMessage(role, text, sources = [], scheduleInsight = null) {
  hideWelcome();

  const article = document.createElement("article");
  article.className = `message ${role}`;

  // Avatar
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "assistant" ? ASSISTANT_LABEL : USER_LABEL;
  article.appendChild(avatar);

  // Body
  const body = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  body.appendChild(bubble);

  if (scheduleInsight) {
    const insight = document.createElement("div");
    insight.className = "schedule-insight";
    insight.innerHTML = scheduleInsight
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
    body.appendChild(insight);
  }


  article.appendChild(body);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function addThinking() {
  hideWelcome();
  const article = document.createElement("article");
  article.className = "message assistant";
  article.id = "thinking";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = ASSISTANT_LABEL;
  article.appendChild(avatar);

  const body = document.createElement("div");
  body.className = "msg-body";
  const bubble = document.createElement("div");
  bubble.className = "bubble thinking";
  bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  body.appendChild(bubble);
  article.appendChild(body);

  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

async function sendMessage(text) {
  addMessage("user", text);
  const thinking = addThinking();

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history }),
    });
    const payload = await resp.json();
    thinking.remove();

    if (!resp.ok) {
      addMessage("assistant", payload.error || "Something went wrong.");
      return;
    }
    if (payload.blocked) {
      const reply = `${payload.relevance.reason}\n\nTry: ${payload.relevance.suggested_rewrite}`;
      addMessage("assistant", reply);
      // Still track blocked exchanges so context isn't lost
      history.push({ role: "user", content: text });
      history.push({ role: "assistant", content: reply });
      return;
    }
    history.push({ role: "user", content: text });
    history.push({ role: "assistant", content: payload.answer });
    addMessage("assistant", payload.answer, [], payload.schedule_insight || null);
  } catch {
    thinking.remove();
    addMessage("assistant", "Could not reach the server. Check that app.py is running.");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  input.style.height = "auto";
  input.focus();
  await sendMessage(text);
});

// Auto-resize textarea
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 130) + "px";
});

// Suggestion chips
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    input.value = chip.textContent;
    input.dispatchEvent(new Event("input"));
    form.requestSubmit();
  });
});

// Health check
async function checkHealth() {
  const resp = await fetch("/api/health");
  const data = await resp.json();
  statusEl.textContent = data.database_ready ? "Ready" : "Run ingest.py";
  statusEl.classList.toggle("ready", data.database_ready);
}

checkHealth();
