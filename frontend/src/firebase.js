import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyC03c1d-mokxhRygZH2kHPcpTB3CoR8XMw",
  authDomain: "ai-fitnesstrainer-9a182.firebaseapp.com",
  projectId: "ai-fitnesstrainer-9a182",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
