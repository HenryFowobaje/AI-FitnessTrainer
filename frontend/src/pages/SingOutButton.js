// SignOutButton.js
import React from 'react';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';

function SignOutButton() {
  const handleSignOut = async () => {
    try {
      await signOut(auth);
      console.log('User signed out');
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return <button onClick={handleSignOut}>Sign Out</button>;
}

export default SignOutButton;
