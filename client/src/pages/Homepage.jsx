import { useState, useContext } from "react";
import arrowIcon from "../assets/image.png";
import SplitText from "../components/SplitText";
import TextType from "../components/TextType";
import GlassSurface from "../components/GlassSurface";
import { useNavigate } from "react-router-dom";
import { PromptContext } from "../App";

function Homepage({ setLoadingChat, setRenderResultPage }) {
  const { prompt, setPrompt } = useContext(PromptContext);
  const navigate = useNavigate();
  const [inputText, setInputText] = useState("");
  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleClick = () => {
    setPrompt(inputText);
    navigate("/chat");
  };

  const handleKeyDown = (event) => {
    if (event.key.toLowerCase() === "enter") {
      handleClick();
    }
  };

  return (
    <div className="relative z-10 flex flex-col justify-center items-center gap-12.5">
      <div className="flex flex-col justify-around items-center gap-3.5">
        <SplitText
          text="AI Model Router"
          className="text-5xl font-semibold text-center text-[#C7C7C7]"
          delay={50}
          duration={1.25}
          ease="power3.out"
          splitType="chars"
          from={{ opacity: 0, y: 40 }}
          to={{ opacity: 1, y: 0 }}
          threshold={0.1}
          rootMargin="-100px"
          textAlign="center"
          showCallback
        />
        <TextType
          text={[
            "Intelligent routing across AI model tiers",
            "Real-time token streaming responses",
            "Safer prompts with built-in validation",
            "Cost-aware decisions for every request",
            "Production-ready API with observability",
          ]}
          typingSpeed={75}
          pauseDuration={1500}
          showCursor
          cursorCharacter="_"
          texts={[
            "Welcome to React Bits! Good to see you!",
            "Build some amazing experiences!",
          ]}
          className="text-3xl font-semibold text-center text-[#C7C7C7]"
          deletingSpeed={50}
          variableSpeedEnabled={false}
          variableSpeedMin={60}
          variableSpeedMax={120}
          cursorBlinkDuration={0.5}
        />
      </div>
      <GlassSurface
        width={400}
        height={48}
        borderRadius={24}
        className="pl-2.5 pr-1.5 flex items-center justify-around gap-5 text-[#C7C7C7]"
      >
        <input
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          type="text"
          value={inputText}
          name="prompt"
          id="prompt"
          className="flex-1 h-5.5 focus:outline-0 placeholder:text-[#C7C7C7]"
          placeholder="Ask Anything"
        />
        <button
          onClick={handleClick}
          type="submit"
          className="h-9 aspect-square bg-[#C7C7C7] rounded-full flex items-center justify-center hover:cursor-pointer"
        >
          <img src={arrowIcon} className="aspect-square h-[11.67px]" />
        </button>
      </GlassSurface>
    </div>
  );
}

export default Homepage;
