import { Routes, Route } from "react-router-dom";
import Homepage from "../pages/Homepage";
import Resultpage from "../pages/Resultpage";

function AppRoutes({ setLoadingChat, setRenderResultPage }) {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Homepage
            setLoadingChat={setLoadingChat}
            setRenderResultPage={setRenderResultPage}
          />
        }
      />
      <Route
        path="/chat"
        element={
          <Resultpage
            setLoadingChat={setLoadingChat}
            setRenderResultPage={setRenderResultPage}
          />
        }
      />
    </Routes>
  );
}

export default AppRoutes;
