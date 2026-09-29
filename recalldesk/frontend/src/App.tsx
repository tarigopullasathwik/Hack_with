import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import MemoryPage from './pages/MemoryPage';
import TicketsPage from './pages/TicketsPage';
import KnowledgePage from './pages/KnowledgePage';
import DemoPage from './pages/DemoPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/demo" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="chat/:customerId" element={<ChatPage />} />
          <Route path="memory" element={<MemoryPage />} />
          <Route path="memory/:customerId" element={<MemoryPage />} />
          <Route path="tickets" element={<TicketsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="demo" element={<DemoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
