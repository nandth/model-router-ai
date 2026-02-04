import { Routes, Route } from "react-router-dom";
import Homepage from "../pages/Homepage";
import Resultpage from "../pages/Resultpage";

function AppRoutes({ setRenderResultPage }) {
  return (
    <Routes>
      <Route
        path="/"
        element={<Homepage setRenderResultPage={setRenderResultPage} />}
      />
      <Route
        path="/chat"
        element={<Resultpage setRenderResultPage={setRenderResultPage} />}
      />
    </Routes>
  );
}

export default AppRoutes;
