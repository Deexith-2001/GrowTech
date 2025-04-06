document.addEventListener("DOMContentLoaded", function () {
    const chatboxMessages = document.getElementById("chatbox-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // Function to safely escape HTML
    function escapeHTML(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    // Function to add messages to the chatbox
    function addMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        msgDiv.innerHTML = `<strong>${escapeHTML(sender)}:</strong> ${escapeHTML(message)}`;
        chatboxMessages.appendChild(msgDiv);
        chatboxMessages.scrollTop = chatboxMessages.scrollHeight;
    }

    // Function to send message to backend
    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (!userMessage) {
            addMessage("Error", "⚠️ Please enter a message.");
            return;
        }

        // Disable button to prevent duplicate messages
        sendBtn.disabled = true;

        addMessage("You", userMessage);
        userInput.value = "";

        // Show loading response from AgriBot
        const loadingMessage = document.createElement("div");
        loadingMessage.classList.add("message");
        loadingMessage.innerHTML = `<strong>AgriBot:</strong> <em>Typing...</em>`;
        chatboxMessages.appendChild(loadingMessage);
        chatboxMessages.scrollTop = chatboxMessages.scrollHeight;

        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage, location: "Hyderabad" }) // Default location
        })
        .then(response => response.json())
        .then(data => {
            chatboxMessages.removeChild(loadingMessage); // Remove typing...
            if (data.response) {
                addMessage("AgriBot", data.response);
            } else {
                addMessage("AgriBot", "⚠️ Sorry, I didn’t understand that.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            chatboxMessages.removeChild(loadingMessage);
            addMessage("AgriBot", "⚠️ Unable to connect to server.");
        })
        .finally(() => {
            sendBtn.disabled = false;
        });
    }

    // Event listeners for sending messages
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") sendMessage();
    });
});

// Toggle chatbot sidebar visibility
function toggleChatbot() {
    const chatbot = document.getElementById("chatbot-sidebar");
    if (chatbot) {
        chatbot.style.display = (chatbot.style.display === "none" || chatbot.style.display === "") ? "block" : "none";
    }
}

// Fetch Minimum Support Price (MSP) data
function fetchMSPData() {
    fetch("/api/msp")
    .then(response => response.json())
    .then(data => {
        if (!Array.isArray(data)) {
            throw new Error("Invalid data format: Expected an array");
        }
        data.forEach(msp => {
            console.log(`Crop: ${msp.crop}, Price: ₹${msp.price}`);
        });
    })
    .catch(error => console.error("Error fetching MSP data:", error));
}
