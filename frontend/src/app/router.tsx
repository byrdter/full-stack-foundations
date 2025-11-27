import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom";

import { Layout } from "@/shared/components/Layout";
import { HomePage } from "./routes/HomePage";
import { ErrorPage } from "./routes/ErrorPage";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />} errorElement={<ErrorPage />}>
      <Route index element={<HomePage />} />
      <Route path="*" element={<HomePage />} />
    </Route>,
  ),
);
