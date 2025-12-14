import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(crypto.randomUUID());
  const [decision, setDecision] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

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

      // ✅ STORE FINAL DECISION (IF ANY)
      if (data.decision) {
        setDecision(data.decision);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Server error. Please try again later." },
      ]);
    }
  }

  function resetChat() {
    setMessages([]);
    setDecision(null);
    setSessionId(crypto.randomUUID());
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

          {/* ✅ SANCTION LETTER DOWNLOAD */}
          {decision?.stage === "SANCTION" &&
            decision?.result?.document && (
              <div className="message bot">
                <strong>📄 Sanction Letter</strong>
                <br />
                <a
                  href={`http://127.0.0.1:8000${decision.result.document.download_url}`}
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
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
