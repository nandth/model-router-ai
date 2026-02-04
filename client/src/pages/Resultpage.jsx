import { useState, useContext, useEffect, useRef } from "react";
import arrowIcon from "../assets/image.png";
import TextType from "../components/TextType";
import GlassSurface from "../components/GlassSurface";
import { useNavigate } from "react-router-dom";
import { PromptContext } from "../App";
import { BarLoader } from "react-spinners";

const apiKey = import.meta.env.VITE_API_KEY;

function Resultpage({ setRenderResultPage }) {
  const { prompt, setPrompt } = useContext(PromptContext);
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [inputText, setInputText] = useState(prompt);
  const navigate = useNavigate();

  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key.toLowerCase() === "enter") {
      handleClick();
    }
  };

  useEffect(() => {
    if (!prompt) return;

    const fetchData = async (prompt) => {
      console.log(apiKey);
      try {
        const res = await fetch(apiKey, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
            route_mode: "auto",
            max_tokens: 500,
          }),
        });
        const response = await res.json();
        setData(response);
        console.log(response);
      } catch (error) {
        console.log(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData(prompt);
  }, [prompt]);

  const handleClick = async () => {
    setPrompt(inputText);

    setLoading(true);

    try {
      const res = await fetch(apiKey, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: inputText,
          route_mode: "auto",
          max_tokens: 500,
        }),
      });

      const response = await res.json();
      setData(response);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <BarLoader
        color="white"
        loading={true}
        width={250}
        size={150}
        aria-label="Loading Spinner"
        data-testid="loader"
      />
    );
  }

  return (
    <div className="relative z-10 flex flex-col justify-center items-center gap-12.5">
      <div className="flex flex-col justify-around items-center gap-3.5">
        <TextType
          text={data.response}
          typingSpeed={50}
          pauseDuration={1500}
          showCursor
          loop={false}
          cursorCharacter="_"
          texts={["this is result"]}
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

export default Resultpage;
