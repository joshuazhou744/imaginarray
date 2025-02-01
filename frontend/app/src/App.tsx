import { FC, useState } from "react";
import ArrayVisualizer from "./components/ArrayVisualizer";
import { Manipulation } from "./utils/manipulateTypes";
import CodeWindow from './components/CodeWindow';
import axios from 'axios';
import './styles/App.css';

const App: FC = () => {

  const [initialArray, setInitialArray] = useState<number[]>([]);
  const [manipulations, setManipulations] = useState<Manipulation<unknown>[]>([]);
  const [initialized, setInitialized] = useState(false);

  const parseCode = async (code: string) => {
    setInitialized(false);
    setInitialArray([]);
    try {
      const lines = code.split("\n");
      const response = await axios.post('http://127.0.0.1:4000/submit_code', {
        code: lines,
      });

      setInitialArray(response.data.initial_arr || []); 
      setManipulations(response.data.manipulations || []);  
      console.log(response.data)
      console.log(initialArray)
      console.log(manipulations)
      setInitialized(true);
    } catch (error) {
      console.error('DAMMIT ERROR :( :\n', error);
    }
  };

  return (
    <div className="split-screen-container">
      <div className="left">
        <CodeWindow parseCode={parseCode} />
      </div>
      <div className="right">
        <h2>ImagArray</h2>
        {initialized && <ArrayVisualizer initialArray={initialArray} manipulations={manipulations}/>}
      </div>
    </div>
  );
};

export default App;
