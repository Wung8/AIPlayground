// src/routes.jsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Environments from "./pages/Environments";
import EnvDoc from "./pages/EnvDoc";
import Play from "./pages/Play";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/environments" element={<Environments />} />
      <Route path="/environments/:slug" element={<EnvDoc />} />
      <Route path="/play/:envSlug" element={<Play />} />
      <Route path="*" element={<Home />} />
    </Routes>
  );
}
