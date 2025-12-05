import { LayoutDashboard, Newspaper, Lightbulb, Menu, X } from "lucide-react";
import { useState } from "react";

interface NavigationProps {
  currentPage: "dashboard" | "news" | "insights";
  onNavigate: (page: "dashboard" | "news" | "insights") => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const navItems = [
    { id: "dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
    { id: "news" as const, label: "News", icon: Newspaper },
    { id: "insights" as const, label: "Insights", icon: Lightbulb },
  ];

  const handleNavigate = (page: "dashboard" | "news" | "insights") => {
    onNavigate(page);
    setMobileMenuOpen(false);
  };

  return (
    <nav className="border-b border-border bg-card sticky top-0 z-50 backdrop-blur-sm bg-[#1e2329]/95">
      <div className="max-w-[1440px] mx-auto px-5 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center shadow-lg">
              <span className="text-lg">₿</span>
            </div>
            <h1 className="text-[#eaecef] tracking-tight">Crypto Analytics</h1>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                    ${
                      isActive
                        ? "bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white shadow-lg"
                        : "text-[#848e9c] hover:text-[#eaecef] hover:bg-[#2b3139]"
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-[#eaecef] p-2 hover:bg-[#2b3139] rounded-lg transition-colors"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-2 animate-in slide-in-from-top duration-200">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`
                    w-full flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                    ${
                      isActive
                        ? "bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white"
                        : "text-[#848e9c] hover:text-[#eaecef] hover:bg-[#2b3139]"
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </nav>
  );
}