document.addEventListener("DOMContentLoaded", function () {
    const chatbox = document.getElementById("chatbot-sidebar");
    const chatbotToggle = document.getElementById("chatbot-toggle");
    const chatboxClose = document.getElementById("chatbox-close");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chatbox-messages");
    const fullscreenBtn = document.getElementById("chatbox-fullscreen-btn");

    // Open Chatbot
    if (chatbotToggle) {
        chatbotToggle.addEventListener("click", function () {
            chatbox.classList.add("chatbox-open");
            chatbox.style.display = "block";
        });
    }

    // Close Chatbot
    if (chatboxClose) {
        chatboxClose.addEventListener("click", function () {
            chatbox.classList.remove("chatbox-open");
            chatbox.classList.remove("chatbox-fullscreen"); // Exit fullscreen when closing
            chatbox.style.display = "none";
        });
    }

    // Toggle Fullscreen Mode
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", function () {
            chatbox.classList.toggle("chatbox-fullscreen");
        });
    }

    // Function to add messages to the chatbox
    function addMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to get the user's location
    function getLocation(callback) {
        if (!navigator.geolocation) {
            console.warn("Geolocation is not supported by this browser.");
            return callback(null);
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                callback({ lat, lon });
            },
            (error) => {
                console.warn("Location access denied or unavailable. Using default location.");
                callback(null);
            }
        );
    }

    // Function to send a message to the backend
    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === "") return;

        addMessage("You", userMessage);
        userInput.value = "";

        getLocation((location) => {
            const payload = {
                message: userMessage,
                location: location ? `${location.lat},${location.lon}` : "Hyderabad",
            };

            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then((response) => response.json())
                .then((data) => {
                    addMessage("AgriBot", data.response);
                })
                .catch((error) => {
                    console.error("Error:", error);
                    addMessage("AgriBot", "Sorry, something went wrong. Please try again.");
                });
        });
    }

    // Attach event listeners if elements exist
    if (sendBtn) sendBtn.addEventListener("click", sendMessage);
    if (userInput) {
        userInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter") sendMessage();
        });
    }
});
