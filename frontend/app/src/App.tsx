import { FC, useState } from "react";
import ArrayVisualizer from "./components/ArrayVisualizer";
import { Manipulation } from "./utils/manipulateTypes";
import CodeWindow from './components/CodeWindow';
import axios from 'axios';
import './styles/App.css';

const App: FC = () => {

  const [initialArray, setInitialArray] = useState<number[]>([]);
  const [manipulations, setManipulations] = useState<Manipulation<unknown>[]>([]);

  const parseCode = async (code: string) => {
    try {
      const lines = code.split("\n");
      const response = await axios.post('http://172.30.145.175:4000/submit_code', {
        code: lines,
      });

      setInitialArray(response.data.initial_arr || []); 
      setManipulations(response.data.manipulations || []);  
      console.log(response.data)
      console.log(initialArray)
      console.log(manipulations)
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
        <h2>Array Manipulation Visualization</h2>
        <ArrayVisualizer initialArray={initialArray} manipulations={manipulations}/>
      </div>
    </div>
  );
};

export default App;
