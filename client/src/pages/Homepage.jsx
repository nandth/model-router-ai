import { useState } from "react";
import arrowIcon from "../assets/image.png";

function Homepage({ setLoadingChat }) {
  const [inputText, setInputText] = useState("");
  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleClick = (event) => {
    setLoadingChat(true);

    setTimeout(() => {
      setLoadingChat(false);
    }, 2000);
  };

  return (
    <div className="w-screen h-screen bg-[#171717] flex flex-col justify-center items-center">
      <div className="w-100 h-12 pl-2.5 pr-1.5 bg-[#272727] flex items-center justify-around gap-5 rounded-3xl text-[#C7C7C7]">
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
      </div>
    </div>
  );
}

export default Homepage;
