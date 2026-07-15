import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "mock-api-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "civitas-demo.firebaseapp.com",
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL || "https://civitas-demo.firebaseio.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "civitas-demo",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "civitas-demo.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789:web:123456"
};

let app;
let firestore: any = null;
let database: any = null;

try {
  if (getApps().length === 0) {
    app = initializeApp(firebaseConfig);
    firestore = getFirestore(app);
    database = getDatabase(app);
  }
} catch (error) {
  console.warn("Firebase initialization failed. Offline mock mode enabled.");
}

export { firestore, database };
