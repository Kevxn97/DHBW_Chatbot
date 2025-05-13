const { OpenAI } = require("openai");
const readline = require("readline");
require('dotenv').config({ path: __dirname + '/.env' });

// Initialisiere den OpenAI-Client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Erstelle eine readline-Schnittstelle
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Funktion für die Ladeanimation
function startLoading() {
  const text = "Generating Answer";
  const dots = [".  ", ".. ", "..."];
  let i = 0;
  let dotIndex = 0;
  
  return setInterval(() => {
    // Create animated text with different colored characters
    let animatedText = "";
    for (let j = 0; j < text.length; j++) {
      // Determine if this character should be highlighted in this frame
      const isHighlighted = (j === i % text.length);
      
      if (text[j] === " ") {
        animatedText += " ";
      } else if (isHighlighted) {
        // Highlighted character (brighter)
        animatedText += `\x1b[1;37m${text[j]}\x1b[0m`;
      } else {
        // Normal character (gray)
        animatedText += `\x1b[90m${text[j]}\x1b[0m`;
      }
    }
    
    // Add animated dots
    const currentDots = dots[dotIndex];
    dotIndex = (dotIndex + 1) % dots.length;
    
    // Increment character position for next frame
    i = (i + 1) % (text.length * 2); // Slow down the animation
    
    process.stdout.write(`\r${animatedText}${currentDots}`);
  }, 150);
}

// Funktion zum Warten auf den Abschluss des Runs mit Timeout
async function waitForRunCompletion(threadId, runId, maxRetries = 3, timeout = 30000) {
  let retries = 0;
  const startTime = Date.now();
  
  while (retries < maxRetries) {
    try {
      const run = await openai.beta.threads.runs.retrieve(threadId, runId);
      
      if (run.status === "completed") return run;
      if (run.status === "failed" || run.status === "cancelled") {
        throw new Error(`Run fehlgeschlagen mit Status: ${run.status}`);
      }
      
      // Prüfe Timeout
      if (Date.now() - startTime > timeout) {
        throw new Error("Zeitüberschreitung bei der Verbindung zum OpenAI-Server.");
      }
      
      await new Promise((resolve) => setTimeout(resolve, 500));
    } catch (error) {
      retries++;
      if (retries >= maxRetries) {
        throw error;
      }
      console.log(`\rVerbindungsversuch ${retries}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// Erstelle einen einzigen Thread einmalig
let threadId;
async function initializeThread(maxRetries = 3) {
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      const thread = await openai.beta.threads.create();
      threadId = thread.id;
      return;
    } catch (error) {
      retries++;
      if (retries >= maxRetries) {
        throw new Error("Konnte keinen Thread erstellen: " + error.message);
      }
      console.log(`\rThread-Erstellungsversuch ${retries}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// Funktion zum Stellen einer Frage und Abrufen der Antwort
async function askQuestion(userInput) {
  let loading;
  try {
    // Stelle sicher, dass ein Thread existiert
    if (!threadId) {
      await initializeThread();
    }

    // Füge die Nachricht zum bestehenden Thread hinzu
    await openai.beta.threads.messages.create(threadId, { role: "user", content: userInput });
    const run = await openai.beta.threads.runs.create(threadId, { assistant_id: "asst_cJqKpSpeLHf6jUCZvhTnafeH" });

    // Starte Ladeanimation
    loading = startLoading();
    
    await waitForRunCompletion(threadId, run.id);
    
    // Stoppe Ladeanimation und lösche die Zeile
    clearInterval(loading);
    process.stdout.write("\r\x1b[K");

    const messages = await openai.beta.threads.messages.list(threadId);
    const assistantMessage = messages.data.find((msg) => msg.role === "assistant" && msg.run_id === run.id);
    
    if (assistantMessage) {
      // Entferne Quellenzitate wie 【4:0†Studiengangsflyer_web_BWL-Digital_Business_Management (1).pdf】
      const responseText = assistantMessage.content[0].text.value.replace(/【.*?】/g, '');
      console.log(responseText);
    } else {
      console.log("Keine Antwort gefunden.");
    }
  } catch (error) {
    if (loading) {
      clearInterval(loading);
    }
    process.stdout.write("\r\x1b[K");
    
    // Benutzerfreundlichere Fehlermeldungen
    if (error.message.includes("apiKey")) {
      console.error("Fehler: API-Schlüssel ungültig oder abgelaufen. Bitte überprüfen Sie Ihre Konfiguration.");
    } else if (error.message.includes("network") || error.message.includes("connect") || error.message.includes("ENOTFOUND")) {
      console.error("Fehler: Keine Verbindung zum Backend möglich. Bitte überprüfen Sie Ihre Internetverbindung und versuchen Sie es später erneut.");
    } else if (error.message.includes("Zeitüberschreitung")) {
      console.error("Fehler: Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es später erneut.");
    } else {
      console.error("Fehler:", error.message || error);
    }
    
    // Kurz warten und dann zurück zum Prompt
    setTimeout(() => {
      console.log("\nBitte versuchen Sie es später noch einmal.");
    }, 500);
  }
}

// Funktion zum Abfragen der Benutzereingabe
function promptUser() {
  rl.question("Gib deine Frage ein: ", async (userInput) => {
    if (userInput.toLowerCase() === "exit") {
      console.log("Beende das Programm...");
      rl.close();
      return;
    }
    await askQuestion(userInput);
    promptUser();
  });
}

// Führe einen initialen Verbindungstest durch
async function testConnection() {
  let loading = startLoading();
  try {
    console.log("Verbindung zum OpenAI-Server wird getestet...");
    // Versuche einen einfachen API-Aufruf
    await openai.models.list({ limit: 1 });
    clearInterval(loading);
    process.stdout.write("\r\x1b[K");
    console.log("Verbindung erfolgreich hergestellt.\n");
    
    // Test the animation for 5 seconds
    console.log("Animation-Test für 5 Sekunden:");
    let animTest = startLoading();
    setTimeout(() => {
      clearInterval(animTest);
      process.stdout.write("\r\x1b[K");
      console.log("Animation-Test abgeschlossen.\n");
      promptUser();
    }, 5000);
    
  } catch (error) {
    clearInterval(loading);
    process.stdout.write("\r\x1b[K");
    console.error("Fehler bei der Verbindung zum OpenAI-Server:", error.message);
    console.log("Bitte überprüfen Sie Ihre Internetverbindung und API-Konfiguration.");
    rl.close();
  }
}

// Starte den Chatbot mit Verbindungstest
testConnection();