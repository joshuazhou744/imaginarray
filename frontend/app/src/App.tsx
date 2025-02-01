// App.tsx
import { FC } from 'react';
import ArrayVisualizer from "./components/ArrayVisualizer"
import { Manipulation } from "./utils/manipulateTypes";
import CodeWindow from './components/CodeWindow';

const App: FC = () => {

  const initialArray = [1, 'two', { three: 3 }];

  const manipulations: Manipulation<unknown>[] = [
    { type: 'append', value: 4 },
    { type: 'append', value: 'five' },
    { type: 'append', value: { six: 6 } },
  ];

  return (
    <div className="split-screen">
      <div className='left'>
          <CodeWindow></CodeWindow>
      </div>
      <div className='right'>
        <h2>Array Manipulation Visualization</h2>
        <ArrayVisualizer initialArray={initialArray} manipulations={manipulations}/>
      </div>

      
    </div>
  )
}

export default App
