const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const statusBadge = document.querySelector("#status");

function addMessage(role, text, sources = [], scheduleInsight = null) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  article.appendChild(bubble);

  if (scheduleInsight) {
    const insight = document.createElement("div");
    insight.className = "schedule-insight";
    // Render **bold** markers
    insight.innerHTML = scheduleInsight
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
    article.appendChild(insight);
  }

  if (sources.length > 0) {
    const sourceList = document.createElement("ol");
    sourceList.className = "sources";
    for (const source of sources) {
      const item = document.createElement("li");
      const pages = source.page_start
        ? `, pages ${source.page_start}-${source.page_end}`
        : "";
      item.textContent = `${source.title} (${source.filename}${pages})`;
      sourceList.appendChild(item);
    }
    article.appendChild(sourceList);
  }

  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

async function checkHealth() {
  const response = await fetch("/api/health");
  const health = await response.json();
  statusBadge.textContent = health.database_ready ? "Database ready" : "Run ingest.py";
  statusBadge.classList.toggle("ready", health.database_ready);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";
  input.focus();

  const pending = document.createElement("article");
  pending.className = "message assistant";
  pending.innerHTML = '<div class="bubble">Thinking...</div>';
  messages.appendChild(pending);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const payload = await response.json();
    pending.remove();

    if (!response.ok) {
      addMessage("assistant", payload.error || "Request failed.");
      return;
    }

    if (payload.blocked) {
      addMessage(
        "assistant",
        `${payload.relevance.reason} Try: ${payload.relevance.suggested_rewrite}`
      );
      return;
    }

    addMessage("assistant", payload.answer, payload.sources || [], payload.schedule_insight || null);
  } catch (error) {
    pending.remove();
    addMessage("assistant", "The request could not be completed. Check the server logs.");
  }
});

checkHealth();

