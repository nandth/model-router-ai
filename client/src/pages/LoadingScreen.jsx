import CircularText from "../components/CircularText";
import { BarLoader } from "react-spinners";

function LoadingScreen({ loadingChat, loadingWebSite }) {
  return (
    <div>
      {loadingWebSite && (
        <CircularText
          text="LOADING"
          onHover="speedUp"
          spinDuration={20}
          className="custom-class h-2.5 w-2.5"
        />
      )}
      {!loadingWebSite && loadingChat && (
        <BarLoader
          color="white"
          loading={true}
          width={250}
          size={150}
          aria-label="Loading Spinner"
          data-testid="loader"
        />
      )}
    </div>
  );
}

export default LoadingScreen;
