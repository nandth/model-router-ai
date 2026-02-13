import { Routes, Route } from "react-router-dom";
import Homepage from "../pages/Homepage";
import Resultpage from "../pages/Resultpage";
import Analyticspage from "../pages/Analyticspage";

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
      <Route
        path="/analytics"
        element={<Analyticspage />}
      />
    </Routes>
  );
}

export default AppRoutes;
