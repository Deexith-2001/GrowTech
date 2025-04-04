document.addEventListener("DOMContentLoaded", function () {
    const chatboxMessages = document.getElementById("chatbox-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // Function to add messages to the chatbox
    function addMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
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

        addMessage("You", userMessage);
        userInput.value = "";

        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage, location: "Hyderabad" })  // Default location
        })
        .then((response) => response.json())
        .then((data) => addMessage("AgriBot", data.response))
        .catch((error) => {
            console.error("Error:", error);
            addMessage("AgriBot", "⚠️ Unable to connect to server.");
        });
    }

    // Event listeners for sending messages
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") sendMessage();
    });
});

// Function to toggle chatbot visibility
function toggleChatbot() {
    const chatbot = document.getElementById("chatbot-sidebar");
    if (chatbot) {
        chatbot.style.display = (chatbot.style.display === "none" || chatbot.style.display === "") ? "block" : "none";
    }
}

// Function to fetch MSP data
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
