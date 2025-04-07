import { db, auth } from './firebase';
import { collection, addDoc } from 'firebase/firestore';

export async function saveWorkoutReport(report) {
  try {
    // Check that the user is logged in
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }

    // Create a reference to a subcollection under the user's document:
    // Path: users/{userId}/workoutReports
    const reportCollectionRef = collection(db, 'users', user.uid, 'workoutReports');

    // Save the report to Firestore
    const docRef = await addDoc(reportCollectionRef, {
      ...report,
      createdAt: new Date() // Optionally add a timestamp of when the report was stored
    });

    console.log('Workout report saved with ID:', docRef.id);
  } catch (error) {
    console.error('Error saving workout report:', error);
  }
}
