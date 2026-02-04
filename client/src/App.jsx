import { createContext, useEffect, useState } from "react";
import Homepage from "./pages/Homepage";
import LoadingScreen from "./pages/LoadingScreen";
import Grainient from "./components/Grainient";
import Resultpage from "./pages/Resultpage";
import AppRoutes from "./routes/AppRoutes";

export const PromptContext = createContext({});

function App() {
  const [loadingWebSite, setLoadingWebSite] = useState(true);
  const [renderResultPage, setRenderResultPage] = useState(false);
  const [prompt, setPrompt] = useState("");

  useEffect(() => {
    const num = Math.floor(Math.random() * 5) + 1;
    setTimeout(() => {
      setLoadingWebSite(false);
    }, num * 1000);
  }, []);

  if (loadingWebSite) {
    return (
      <div className="w-screen h-screen relative overflow-hidden flex justify-center items-center">
        <div className="absolute inset-0 -z-10">
          <Grainient
            color1="#c7c7c7"
            color2="#171717"
            color3="#000000"
            timeSpeed={0.25}
            colorBalance={0}
            warpStrength={1}
            warpFrequency={5}
            warpSpeed={2}
            warpAmplitude={50}
            blendAngle={0}
            blendSoftness={0.05}
            rotationAmount={500}
            noiseScale={2}
            grainAmount={0.1}
            grainScale={2}
            grainAnimated={false}
            contrast={1.5}
            gamma={1}
            saturation={1}
            centerX={0}
            centerY={0}
            zoom={0.9}
          />
        </div>
        <LoadingScreen loadingWebSite={loadingWebSite} />
      </div>
    );
  }
  return (
    <PromptContext value={{ prompt, setPrompt }}>
      <div className="w-screen h-screen relative overflow-hidden flex justify-center items-center">
        <div className="absolute inset-0 -z-10">
          <Grainient
            color1="#c7c7c7"
            color2="#171717"
            color3="#000000"
            timeSpeed={0.25}
            colorBalance={0}
            warpStrength={1}
            warpFrequency={5}
            warpSpeed={2}
            warpAmplitude={50}
            blendAngle={0}
            blendSoftness={0.05}
            rotationAmount={500}
            noiseScale={2}
            grainAmount={0.1}
            grainScale={2}
            grainAnimated={false}
            contrast={1.5}
            gamma={1}
            saturation={1}
            centerX={0}
            centerY={0}
            zoom={0.9}
          />
        </div>
        <AppRoutes setRenderResultPage={setRenderResultPage} />
      </div>
    </PromptContext>
  );
}

export default App;
