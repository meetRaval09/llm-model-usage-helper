const BACKEND = "http://localhost:8000";
const saveBtn = document.getElementById("save");
const statusEl = document.getElementById("status");

saveBtn.addEventListener("click", async () => {
  statusEl.textContent = "Saving...";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const chat = await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_CHAT" });
    if (!chat || chat.error) {
      statusEl.textContent = chat ? chat.error : "Could not read this page.";
      return;
    }
    const res = await fetch(BACKEND + "/chats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(chat),
    });
    if (!res.ok) throw new Error("Backend said " + res.status);
    const out = await res.json();
    statusEl.textContent = "Saved " + out.messages_saved + " messages.";
  } catch (err) {
    statusEl.textContent = "Failed: " + err.message + ". Refresh the chat page and try again.";
  }
});
