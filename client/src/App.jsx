import { useState, useEffect, useRef } from "react";
import { auth, db } from "./firebase";
import {
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";
import {
  collection,
  addDoc,
  query,
  orderBy,
  limit,
  onSnapshot,
  serverTimestamp,
} from "firebase/firestore";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Ref to auto-scroll to bottom
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    const unsubscribeAuth = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribeAuth();
  }, []);

  // 🔥 Listen for Chat History
  useEffect(() => {
    if (!user) return;

    // Get last 50 messages ordered by time
    const q = query(
      collection(db, "commands"),
      orderBy("createdAt", "asc"),
      limit(50),
    );

    const unsubscribeDocs = onSnapshot(q, (snapshot) => {
      const msgs = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      setMessages(msgs);
    });

    return () => unsubscribeDocs();
  }, [user]);

  // Auto-scroll when messages change
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error("Login failed", error);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setMessages([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    try {
      await addDoc(collection(db, "commands"), {
        text: input,
        status: "pending",
        createdAt: serverTimestamp(), // Important for sorting
        user: user.email,
      });
      setInput("");
    } catch (error) {
      console.error("Error sending command:", error);
    }
    setLoading(false);
  };

  if (!user) {
    return (
      <div className="login-container">
        <h1>👻 G-BOT V2</h1>
        <p>Restricted Access. Identity Verification Required.</p>
        <button onClick={handleLogin} className="login-btn">
          Authenticate with Google
        </button>
      </div>
    );
  }

  return (
    <>
      <header>
        <h1>
          <div className="status-dot"></div>
          G-BOT ONLINE
        </h1>
        <button onClick={handleLogout} className="logout-btn">
          Disconnect
        </button>
      </header>

      <div className="chat-window">
        {messages.map((msg) => (
          <div key={msg.id} className="message-group">
            {/* 1. The User's Command */}
            <div className={`message-row user`}>
              <div className="bubble user">{msg.text}</div>
            </div>

            {/* 2. The Bot's Response (If it exists) */}
            {msg.status !== "pending" && (
              <div className={`message-row bot`}>
                <div
                  className={`bubble ${msg.status === "error" ? "error" : "bot"}`}
                >
                  {msg.status === "completed" ? (
                    <>
                      <strong>✅ Executed:</strong>
                      <br />
                      {msg.response}
                    </>
                  ) : msg.status === "error" ? (
                    <>
                      <strong>❌ Error:</strong>
                      <br />
                      {msg.error}
                    </>
                  ) : null}
                  <span className="meta">
                    {msg.processedAt?.toDate
                      ? msg.processedAt.toDate().toLocaleTimeString()
                      : "Just now"}
                  </span>
                </div>
              </div>
            )}

            {/* 3. Pending Indicator */}
            {msg.status === "pending" && (
              <div className="message-row bot">
                <div className="bubble bot" style={{ opacity: 0.7 }}>
                  Processing... ⏳
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={endOfMessagesRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command..."
          disabled={loading}
        />
        <button type="submit" className="send-btn" disabled={loading}>
          {loading ? "..." : "SEND"}
        </button>
      </form>
    </>
  );
}

export default App;
