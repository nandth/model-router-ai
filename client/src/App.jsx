import { useEffect, useState } from "react";
import Homepage from "./pages/Homepage";
import LoadingScreen from "./pages/LoadingScreen";

function App() {
  const [loadingChat, setLoadingChat] = useState(false);
  const [loadingWebSite, setLoadingWebSite] = useState(true);
  useEffect(() => {
    const num = Math.floor(Math.random() * 5) + 1;
    setTimeout(() => {
      setLoadingWebSite(false);
    }, num * 1000);
  }, []);
  return loadingChat || loadingWebSite ? (
    <LoadingScreen loadingChat={loadingChat} loadingWebSite={loadingWebSite} />
  ) : (
    <Homepage setLoadingChat={setLoadingChat} />
  );
}

export default App;
