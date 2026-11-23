import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Navbar } from "./components/Navbar";
import { PageId, Sidebar } from "./components/Sidebar";
import { AIModelRouting } from "./pages/AIModelRouting";
import { BenchmarkComparison } from "./pages/BenchmarkComparison";
import { DockerExecutionResults } from "./pages/DockerExecutionResults";
import { GeneratedTestCases } from "./pages/GeneratedTestCases";
import { OverviewDashboard } from "./pages/OverviewDashboard";
import { PullRequestReview } from "./pages/PullRequestReview";
import { RepositoryManagement } from "./pages/RepositoryManagement";
import { ReproducibilityEvidence } from "./pages/ReproducibilityEvidence";
import { StaticAnalysis } from "./pages/StaticAnalysis";
import { WebsiteManual } from "./pages/WebsiteManual";
import { ThemeProvider } from "./context/ThemeContext";
import { fetchHealth } from "./services/api";

const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>("overview");
  const [selectedPrId, setSelectedPrId] = useState<number | null>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .catch(() => {});
  }, []);

  const handleNavigateToPr = (prId: number) => {
    setSelectedPrId(prId);
    setCurrentPage("pr-review");
  };

  const renderPage = () => {
    switch (currentPage) {
      case "overview":
        return <OverviewDashboard onSelectPr={handleNavigateToPr} onNavigate={setCurrentPage} />;
      case "repos":
        return <RepositoryManagement onSelectPr={handleNavigateToPr} />;
      case "pr-review":
        return <PullRequestReview initialPrId={selectedPrId} onNavigate={setCurrentPage} />;
      case "static-analysis":
        return <StaticAnalysis />;
      case "model-routing":
        return <AIModelRouting />;
      case "test-cases":
        return <GeneratedTestCases />;
      case "docker-results":
        return <DockerExecutionResults />;
      case "evidence":
        return <ReproducibilityEvidence />;
      case "benchmarks":
        return <BenchmarkComparison />;
      case "manual":
        return <WebsiteManual onNavigate={setCurrentPage} />;
      default:
        return <OverviewDashboard onSelectPr={handleNavigateToPr} onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="h-screen max-h-screen overflow-hidden bg-paper text-ink font-sans flex flex-col selection:bg-accent-subtle selection:text-accent bg-dot-grid relative transition-colors duration-300">
      {/* Restrained Subtle Depth Highlight */}
      <div className="pointer-events-none fixed -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-accent/5 dark:bg-accent/15 blur-[120px] rounded-full z-0" />

      <Navbar systemHealth={health} onNavigate={setCurrentPage} />
      <div className="flex flex-1 overflow-hidden min-h-0 relative z-10">
        <Sidebar currentPage={currentPage} onSelectPage={setCurrentPage} />
        <main className="flex-1 h-full overflow-y-auto min-h-0 p-6 sm:p-8">
          <div className="max-w-7xl w-full mx-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
              >
                {renderPage()}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;
