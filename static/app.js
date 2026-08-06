/**
 * チャットボット Web UI のフロントエンドロジック。
 */

const chatContainer = document.getElementById("chat-container");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const clearButton = document.getElementById("clear-button");
const statusBadge = document.getElementById("status-badge");

let sessionId = null;
let isSending = false;

function addMessage(role, content, extraClass = "", sources = []) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}${extraClass ? ` ${extraClass}` : ""}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  wrapper.appendChild(bubble);

  if (sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";
    sourcesEl.innerHTML = "<div class=\"sources-title\">参照した資料</div>";

    sources.forEach((src) => {
      const item = document.createElement("div");
      item.className = "source-item";
      item.innerHTML = `<span class="source-name">${src.source}</span>（スコア: ${src.score}）<br>${src.snippet}`;
      sourcesEl.appendChild(item);
    });

    wrapper.appendChild(sourcesEl);
  }

  chatContainer.appendChild(wrapper);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  return wrapper;
}

function removeMessage(element) {
  if (element && element.parentNode) {
    element.parentNode.removeChild(element);
  }
}

function formatBackendLabel(data) {
  if (data.backend === "openai_rag") {
    return `RAG + OpenAI (${data.model})`;
  }
  if (data.backend === "rule_rag") {
    return `RAG + ルール (${data.rag_retriever})`;
  }
  if (data.backend === "openai") {
    return `OpenAI (${data.model})`;
  }
  return "ルールベース";
}

async function fetchHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("health check failed");
    const data = await response.json();
    statusBadge.textContent = formatBackendLabel(data);
    statusBadge.className = "status online";
  } catch {
    statusBadge.textContent = "接続エラー";
    statusBadge.className = "status error";
  }
}

async function sendMessage(message) {
  if (isSending) return;
  isSending = true;
  sendButton.disabled = true;
  messageInput.disabled = true;

  addMessage("user", message);
  const loadingEl = addMessage("assistant", "考え中...", "loading");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "リクエストに失敗しました");
    }

    sessionId = data.session_id;
    removeMessage(loadingEl);
    addMessage("assistant", data.reply, "", data.sources || []);
  } catch (error) {
    removeMessage(loadingEl);
    addMessage("assistant", `エラー: ${error.message}`, "error");
  } finally {
    isSending = false;
    sendButton.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
  }
}

async function clearConversation() {
  if (sessionId) {
    try {
      await fetch(`/api/session/${sessionId}`, { method: "DELETE" });
    } catch {
      // セッション削除に失敗しても UI はリセットする
    }
  }

  sessionId = null;
  chatContainer.innerHTML = "";
  addMessage(
    "assistant",
    "会話をクリアしました。霧晶の王国について質問してください。"
  );
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  messageInput.value = "";
  sendMessage(message);
});

clearButton.addEventListener("click", clearConversation);

fetchHealth();
messageInput.focus();
