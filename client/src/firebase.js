// client/src/firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBjybTQ7Bv9HACWN-9ObuIW-KRw9bKIsgY",
  authDomain: "gbot-core.firebaseapp.com",
  projectId: "gbot-core",
  storageBucket: "gbot-core.firebasestorage.app",
  messagingSenderId: "54671337536",
  appId: "1:54671337536:web:1b64c9089d6043421e17a5"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
