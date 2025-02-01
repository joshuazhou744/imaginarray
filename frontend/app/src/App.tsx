// App.tsx
import { FC } from 'react';
import ArrayVisualizer from "./components/ArrayVisualizer"
import { Manipulation } from "./utils/manipulateTypes";
import CodeWindow from './components/CodeWindow';
import './styles/App.css';

const App: FC = () => {

  const initialArray = [1, 2, 3];

  const manipulations: Manipulation<unknown>[] = [
    { type: 'append', value: 4 },
    { type: 'append', value: 5 },
    {type: "reverse"}
  ];

  return (
    <div className="split-screen-container">
      <div className='left'>
          <CodeWindow/>
      </div>
      <div className='right'>
        <h2>Array Manipulation Visualization</h2>
        <ArrayVisualizer initialArray={initialArray} manipulations={manipulations}/>
      </div>
    </div>
  )
}

export default App
