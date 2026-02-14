import { createContext, useEffect, useState } from "react";
import { Link } from "react-router-dom"; // Import Link
import Homepage from "./pages/Homepage";
import LoadingScreen from "./pages/LoadingScreen";
import Grainient from "./components/Grainient";
import Resultpage from "./pages/Resultpage";
import AppRoutes from "./routes/AppRoutes";
import GlassSurface from "./components/GlassSurface"; // Import GlassSurface

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
        
        {/* --- GLOBAL NAVIGATION BAR --- */}
        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex gap-4">
          
          {/* 1. Home Button */}
          <GlassSurface
            width={50}
            height={50}
            borderRadius={24}
            className="flex items-center justify-center transition-transform hover:scale-110 cursor-pointer"
          >
            <Link to="/" className="w-full h-full flex items-center justify-center">
               <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c7c7c7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
                  <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
               </svg>
            </Link>
          </GlassSurface>

          {/* 2. Analytics Button */}
          <GlassSurface
            width={50}
            height={50}
            borderRadius={24}
            className="flex items-center justify-center transition-transform hover:scale-110 cursor-pointer"
          >
            <Link to="/analytics" className="w-full h-full flex items-center justify-center">
               <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c7c7c7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
            </Link>
          </GlassSurface>

        </nav>
        {/* ----------------------------- */}

        <AppRoutes setRenderResultPage={setRenderResultPage} />
      </div>
    </PromptContext>
  );
}

export default App;