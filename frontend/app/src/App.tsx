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

  const parseCode = async (code: string) => {
    setInitialized(false);
    setInitialArray(initialArray);
    try {
      const lines = code.split("\n");
      const response = await axios.post('/api/submit_code', {
        code: lines,
      });

      setInitialArray(response.data.initial_arr || []);
      setManipulations(response.data.manipulations || []);
      setLineNums(response.data.line_nums || []);
      console.log("RESPONSE:", response.data);
      setInitialized(true);
      setHighlightedLine(null);
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        if (error.response?.data?.error) {
          alert(`Execution Error: ${error.response.data.error}`);
        }
        console.error("Axios error:\n", error);
      } else {
        console.error("Unknown error:\n", error);
      }
    }
  }
    

  const handlePreset = (preset: string) => {
    setCode(preset)
  }

  return (
    <div className="homepage">
      <div className="visualizer-header">
          <h2>ImagArray</h2>
      </div>
      <div className="split-screen-container">
        <div className="left">
          <CodeWindow parseCode={parseCode} highlightedLine={highlightedLine} code={code} isProcessing={isProcessing} setIsProcessing={setIsProcessing}/>
        </div>

        <div className="right">
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
    </div>

  );
};

export default App;
