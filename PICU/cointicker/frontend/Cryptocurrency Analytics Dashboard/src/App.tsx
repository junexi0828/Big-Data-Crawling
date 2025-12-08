import { useState } from "react";
import { Navigation } from "./components/navigation";
import { DashboardPage } from "./components/dashboard-page";
import { NewsPage } from "./components/news-page";
import { InsightsPage } from "./components/insights-page";
import { ScrollToTop } from "./components/scroll-to-top";
import { ScrollProgress } from "./components/scroll-progress";

export default function App() {
  const [currentPage, setCurrentPage] = useState<"dashboard" | "news" | "insights">("dashboard");

  return (
    <div className="min-h-screen bg-[#0b0e11]">
      <ScrollProgress />
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />

      <main className="max-w-[1440px] mx-auto px-5 lg:px-8 py-8">
        {currentPage === "dashboard" && <DashboardPage />}
        {currentPage === "news" && <NewsPage />}
        {currentPage === "insights" && <InsightsPage />}
      </main>

      <ScrollToTop />

      {/* Footer */}
      <footer className="border-t border-[#2b3139] mt-16">
        <div className="max-w-[1440px] mx-auto px-5 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center">
                <span className="text-sm">₿</span>
              </div>
              <span className="text-[#848e9c] text-sm">Crypto Analytics Dashboard</span>
            </div>
            <div className="text-[#848e9c] text-sm">
              Built with React & Tailwind CSS
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}