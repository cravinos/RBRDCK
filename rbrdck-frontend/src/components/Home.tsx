import React, { useState } from 'react';
import axios from 'axios';

const Home: React.FC = () => {
  const [token, setToken] = useState('');
  const [authStatus, setAuthStatus] = useState('');

  const handleAuth = async () => {
    try {
      const response = await axios.post('/api/auth', { token });
      setAuthStatus('Authentication successful!');
      // Store the token or user info in state or context
    } catch (error) {
      setAuthStatus('Authentication failed. Please try again.');
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Welcome to RBRDCK</h1>
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">GitHub Authentication</h2>
        <input
          type="text"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Enter GitHub Token"
          className="border p-2 mr-2"
        />
        <button onClick={handleAuth} className="bg-blue-500 text-white px-4 py-2 rounded">
          Authenticate
        </button>
        {authStatus && <p className="mt-2">{authStatus}</p>}
      </div>
    </div>
  );
};

export default Home;