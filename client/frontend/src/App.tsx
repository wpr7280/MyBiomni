import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import SSOLogin from './pages/SSOLogin';
import ChatLayout from './pages/ChatLayout';
import { useAuthStore } from './store/authStore';

function App() {
  const { token } = useAuthStore();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/sso" element={<SSOLogin />} />
      <Route
        path="/*"
        element={token ? <ChatLayout /> : <Navigate to="/login" replace />}
      />
    </Routes>
  );
}

export default App;
