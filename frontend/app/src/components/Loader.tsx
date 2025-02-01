// Loader.tsx
import "../styles/Loader.css";

const Loader = () => {
  return (
    <div className="loader-container">
      <div className="loader">
        <div className="square" id="sq1"></div>
        <div className="square" id="sq2"></div>
        <div className="square" id="sq3"></div>
        <div className="square" id="sq4"></div>
        <div className="square" id="sq5"></div>
        <div className="square" id="sq6"></div>
        <div className="square" id="sq7"></div>
        <div className="square" id="sq8"></div>
        <div className="square" id="sq9"></div>
      </div>
      <h3>Visualizing</h3>
    </div>
  );
};

export default Loader;
