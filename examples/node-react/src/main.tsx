import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { NotesPage } from "./NotesPage";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("missing #root element");
}

createRoot(root).render(
  <StrictMode>
    <NotesPage />
  </StrictMode>,
);
