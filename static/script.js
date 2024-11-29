let ws;
let username;

function enterChat() {
    username = document.getElementById("nickname-input").value;
    if (!username) {
        alert("Por favor, insira um nickname.");
        return;
    }

    document.getElementById("nickname-section").style.display = "none";
    document.getElementById("chat-section").style.display = "flex";

    ws = new WebSocket(`ws://${window.location.host}/ws/chat?username=${username}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addMessageToChat(data.sender, data.message);
    };
}

function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message && ws) {
        addMessageToChat("Você", message); // Exibe a mensagem localmente
        ws.send(message); // Envia para o WebSocket
        messageInput.value = "";
    }
}

function addMessageToChat(sender, message) {
    const messagesContainer = document.getElementById("messages");
    const messageElement = document.createElement("div");

    messageElement.classList.add("message");
    if (sender === "Você") {
        messageElement.classList.add("sent");
    } else if (sender === username) {
        // Ignorar a cópia enviada pelo WebSocket para o próprio usuário
        return;
    } else {
        messageElement.classList.add("received");
    }

    messageElement.innerText = `${sender}: ${message}`;
    messagesContainer.appendChild(messageElement);

    // Scroll automático para a última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
