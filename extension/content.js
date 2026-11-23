const SELECTORS = {
  chatgpt: {
    messages:
      '[data-user-message-bubble="true"], [data-dil-response], [data-markdown-text-style="assistant-message"]',
    role: (el) => (el.matches("[data-user-message-bubble]") ? "user" : "assistant"),
  },
  claude: {
    messages: '[data-testid="user-message"], .font-claude-response',
    role: (el) =>
      el.matches('[data-testid="user-message"]') ? "user" : "assistant",
  },
};

function detectPlatform() {
  const host = location.hostname;
  if (host.includes("claude.ai")) return "claude";
  if (host.includes("chatgpt.com") || host.includes("openai.com")) return "chatgpt";
  return null;
}

function extractChat() {
  const platform = detectPlatform();
  if (!platform) return { error: "This site is not supported yet." };
  const rules = SELECTORS[platform];
  const all = Array.from(document.querySelectorAll(rules.messages));
  const nodes = all.filter(
    (el) => !el.parentElement || !el.parentElement.closest(rules.messages)
  );
  const messages = nodes
    .map((el) => ({ role: rules.role(el), text: (el.innerText || "").trim() }))
    .filter((m) => m.text.length > 0);
  if (messages.length === 0) {
    return { error: "No messages found. Open a chat that has messages." };
  }
  return {
    platform,
    url: location.href.split("#")[0],
    title: document.title.replace(/\s+/g, " ").trim() || "Untitled chat",
    messages,
  };
}

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.type === "EXTRACT_CHAT") sendResponse(extractChat());
});
