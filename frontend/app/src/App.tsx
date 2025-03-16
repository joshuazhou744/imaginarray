import { FC, useState } from "react";
import ArrayVisualizer from "./components/ArrayVisualizer";
import { Manipulation } from "./utils/manipulateTypes";
import CodeWindow from './components/CodeWindow';
import axios from 'axios';
import './styles/App.css';
import Dropdown from './components/Dropdown';

const App: FC = () => {
  const [initialArray, setInitialArray] = useState<number[]>([]);
  const [manipulations, setManipulations] = useState<Manipulation<unknown>[]>([]);
  const [lineNums, setLineNums] = useState<number[]>([]);
  const [initialized, setInitialized] = useState(false);
  const [highlightedLine, setHighlightedLine] = useState<number | null>(null);
  const [code, setCode] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const SERVER_URL = import.meta.env.VITE_SERVER_URL;

  const parseCode = async (code: string) => {
    setInitialized(false);
    setInitialArray(initialArray);
    try {
      const lines = code.split("\n");
      const response = await axios.post(`${SERVER_URL}/submit_code`, {
        code: lines,
      });

      setInitialArray(response.data.initial_arr || []);
      setManipulations(response.data.manipulations || []);
      setLineNums(response.data.line_nums || []);
      console.log("RESPONSE:", response.data);
      setInitialized(true);
      setHighlightedLine(null);
    } catch (error) {
      console.error('DAMMIT ERROR :( :\n', error);
    }
  };

  const handlePreset = (preset: string) => {
    setCode(preset)
  }

  return (
    <div className="split-screen-container">
      <div className="left">
        <CodeWindow parseCode={parseCode} highlightedLine={highlightedLine} code={code} isProcessing={isProcessing} setIsProcessing={setIsProcessing}/>
      </div>
      <div className="right">
        <div className="visualizer-header">
          <h2>ImaginArray</h2>
        </div>
        <div className="dropdown-container">
          <Dropdown handlePreset={handlePreset} />
        </div>

        {initialized && (
          <ArrayVisualizer 
            initialArray={initialArray} 
            manipulations={manipulations} 
            lineNums={lineNums}
            setHighlightedLine={setHighlightedLine}
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing} 
          />
        )}
      </div>
    </div>
  );
};

export default App;
