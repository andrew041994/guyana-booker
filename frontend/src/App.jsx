import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';

const API = 'http://localhost:8000';

function Login() {
  const [email, setEmail] = useState('customer@guyana.com');
  const [password, setPassword] = useState('pass');

  const login = async () => {
    try {
      const res = await axios.post(`${API}/auth/login`, new URLSearchParams({
        username: email,
        password: password
      }));
      localStorage.setItem('token', res.data.access_token);
      alert('Logged in! Refresh page');
    } catch {
      alert('Wrong credentials');
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>
      <h1 style={{ color: '#16a34a' }}>Guyana Booker Web</h1>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" style={{ display: 'block', margin: '10px auto', padding: '10px', width: '300px' }} />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" style={{ display: 'block', margin: '10px auto', padding: '10px', width: '300px' }} />
      <button onClick={login} style={{ padding: '10px 20px', background: '#16a34a', color: 'white', border: 'none' }}>Login</button>
      <p>Use customer@guyana.com / pass</p>
    </div>
  );
}

function Home() {
  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>
      <h1 style={{ color: '#16a34a' }}>Welcome to Guyana Booker Web!</h1>
      <p>Your Booksy clone is LIVE on web + mobile</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}
