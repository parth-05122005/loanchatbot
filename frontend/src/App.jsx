import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(crypto.randomUUID());
  const [sanctionUrl, setSanctionUrl] = useState(null); // FIX: was storing full decision object,
                                                         // only need the download URL
  const [isLoading, setIsLoading] = useState(false);    // FIX: added loading state so user knows
                                                         // backend is processing
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: input,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.reply || "Something went wrong." },
      ]);

      // FIX: backend returns sanction_letter_url as a top-level field directly
      // on the response — not nested inside data.decision.result.document.
      // Old code: data.decision?.result?.document?.download_url → always undefined
      // New code: data.sanction_letter_url → correct
      if (data.sanction_letter_url) {
        setSanctionUrl(data.sanction_letter_url);
      }

    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Server error. Please try again later." },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function resetChat() {
    setMessages([]);
    setSanctionUrl(null);
    setSessionId(crypto.randomUUID());
    setIsLoading(false);
  }

  return (
    <div className="app">
      <div className="chat-container">

        {/* Header */}
        <div className="chat-header">
          Loan Assistant
          <button className="new-chat-btn" onClick={resetChat}>
            New Chat
          </button>
        </div>

        {/* Messages */}
        <div className="chat-body">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === "user" ? "user" : "bot"}`}
            >
              {msg.text}
            </div>
          ))}

          {/* Loading indicator while backend processes */}
          {isLoading && (
            <div className="message bot">
              Processing...
            </div>
          )}

          {/* FIX: sanction letter download — now reads from sanctionUrl state
              which is set from data.sanction_letter_url (top-level field).
              Previously read from data.decision.result.document.download_url
              which never existed in the chat API response. */}
          {sanctionUrl && (
            <div className="message bot">
              <strong>Sanction Letter Ready</strong>
              <br />
              <a
                href={`http://127.0.0.1:8000${sanctionUrl}`}
                target="_blank"
                rel="noreferrer"
                style={{ color: "#60a5fa" }}
              >
                Download Sanction Letter
              </a>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading}>
            {isLoading ? "..." : "Send"}
          </button>
        </div>

      </div>
    </div>
  );
}

export default App;