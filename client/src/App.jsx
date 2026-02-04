import Homepage from "./pages/Homepage";
import LoadingScreen from "./pages/LoadingScreen";

function App() {
  const loading = false;
  return loading ? <LoadingScreen /> : <Homepage />;
}

export default App;
