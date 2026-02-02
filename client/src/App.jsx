import { useState, useEffect } from 'react';
import { db, auth } from './firebase';
import { signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "firebase/auth";
import { collection, addDoc, query, orderBy, limit, onSnapshot } from 'firebase/firestore';
import './App.css';

const provider = new GoogleAuthProvider();

function App() {
  const [user, setUser] = useState(null);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("OFFLINE");
  const [lastResponse, setLastResponse] = useState("");

  // 1. Listen for Authentication (Are you logged in?)
  useEffect(() => {
    const unsubAuth = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubAuth();
  }, []);

  // 2. Listen for Database Updates (Only if logged in)
  useEffect(() => {
    if (!user) return;

    const q = query(
      collection(db, "commands"),
      orderBy("timestamp", "desc"),
      limit(1)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      if (!snapshot.empty) {
        const doc = snapshot.docs[0].data();
        setStatus(doc.status.toUpperCase());
        if (doc.response) setLastResponse(doc.response);
      }
    }, (error) => {
      console.error("Access Denied:", error);
      setStatus("ACCESS DENIED");
    });

    return () => unsubscribe();
  }, [user]);

  const handleLogin = () => {
    signInWithPopup(auth, provider).catch(console.error);
  };

  const sendCommand = async () => {
    if (!input || !user) return;
    
    try {
      await addDoc(collection(db, "commands"), {
        action: input,
        status: "pending",
        timestamp: new Date(),
        user: user.email 
      });
      setInput("");
      setStatus("SENT");
    } catch (e) {
      console.error("Error sending command: ", e);
      setStatus("ERROR");
    }
  };

  // --- RENDER: LOGIN SCREEN ---
  if (!user) {
    return (
      <div className="container login-screen">
        <h1>G-BOT REMOTE 👻</h1>
        <p>Biometric Authentication Required</p>
        <button className="auth-btn" onClick={handleLogin}>ACCESS SYSTEM</button>
      </div>
    );
  }

  // --- RENDER: COMMAND DECK ---
  return (
    <div className="container">
      <div className="header">
        <div className="user-badge">👤 {user.displayName.split(" ")[0]}</div>
        <button className="logout-btn" onClick={() => signOut(auth)}>DISCONNECT</button>
      </div>
      
      <h1>G-BOT V1</h1>
      
      <div className="status-panel">
        <div className="status-row">
           <span className={`led ${status === 'COMPLETED' ? 'green' : status === 'PENDING' ? 'yellow' : 'red'}`}></span>
           <span className="status-text">{status}</span>
        </div>
        <div className="console-output">
          &gt; {lastResponse || "System ready..."}
        </div>
      </div>

      <div className="input-deck">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter directive..."
          onKeyDown={(e) => e.key === 'Enter' && sendCommand()}
          autoFocus
        />
        <button className="send-btn" onClick={sendCommand}>EXECUTE</button>
      </div>
    </div>
  );
}

export default App;
