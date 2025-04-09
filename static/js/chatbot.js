document.addEventListener("DOMContentLoaded", function () {
    const chatbox = document.getElementById("chatbot");
    const chatboxMessages = document.getElementById("chatbot-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatbotToggle = document.getElementById("chatbot-toggle");
    const chatbotClose = document.getElementById("chatbot-close");
    const fullscreenBtn = document.getElementById("chatbot-fullscreen");
    const langSelect = document.getElementById("language-select");
    let selectedLang = "en";

    // 🔔 Request notification permission + welcome message
    if ("Notification" in window) {
        if (Notification.permission !== "granted") {
            Notification.requestPermission().then(permission => {
                console.log("🔔 Notification permission:", permission);
            });
        }

        // 🎉 Welcome notification (optional)
        setTimeout(() => {
            triggerNotification("🌾 Welcome to AgriBot!", "Ask about crops, weather, pests or soil!");
        }, 3000);
    }

    // 🌐 Update selected language
    if (langSelect) {
        langSelect.addEventListener("change", () => {
            selectedLang = langSelect.value;
        });
    }

    // 🛡 Escape HTML
    function escapeHTML(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    // 💬 Add chat message to window
    function addMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        msgDiv.innerHTML = `<strong>${escapeHTML(sender)}:</strong> ${escapeHTML(message)}`;
        chatboxMessages.appendChild(msgDiv);
        chatboxMessages.scrollTop = chatboxMessages.scrollHeight;
    }

    // 📍 Get user location
    function getLocation(callback) {
        if (!navigator.geolocation) {
            console.warn("Geolocation not supported.");
            return callback(null);
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                callback({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                });
            },
            () => {
                console.warn("Location access denied or unavailable.");
                callback(null);
            }
        );
    }

    // 🚀 Send message to backend
    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (!userMessage) {
            addMessage("Error", "⚠️ Please enter a message.");
            return;
        }

        sendBtn.disabled = true;
        addMessage("You", userMessage);
        userInput.value = "";

        const loadingMessage = document.createElement("div");
        loadingMessage.classList.add("message");
        loadingMessage.innerHTML = `<strong>AgriBot:</strong> <em>Typing...</em>`;
        chatboxMessages.appendChild(loadingMessage);
        chatboxMessages.scrollTop = chatboxMessages.scrollHeight;

        // 🌍 Send with location data
        getLocation((location) => {
            const payload = {
                message: userMessage,
                language: selectedLang || "en",
                location: location ? `${location.lat},${location.lon}` : "Hyderabad",
                latitude: location ? location.lat : null,
                longitude: location ? location.lon : null,
            };

            fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then((response) => response.json())
                .then((data) => {
                    chatboxMessages.removeChild(loadingMessage);
                    if (data.response) {
                        addMessage("AgriBot", data.response);
                        triggerNotification("🌱 AgriBot", data.response);  // 🔔 Notify response
                    } else {
                        addMessage("AgriBot", "⚠️ Sorry, I didn’t understand that.");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    chatboxMessages.removeChild(loadingMessage);
                    addMessage("AgriBot", "⚠️ Unable to connect to server.");
                })
                .finally(() => {
                    sendBtn.disabled = false;
                });
        });
    }

    // ⌨️ Button and key events
    if (sendBtn) sendBtn.addEventListener("click", sendMessage);
    if (userInput) {
        userInput.addEventListener("keypress", (event) => {
            if (event.key === "Enter") sendMessage();
        });
    }

    // 📱 Chatbot toggle
    if (chatbotToggle) {
        chatbotToggle.addEventListener("click", () => {
            chatbox.classList.add("chatbox-open");
            chatbox.style.display = "block";
        });
    }

    // ❌ Close chatbot
    if (chatbotClose) {
        chatbotClose.addEventListener("click", () => {
            chatbox.classList.remove("chatbox-open", "chatbox-fullscreen");
            chatbox.style.display = "none";
        });
    }

    // 🔲 Fullscreen toggle
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", () => {
            chatbox.classList.toggle("chatbox-fullscreen");
        });
    }
});

// 🔔 Trigger system notification
function triggerNotification(title, message) {
    if ("Notification" in window && Notification.permission === "granted") {
        new Notification(title, {
            body: message,
            icon: "/static/images/agribot-icon.png", // Customize as needed
        });
    }
}
