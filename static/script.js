// Store current speech instance
let currentSpeech = null;

// 🌍 GLOBAL VARIABLES
let recognition;
let isListening = false;

/* =========================
   🧠 TEXT PROCESSING
========================= */

// Normalize input
function normalizeInput(input) {
    return input
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9\s]/g, "")
        .replace(/\s+/g, " ");
}

// Dictionary
const dictionary = ["hello", "course", "python", "java", "bye"];

// Levenshtein Distance
function levenshtein(a, b) {
    let matrix = [];

    for (let i = 0; i <= b.length; i++) matrix[i] = [i];
    for (let j = 0; j <= a.length; j++) matrix[0][j] = j;

    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b[i - 1] === a[j - 1]) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j] + 1
                );
            }
        }
    }

    return matrix[b.length][a.length];
}

// Spelling correction
function correctSpelling(input) {
    let words = input.split(" ");

    return words.map(word => {
        if (dictionary.includes(word)) return word;

        let closest = word;
        let minDistance = Infinity;

        dictionary.forEach(dictWord => {
            let distance = levenshtein(word, dictWord);
            if (distance < minDistance) {
                minDistance = distance;
                closest = dictWord;
            }
        });

        return (minDistance <= 2) ? closest : word;
    }).join(" ");
}



function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput === "") return;

    let cleanInput = normalizeInput(userInput);
    cleanInput = correctSpelling(cleanInput);


    let chatBox = document.getElementById("chat-box");

    // Show user message
    chatBox.innerHTML += "<p><b>You:</b> " + userInput + "</p>";

    // Show typing indicator
    chatBox.innerHTML += "<p id='typing'><i>Bot is typing...</i></p>";

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        document.getElementById("typing").remove();

        // Show bot reply
        chatBox.innerHTML += "<p><b>Bot:</b> " + data.reply + "</p>";

        // Speak reply
        speakText(data.reply);

        // Clear input
        document.getElementById("user-input").value = "";

        // Auto scroll
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

/* 🎤 VOICE INPUT */
function startVoice() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice recognition not supported in this browser");
        return;
    }

    let recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";
    recognition.start();

    recognition.onresult = function(event) {
        let voiceText = event.results[0][0].transcript.toLowerCase();
        document.getElementById("user-input").value = voiceText;
        sendMessage();
    };
}

recognition.onresult = function(event) {
    let userText = event.results[0][0].transcript;

    userText = normalizeInput(userText); // ✅ FIX HERE

    document.getElementById("input").value = userText;

    stopListening();
    botReply(userText);
};

/* 🔊 VOICE OUTPUT */
function speakText(text) {
    if ('speechSynthesis' in window) {

        // 🛑 STOP MIC before speaking
        if (isListening) {
            recognition.stop();
            isListening = false;
            document.getElementById('voiceBtn').classList.remove('listening');
        }

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-IN';

        // ▶ After speaking ends, mic stays OFF (safe)
        utterance.onend = function () {
            console.log("Speech finished");
        };

        window.speechSynthesis.speak(utterance);
    }
}

/* ⏸ PAUSE */
function pauseVoice() {
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
    }
}

/* ▶ RESUME */
function resumeVoice() {
    if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
    }
}

/* ⏹ STOP */
function stopVoice() {
    window.speechSynthesis.cancel();
}

