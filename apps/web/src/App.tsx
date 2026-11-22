import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { PublicLayout } from "./components/layout/PublicLayout";
import { TerminalLayout } from "./components/layout/TerminalLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { CountriesPage } from "./pages/CountriesPage";
import { CountryDetailPage } from "./pages/CountryDetailPage";
import { IndicatorsPage } from "./pages/IndicatorsPage";
import { MarketsPage } from "./pages/MarketsPage";
// Terminal Pages
import { TerminalDashboard } from "./pages/TerminalDashboard";
import { TerminalMacro } from "./pages/TerminalMacro";
import { TerminalMarkets } from "./pages/TerminalMarkets";
import { TerminalCountries } from "./pages/TerminalCountries";

import { useAuthStore } from "./stores/auth";

export default function App() {
  const initialize = useAuthStore((s) => s.initialize);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  return (
    <Routes>
      {/* PUBLIC ROUTES */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/countries" element={<CountriesPage />} />
        <Route path="/countries/:iso2" element={<CountryDetailPage />} />
        <Route path="/indicators" element={<IndicatorsPage />} />
        <Route path="/markets" element={<MarketsPage />} />
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>

      {/* PROTECTED TERMINAL ROUTES */}
      <Route element={<ProtectedRoute />}>
        <Route element={<TerminalLayout />}>
          <Route path="/terminal" element={<Navigate to="/terminal/dashboard" replace />} />
          <Route path="/terminal/dashboard" element={<TerminalDashboard />} />
          <Route path="/terminal/macro" element={<TerminalMacro />} />
          <Route path="/terminal/markets" element={<TerminalMarkets />} />
          <Route path="/terminal/countries" element={<TerminalCountries />} />
        </Route>
      </Route>
    </Routes>
  );
}