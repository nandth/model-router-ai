import { useState, useContext, useEffect } from "react";
import arrowIcon from "../assets/image.png";
import TextType from "../components/TextType";
import GlassSurface from "../components/GlassSurface";
import { PromptContext } from "../App";
import { BarLoader } from "react-spinners";
import SplitText from "../components/SplitText";
import { Link } from "react-router-dom";
import homeIcon from "../assets/home.png";

const apiKey = import.meta.env.VITE_API_KEY;

function Resultpage() {
  const { prompt, setPrompt } = useContext(PromptContext);
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [inputText, setInputText] = useState(prompt);
  const { response, ...restData } = data;
  const fetchData = async () => {
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

  const renderJSON = (obj) => {
    if (!obj || Object.keys(obj).length === 0) {
      return <span className="opacity-60">No Data Received</span>;
    }

    const json = JSON.stringify(obj, null, 2);

    const regex =
      /"(?:\\.|[^"])*"(?=\s*:)|"(?:\\.|[^"])*"|\btrue\b|\bfalse\b|\bnull\b|-?\d+(?:\.\d+)?/g;

    const elements = [];
    let lastIndex = 0;

    for (const match of json.matchAll(regex)) {
      const start = match.index;
      const token = match[0];

      // Push text between tokens
      if (start > lastIndex) {
        elements.push(
          <span key={lastIndex}>{json.slice(lastIndex, start)}</span>,
        );
      }

      // Keys
      if (
        token.startsWith('"') &&
        json
          .slice(start + token.length)
          .trim()
          .startsWith(":")
      ) {
        elements.push(
          <span key={start} className="text-[#9cdcfe]">
            {token}
          </span>,
        );
      }
      // Strings
      else if (token.startsWith('"')) {
        elements.push(
          <span key={start} className="text-[#ce9178]">
            {token}
          </span>,
        );
      }
      // Numbers
      else if (!isNaN(token)) {
        elements.push(
          <span key={start} className="text-[#b5cea8]">
            {token}
          </span>,
        );
      }
      // Booleans
      else if (token === "true" || token === "false") {
        elements.push(
          <span key={start} className="text-[#569cd6]">
            {token}
          </span>,
        );
      }
      // Null
      else if (token === "null") {
        elements.push(
          <span key={start} className="text-[#c586c0]">
            {token}
          </span>,
        );
      }

      lastIndex = start + token.length;
    }

    // Push remaining text
    if (lastIndex < json.length) {
      elements.push(<span key={lastIndex}>{json.slice(lastIndex)}</span>);
    }

    return elements;
  };

  useEffect(() => {
    fetchData(prompt);
  }, []);

  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleClick();
    }
  };

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
    <div className="w-full h-full flex justify-around">
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
        <GlassSurface
          width={50}
          height={50}
          borderRadius={24}
          className="pl-2.5 pr-1.5 flex items-center justify-center gap-5 bg-[#c7c7c7]"
          displace={0}
          distortionScale={0}
        >
          <button className="aspect-square w-12.5 rounded-full flex justify-center items-center">
            <Link to={"/"}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#c7c7c7"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-house-icon lucide-house"
              >
                <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
                <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              </svg>
            </Link>
          </button>
        </GlassSurface>
      </nav>
      <div className="min-w-[50%] relative z-10 flex flex-col justify-center items-center gap-12.5">
        <div className="flex flex-col justify-around items-center gap-3.5">
          <SplitText
            text="Information about the response received"
            className="text-2xl font-semibold text-center text-[#171717]"
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
          <pre className="text-left text-sm font-mono bg-[#1e1e1e] text-[#d4d4d4] p-4 rounded-xl max-h-[400px] overflow-auto w-full">
            {renderJSON(restData)}
          </pre>
        </div>
      </div>
      <div className="min-w-[50%] relative z-10 flex flex-col justify-center items-center gap-12.5">
        <div className="flex flex-col justify-around items-center gap-3.5 text-left text-l font-mono bg-[#1e1e1e] text-[#d4d4d4] p-4 rounded-xl max-h-100 overflow-auto w-full">
          <TextType
            text={data.response || "No response received"}
            typingSpeed={30}
            pauseDuration={1500}
            showCursor
            loop={false}
            cursorCharacter="_"
            texts={["this is result"]}
            className="text-l font-semibold text-center text-[#C7C7C7]"
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
    </div>
  );
}

export default Resultpage;
