const chatArea = document.getElementById("chat-area");
const chatInput = document.getElementById("chat-input");
const chatForm = document.getElementById("chat-form");

function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}
scrollToBottom();

// Auto-resize input
chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = chatInput.scrollHeight + "px";
});

// Submit on Enter (without Shift)
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});

// Handle sending messages + streaming
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Show user message
    const userDiv = document.createElement("div");
    userDiv.className = "user-msg";
    userDiv.textContent = query;
    chatArea.appendChild(userDiv);
    scrollToBottom();

    // Reset input
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Placeholder for bot message
    const botDiv = document.createElement("div");
    botDiv.className = "bot-msg";
    chatArea.appendChild(botDiv);

    try {
        const response = await fetch("/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            const parts = buffer.split("\n\n");
            buffer = parts.pop();
            for (let part of parts) {
                if (part.startsWith("data:")) {
                    const text = part.replace("data: ", "");
                    botDiv.textContent += text;
                    scrollToBottom();
                }
            }
        }
    } catch (err) {
        botDiv.textContent = "⚠️ Error: failed to connect.";
        console.error(err);
    }
});

// Start a new chat session
function startNewChat() {
    fetch("/new_chat", { method: "POST" })
        .then(() => window.location.href = "/"); // safer than reload()
}

// Load a previous chat session
function loadChat(index) {
    window.location.href = `/load_chat/${index}`;
}
