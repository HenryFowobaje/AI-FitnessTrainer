// reportService.js
import { db } from "./firebase";
import { collection, addDoc } from "firebase/firestore";
import { auth } from "./firebase";

export const saveWorkoutReport = async (report) => {
  const user = auth.currentUser;
  if (!user) {
    console.error("⚠️ No user logged in — can't save report");
    return;
  }

  try {
    const reportWithUser = { ...report, userId: user.uid };
    console.log("📝 Saving report to Firebase:", reportWithUser);

    await addDoc(collection(db, "workouts"), reportWithUser);
    console.log("✅ Report saved!");
  } catch (error) {
    console.error("❌ Error saving workout:", error);
  }
};

