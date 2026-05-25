const form      = document.querySelector("#chat-form");
const input     = document.querySelector("#message-input");
const messages  = document.querySelector("#messages");
const statusEl  = document.querySelector("#status");
const welcome   = document.querySelector("#welcome");

// Gemini-style star SVG for assistant avatar
const STAR_SVG = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2C12 2 12.5 7.5 15 10C17.5 12.5 23 12 23 12C23 12 17.5 11.5 15 14C12.5 16.5 12 22 12 22C12 22 11.5 16.5 9 14C6.5 11.5 1 12 1 12C1 12 6.5 12.5 9 10C11.5 7.5 12 2 12 2Z" fill="white"/>
</svg>`;

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
  if (role === "assistant") {
    avatar.innerHTML = STAR_SVG;
  } else {
    avatar.textContent = "You";
  }
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

  if (sources.length > 0) {
    const sourceList = document.createElement("ol");
    sourceList.className = "sources";
    for (const s of sources) {
      const li = document.createElement("li");
      const pages = s.page_start ? `, pp. ${s.page_start}–${s.page_end}` : "";
      li.textContent = `${s.title} (${s.filename}${pages})`;
      sourceList.appendChild(li);
    }
    body.appendChild(sourceList);
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
  avatar.innerHTML = STAR_SVG;
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
      body: JSON.stringify({ message: text }),
    });
    const payload = await resp.json();
    thinking.remove();

    if (!resp.ok) {
      addMessage("assistant", payload.error || "Something went wrong.");
      return;
    }
    if (payload.blocked) {
      addMessage("assistant", `${payload.relevance.reason}\n\nTry: ${payload.relevance.suggested_rewrite}`);
      return;
    }
    addMessage("assistant", payload.answer, payload.sources || [], payload.schedule_insight || null);
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
