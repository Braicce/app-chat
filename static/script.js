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

    // Cria o WebSocket com o URL correto
    ws = new WebSocket(`ws://${window.location.host}/ws/chat?username=${username}`);

    // Definir o manipulador de evento para o WebSocket
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Tratar a mensagem de boas-vindas e a mensagem de saída
        if (data.sender === "Chat") {
            addSystemMessageToChat(data.message);
        } else {
            addMessageToChat(data.username, data.message); // Exibe a mensagem do usuário
        }

        // Toca o som de notificação quando uma mensagem é recebida
        if (data.username !== username) {
            playNotificationSound();  // Toca o som de notificação
        }
    };

    // Adiciona o ouvinte para o ENTER
    const messageInput = document.getElementById("message-input");
    messageInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();  // Evita o comportamento padrão (quebra de linha)
            sendMessage();           // Chama a função para enviar a mensagem
        }
    });
}

function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message && ws) {
        addMessageToChat("Você", message); // Exibe a mensagem localmente
        ws.send(message); // Envia para o WebSocket
        messageInput.value = ""; // Limpa o campo de entrada
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

function addSystemMessageToChat(message) {
    const messagesContainer = document.getElementById("messages");
    const messageElement = document.createElement("div");

    messageElement.classList.add("message", "system");
    messageElement.innerText = message;
    messagesContainer.appendChild(messageElement);

    // Scroll automático para a última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Função para tocar o som
function playNotificationSound() {
    const audio = new Audio('/static/notification.mp3');  // Caminho para o arquivo MP3
    audio.play();
}
