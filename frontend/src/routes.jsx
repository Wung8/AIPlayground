// src/routes.jsx
import React from "react";
import { Routes as RouterRoutes, Route, Outlet } from "react-router-dom";

import Layout from "./components/Layout";

import Home from "./pages/Home";
import Environments from "./pages/Environments";
import EnvDoc from "./pages/EnvDoc";
import Play from "./pages/Play";

function AppLayout() {
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
}

export default function AppRoutes() {
  return (
    <RouterRoutes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/environments" element={<Environments />} />
        <Route path="/environments/:slug" element={<EnvDoc />} />
        <Route path="/play/:envSlug" element={<Play />} />
        <Route path="*" element={<Home />} />
      </Route>
    </RouterRoutes>
  );
}
