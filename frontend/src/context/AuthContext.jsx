import { createContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [userLoading, setUserLoading] = useState(Boolean(localStorage.getItem('token')));
  const [userError, setUserError] = useState(false);
  const [showGreeting, setShowGreeting] = useState(
    localStorage.getItem('showGreeting') !== 'false'
  );
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setUser(null);
      setUserLoading(false);
      setUserError(false);
      return;
    }

    let cancelled = false;
    setUserLoading(true);
    setUserError(false);

    client.get('/auth/me')
      .then((response) => {
        if (!cancelled) setUser(response.data);
      })
      .catch((error) => {
        if (cancelled) return;
        setUserError(true);
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
        }
        console.error('Could not verify current user:', error.response?.data || error.message);
      })
      .finally(() => {
        if (!cancelled) setUserLoading(false);
      });

    return () => { cancelled = true; };
  }, [token]);

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email.trim());
      formData.append('password', password);

      const response = await client.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      navigate('/dashboard');
      return true;
    } catch (error) {
      console.error('Login failed:', error.response?.data || error.message);
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    navigate('/login');
  };

  const updateShowGreeting = (value) => {
    setShowGreeting(value);
    localStorage.setItem('showGreeting', String(value));
  };

  return (
    <AuthContext.Provider value={{
      token, user, userLoading, userError, showGreeting,
      updateShowGreeting, login, logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
