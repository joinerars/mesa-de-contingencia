import { createContext, useContext, useState, useCallback } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    try {
      const stored = localStorage.getItem("mesa_auth");
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });

  const login = useCallback((token, user) => {
    const data = { token, user };
    localStorage.setItem("mesa_auth", JSON.stringify(data));
    setAuth(data);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("mesa_auth");
    setAuth(null);
  }, []);

  return (
    <AuthContext.Provider value={{ auth, login, logout, user: auth?.user, token: auth?.token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
