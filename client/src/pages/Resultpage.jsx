import { useState, useContext, useEffect, useRef } from "react";
import arrowIcon from "../assets/image.png";
import TextType from "../components/TextType";
import GlassSurface from "../components/GlassSurface";
import { useNavigate } from "react-router-dom";
import { PromptContext } from "../App";

function Resultpage({ setLoadingChat, setRenderResultPage }) {
  const { prompt, setPrompt } = useContext(PromptContext);
  const [inputText, setInputText] = useState(prompt);
  const navigate = useNavigate();
  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  useEffect(() => {
    setLoadingChat(true);
    fetch("https://jsonplaceholder.typicode.com/todos/1")
      .then((response) => response.json())
      .then((json) => console.log(json))
      .finally(() => {
        setLoadingChat(false);
      });
  }, []);

  const handleClick = () => {
    setPrompt(inputText);
    navigate("/chat");
  };

  return (
    <div className="relative z-10 flex flex-col justify-center items-center gap-12.5">
      <div className="flex flex-col justify-around items-center gap-3.5">
        <TextType
          text={
            'The meaning of life can vary greatly between different philosophical views, religions, and individuals, but generally, it could be viewed as the pursuit of happiness, seeking knowledge, or contributing to society or the greater good. \n\nDogs have eyes, feet, and hair as a result of millions of years of evolution. Eyes allow them to perceive their surroundings, feet enable them to move and explore those surroundings, and hair (or fur) helps regulate their body temperature and provides some level of protection.\n\nDogs are not blue because color in animals is determined by genes and evolution. The colors we see in dogs today are the result of selective breeding by humans. However, there are "blue" dogs, but in the animal world, "blue" refers to a type of gray.\n\nThe phrase "roses grown in the sky" is not literal. Roses grow from the ground, not the sky. It might be a metaphor or an expression, meaning might depend on the context.\n\nPotatoes are actually not grown in water, they are grown in soil. However, they need a fair amount of water to grow correctly. Potato plants love well-drained, loose soil.\n\nThe concept of God varies greatly among different religions and belief systems. In monotheistic religions like Christianity, Judaism, Islam, God is seen as an all-powerful, all-knowing entity who is responsible for the creation of the universe. In non-theistic religions or philosophical systems, the concept of "God" might not exist or might be understood differently.\n\nThe color of your skin is determined by a pigment called melanin produced by cells in your skin called melanocytes. The amount of melanin you have generally decides the color of your skin, hair, and eyes. If you have less melanin, your skin will be lighter (white). If you have more, your skin will be darker. The amount of melanin is primarily determined by genetics – it is inherited from your parents.'
          }
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
