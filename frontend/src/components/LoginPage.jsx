import React, { useState } from "react";

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const response = await fetch("http://127.0.0.1:8081/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const result = await response.json();

    if (response.ok) {
      setError(""); // clear any error
      alert(result.message);
      if (onLoginSuccess) onLoginSuccess(); // callback to parent
    } else {
      setError(result.message);
    }
  } catch (err) {   // ✅ renamed here
    setError("Server error, please try again.");
  }
};

  return (
    <div className="flex items-center justify-center min-h-screen bg-black text-white">
      <div className="p-8 bg-zinc-900 rounded-lg shadow-lg w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">Chatbot Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
          <button
            type="submit"
            className="w-full py-2 bg-green-600 hover:bg-green-500 rounded-lg"
          >
            Login
          </button>
        </form>
        {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
      </div>
    </div>
  );
}
