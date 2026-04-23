import { Menu } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "Tentang SPBE" },
  { to: "/documents", label: "Documents" },
  { to: "/chat/vector", label: "Chatbot SPBE" },
  { to: "/knowledge-graph", label: "Knowledge Graph" },
  { to: "/chat/graph", label: "Graph Chat" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/prompt-templates", label: "Template Prompt" },
  { to: "/research", label: "Hasil Penelitian" }
];

export function AppShell() {
  const [open, setOpen] = useState(false);

  return (
    <div className="editorial-grid min-h-screen lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-[82vw] max-w-[320px] border-r border-[var(--line)] bg-[var(--background)]/95 p-6 backdrop-blur-xl transition duration-300 lg:static lg:w-auto lg:max-w-none lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex items-center justify-between pb-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--muted)]">SPBEBOT</p>
            <h1 className="display-serif text-4xl italic">workspace</h1>
          </div>
          <button className="lg:hidden" onClick={() => setOpen(false)}>
            close
          </button>
        </div>

        <div className="space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex min-h-12 items-center rounded-2xl px-4 py-3 text-sm transition",
                  isActive
                    ? "font-medium shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]"
                    : "text-[var(--muted)] hover:bg-black/5 hover:text-[var(--foreground)]",
                )
              }
              style={({ isActive }) =>
                isActive
                  ? {
                      backgroundColor: "var(--foreground)",
                      color: "#ffffff",
                    }
                  : undefined
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        <div className="mt-10 border-t border-[var(--line)] pt-6 text-xs leading-6 text-[var(--muted)]">
          Platform Information Retrieval pada dokumen Panduan Monitoring dan Evaluasi Sistem Pemerintahan Berbasis Elektronik (SPBE)
        </div>
      </aside>

      <div className="min-h-screen">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-[var(--line)] bg-[var(--background)]/75 px-4 py-4 backdrop-blur-xl lg:px-8">
          <button className="rounded-full border border-[var(--line)] p-3 lg:hidden" onClick={() => setOpen(true)}>
            <Menu className="h-4 w-4" />
          </button>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">SPBEBOT Platform</p>
          </div>
          <p className="text-right text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
            Retrieval-Augmented Generation Vector and Graph
          </p>
        </header>

        <main className="px-4 py-6 lg:px-8 lg:py-10">
          <Outlet />
        </main>

        <footer className="border-t border-[var(--line)] px-4 py-5 text-xs uppercase tracking-[0.22em] text-[var(--muted)] lg:px-8">
          <p>Copyright © Regi Muhammar. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}
