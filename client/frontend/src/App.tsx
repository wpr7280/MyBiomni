import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import SSOLogin from './pages/SSOLogin';
import ChangePassword from './pages/ChangePassword';
import Profile from './pages/Profile';
import ChatLayout from './pages/ChatLayout';
import { useAuthStore } from './store/authStore';

function App() {
  const { token } = useAuthStore();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/sso" element={<SSOLogin />} />
      <Route
        path="/change-password"
        element={token ? <ChangePassword /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/profile"
        element={token ? <Profile /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/*"
        element={token ? <ChatLayout /> : <Navigate to="/login" replace />}
      />
    </Routes>
  );
}

export default App;
