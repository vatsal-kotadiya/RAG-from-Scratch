import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Files, MessageSquare, BarChart } from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/documents', label: 'Documents', icon: Files },
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/evaluation', label: 'Evaluation', icon: BarChart },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-ink text-slate-200 p-5 flex flex-col gap-2 shrink-0">
        <div className="text-lg font-bold text-white mb-4">RAG Intelligence</div>
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                isActive ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800'
              }`
            }
          >
            <Icon size={18} /> {label}
          </NavLink>
        ))}
        <div className="mt-auto text-xs text-slate-500">RAG From Scratch v0.1</div>
      </aside>
      <main className="flex-1 p-6 max-w-6xl w-full mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
