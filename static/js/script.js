const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");

if (searchBtn && searchInput) {

    searchBtn.addEventListener("click", () => {

        const query = searchInput.value.trim();

        if (!query) {
            alert("Please enter a car or brand name.");
            return;
        }

        window.location.href = "/agent?query=" + encodeURIComponent(query);

    });

    searchInput.addEventListener("keydown", (event) => {

        if (event.key === "Enter") {
            searchBtn.click();
        }

    });

}
// ==========================
// AI CHATBOT
// ==========================

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

if (sendBtn && userInput && chatBox) {

    function sendMessage() {

        const message = userInput.value.trim();

        if (!message) return;

        // User Message
        const userDiv = document.createElement("div");
        userDiv.className = "user-message";
        userDiv.innerHTML = `
<strong>👤 You</strong><br><br>
${message}
`;
        chatBox.appendChild(userDiv);

        // Temporary Bot Reply
        const botDiv = document.createElement("div");
botDiv.className = "bot-message";
botDiv.innerHTML = `
<strong>🤖 Velocix AI</strong><br><br>
<span class="typing">
    Thinking<span>.</span><span>.</span><span>.</span>
</span>
`;
chatBox.appendChild(botDiv);

chatBox.scrollTop = chatBox.scrollHeight;

userInput.value = "";

fetch("/chat", {

    method: "POST",

    headers: {

        "Content-Type": "application/json"

    },

    body: JSON.stringify({

        message: message

    })

})

.then(response => response.json())

.then(data => {

    botDiv.innerHTML = `
<strong>🤖 Velocix AI</strong><br><br>
${data.reply.replace(/\n/g,"<br>")}
`;

})

.catch(() => {

    botDiv.textContent = "⚠ Error connecting to server.";

});

    }

    sendBtn.addEventListener("click", sendMessage);

    userInput.addEventListener("keydown", function(event){

        if(event.key === "Enter"){

            sendMessage();

        }

    });

}