const { OpenAI } = require("openai");
// const readline = require("readline");
const express = require('express');
const cors = require('cors');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// Initialisiere den OpenAI-Client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "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",
});

// Funktion zum Warten auf den Abschluss des Runs
async function waitForRunCompletion(threadId, runId) {
  while (true) {
    const run = await openai.beta.threads.runs.retrieve(threadId, runId);
    if (run.status === "completed") return run;
    if (run.status === "failed" || run.status === "cancelled") {
      throw new Error(`Run fehlgeschlagen mit Status: ${run.status}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

// Wir verwenden einen Thread pro Server-Instanz oder pro User-Session (hier vereinfacht)
// Für eine echte Anwendung müsstest du Threads pro Benutzer verwalten.
let threadId;
async function initializeThread() {
  if (!threadId) {
    const thread = await openai.beta.threads.create();
    threadId = thread.id;
    console.log(`Thread initialisiert mit ID: ${threadId}`);
  }
}

// Funktion zum Stellen einer Frage und Abrufen der Antwort
async function getAssistantResponse(userInput) {
  try {
    if (!threadId) {
      await initializeThread();
    }

    // Füge die Nachricht zum bestehenden Thread hinzu
    await openai.beta.threads.messages.create(threadId, { role: "user", content: userInput });
    const run = await openai.beta.threads.runs.create(threadId, { assistant_id: "asst_cJqKpSpeLHf6jUCZvhTnafeH" });

    await waitForRunCompletion(threadId, run.id);

    const messages = await openai.beta.threads.messages.list(threadId);
    const assistantMessage = messages.data.find((msg) => msg.role === "assistant" && msg.run_id === run.id);

    if (assistantMessage && assistantMessage.content[0].type === 'text') {
      // Entferne Quellenzitate wie 【4:0†Studiengangsflyer_web_BWL-Digital_Business_Management (1).pdf】
      const responseText = assistantMessage.content[0].text.value.replace(/【.*?】/g, '');
      return responseText;
    } else {
      return "Keine Antwort gefunden.";
    }
  } catch (error) {
    console.error("Fehler bei der Anfrage an OpenAI:", error.message || error);
    throw new Error("Fehler bei der Verarbeitung der Anfrage.");
  }
}

// API Endpunkt erstellen
app.post('/api/ask', async (req, res) => {
  const userInput = req.body.question;

  if (!userInput) {
    return res.status(400).json({ error: 'Frage fehlt im Request Body.' });
  }

  console.log(`Anfrage erhalten: "${userInput}"`);

  try {
    const assistantReply = await getAssistantResponse(userInput);
    res.json({ answer: assistantReply });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Starte den Server
app.listen(port, async () => {
  console.log(`Backend-Server läuft auf http://localhost:${port}`);
  await initializeThread();
});