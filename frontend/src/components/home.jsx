import React, { useState, useEffect } from "react";
export default function Home() {
  const [messages, setMessages] = useState([
    { sender: "Aariv", text: "Hi, how can I help you today?" },
  ]);
  const [input, setInput] = useState("");

  // Load history on mount
  useEffect(() => {
    fetch("http://127.0.0.1:8081/api/chat_history")
      .then((res) => res.json())
      .then((data) => {
        // normalize backend history (role → sender, content → text)
        const normalized = data.map((msg) => ({
          sender: msg.role === "user" ? "user" : "Aativ",
          text: msg.content,
        }));
        setMessages(normalized);
      })
      .catch((err) => console.error(err));
  }, []);

  // Handle sending message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, newMessage]);

    try {
      const res = await fetch("http://127.0.0.1:8081/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      const aiMessage = { sender: "Aariv", text: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Error sending message:", err);
    }

    setInput("");
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-r from-gray-900 via-black to-gray-900 text-white relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute w-[500px] h-[500px] bg-purple-600 opacity-30 rounded-full blur-3xl top-10 left-10 animate-pulse"></div>
        <div className="absolute w-[400px] h-[400px] bg-blue-600 opacity-20 rounded-full blur-3xl bottom-20 right-10 animate-pulse"></div>
      </div>

      {/* Chatbot Card */}
      <div className="w-[660px] h-[880px] bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-2xl flex flex-col p-6">
        {/* Header */}
        <div className="flex flex-col space-y-1.5 pb-4 border-b border-gray-700">
          <h2 className="font-bold text-xl tracking-tight text-white">Chatbot</h2>
          <p className="text-sm text-gray-300"> 👋 I'm Aariv, Your personal Medical AI assistant ✨</p>
        </div>

        {/* Chat Window */}
        <div className="flex-1 overflow-y-auto space-y-4 py-4 scrollbar-thin scrollbar-thumb-gray-600">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.sender === "Aariv" && (
                <span className="w-10 h-10 flex items-center justify-center rounded-full bg-purple-600 text-white font-bold">
                  Aariv
                </span>
              )}
              <p
                className={`px-4 py-2 rounded-2xl max-w-[70%] ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-gray-800 text-gray-100 rounded-bl-none"
                }`}
              >
                {msg.text}
              </p>
              {msg.sender === "user" && (
                <span className="w-8 h-8 flex items-center justify-center rounded-full bg-blue-500 text-white font-bold">
                  U
                </span>
              )}
            </div>
          ))}
        </div>

        {/* Input Box */}
        <form
          onSubmit={sendMessage}
          className="flex items-center space-x-2 pt-4 border-t border-gray-700"
        >
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-gray-900/50 text-white px-4 py-2 rounded-lg border border-gray-700 focus:ring-2 focus:ring-purple-500 outline-none"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg shadow-md transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
