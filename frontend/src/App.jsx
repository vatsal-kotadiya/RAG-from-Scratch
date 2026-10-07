import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Documents from './pages/Documents.jsx';
import Chat from './pages/Chat.jsx';
import Evaluation from './pages/Evaluation.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="chat" element={<Chat />} />
          <Route path="evaluation" element={<Evaluation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
