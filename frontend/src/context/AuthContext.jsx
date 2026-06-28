import { createContext, useContext, useState, useCallback, useEffect, useRef } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    try {
      const stored = localStorage.getItem("mesa_auth");
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });
  const [sessionMsg, setSessionMsg] = useState(null);
  const checkRef = useRef(null);

  const login = useCallback((token, user) => {
    const data = { token, user };
    localStorage.setItem("mesa_auth", JSON.stringify(data));
    setAuth(data);
    setSessionMsg(null);
  }, []);

  const logout = useCallback((msg) => {
    localStorage.removeItem("mesa_auth");
    setAuth(null);
    if (msg) setSessionMsg(msg);
  }, []);

  // Escuchar evento global de sesión expirada (emitido por client.js en 401)
  useEffect(() => {
    const handler = () => logout("Tu sesión expiró. Por favor vuelve a iniciar sesión.");
    window.addEventListener("session-expired", handler);
    return () => window.removeEventListener("session-expired", handler);
  }, [logout]);

  // Verificar sesión activa cada 2 minutos mientras está logueado
  useEffect(() => {
    if (!auth) {
      clearInterval(checkRef.current);
      return;
    }
    const check = async () => {
      try {
        await api.me();
      } catch (err) {
        if (err.message === "Sesión expirada") {
          // El handler de session-expired ya se encarga
        }
      }
    };
    checkRef.current = setInterval(check, 2 * 60 * 1000);
    return () => clearInterval(checkRef.current);
  }, [auth]);

  return (
    <AuthContext.Provider value={{ auth, login, logout, user: auth?.user, token: auth?.token, sessionMsg }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
