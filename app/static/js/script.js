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

        if (data.sender === "Chat") {
            addSystemMessageToChat(data.message); // Mensagens do sistema (entrada/saída)
        } else if (data.username === username) {
            // Ignorar mensagens recebidas do próprio usuário
            return;
        } else if (data.type === "photo") {
            addMessageToChat(data.username, data.message, "photo"); // Mensagens do tipo foto
        } else {
            addMessageToChat(data.username, data.message, "text"); // Mensagens de texto
        }

        // Toca o som de notificação para mensagens de outros usuários
        if (data.username && data.username !== username) {
            playNotificationSound();
        }
    };

    // Adiciona o ouvinte para o ENTER no campo de mensagem
    const messageInput = document.getElementById("message-input");
    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Evita o comportamento padrão (quebra de linha)
            sendMessage(); // Envia a mensagem
        }
    });
}

function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message && ws) {
        ws.send(JSON.stringify({ type: "text", content: message }));
        addMessageToChat("Você", message, "text"); // Exibe no chat localmente
        messageInput.value = ""; // Limpa o campo de entrada
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();
        const filePath = result.filePath;

        if (filePath && ws) {
            ws.send(JSON.stringify({ type: "photo", content: filePath }));
            addMessageToChat("Você", filePath, "photo"); // Renderiza localmente
        }
    } catch (error) {
        console.error("Erro ao fazer upload:", error);
        alert("Falha ao enviar o arquivo.");
    }
}

function addMessageToChat(sender, message, type = "text") {
    const messagesContainer = document.getElementById("messages");
    const messageElement = document.createElement("div");

    messageElement.classList.add("message");
    if (sender === "Você") {
        messageElement.classList.add("sent");
    } else {
        messageElement.classList.add("received");
    }

    if (type === "photo") {
        // Renderizar imagem
        const img = document.createElement("img");
        img.src = message; // Caminho da imagem
        img.alt = "Imagem enviada";
        img.style.maxWidth = "200px";
        img.style.borderRadius = "8px";
        messageElement.appendChild(img);

        // Adicionar texto "Enviou uma foto"
        const photoCaption = document.createElement("div");
        photoCaption.textContent = `${sender} enviou uma foto:`;
        photoCaption.style.fontSize = "12px";
        photoCaption.style.color = "#555"; // Cor opcional para o texto
        photoCaption.style.marginTop = "5px"; // Espaçamento entre imagem e texto
        messageElement.appendChild(photoCaption);
    } else {
        // Renderizar texto
        const messageWithEmojis = joypixels.toImage(message);
        messageElement.innerHTML = `<strong>${sender}:</strong> ${messageWithEmojis}`;
    }

    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll automático
}

function addSystemMessageToChat(message) {
    const messagesContainer = document.getElementById("messages");
    const messageElement = document.createElement("div");

    messageElement.classList.add("message", "system");
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);

    // Scroll automático para a última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Função para tocar o som
function playNotificationSound() {
    const audio = new Audio("/static/misc/notification.mp3"); // Caminho para o arquivo MP3
    audio.play();
}

// Evento para upload de arquivos
const photoInput = document.getElementById("photo-input");
photoInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
});

// Função para abrir a lista de emojis
function openEmojiPicker() {
    const emojiPicker = document.getElementById("emoji-picker");
    if (!emojiPicker) {
        console.error("Emoji picker element not found.");
        return;
    }
    if (emojiPicker.innerHTML === "") {
        loadEmojis(); // Carregar os emojis apenas uma vez
    }
    emojiPicker.style.display = emojiPicker.style.display === "block" ? "none" : "block";
}

// Função para carregar emojis locais usando JoyPixels
function loadEmojis() {
    const emojiPicker = document.getElementById("emoji-picker");
    const emojiShortnames = [
        ':smile:', ':heart:', ':thumbsup:', ':laughing:', ':sob:', ':star:', ':wink:', ':grin:'
    ]; // Lista de shortnames de emojis

    emojiPicker.innerHTML = ""; // Limpa o conteúdo antes de recarregar
    emojiShortnames.forEach((shortname) => {
        const imgHTML = joypixels.shortnameToImage(shortname); // Gera o HTML da imagem
        const imgElement = document.createElement('span');
        imgElement.innerHTML = imgHTML;
        imgElement.style.cursor = "pointer";
        imgElement.style.margin = "5px";
        imgElement.onclick = () => addEmojiToMessage(shortname); // Adiciona o shortname ao clicar
        emojiPicker.appendChild(imgElement);
    });
}

// Adicionar emoji ao campo de texto
function addEmojiToMessage(emoji) {
    const messageInput = document.getElementById("message-input");
    messageInput.value += `${emoji}`;
    document.getElementById("emoji-picker").style.display = "none";
}
