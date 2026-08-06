/**
 * チャットボット Web UI のフロントエンドロジック。
 *
 * やっていること:
 * 1. ユーザーがフォームに入力して送信
 * 2. POST /api/chat にメッセージと session_id を送る
 * 3. 返ってきた reply を画面に表示
 * 4. session_id を保持して、次のメッセージでも同じ会話を続ける
 */

const chatContainer = document.getElementById("chat-container");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const clearButton = document.getElementById("clear-button");
const statusBadge = document.getElementById("status-badge");

let sessionId = null;
let isSending = false;

function addMessage(role, content, extraClass = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}${extraClass ? ` ${extraClass}` : ""}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  wrapper.appendChild(bubble);
  chatContainer.appendChild(wrapper);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  return wrapper;
}

function removeMessage(element) {
  if (element && element.parentNode) {
    element.parentNode.removeChild(element);
  }
}

async function fetchHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("health check failed");
    const data = await response.json();
    const label = data.backend === "openai"
      ? `OpenAI (${data.model})`
      : "ルールベース";
    statusBadge.textContent = label;
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
    addMessage("assistant", data.reply);
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
    "会話をクリアしました。新しいメッセージを入力してください。"
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
