// App.tsx
import { FC } from 'react';
import ArrayVisualizer from "./components/ArrayVisualizer"
import { Manipulation } from "./utils/manipulateTypes";

const App: FC = () => {

  const initialArray = [1, 'two', { three: 3 }];

  const manipulations: Manipulation<unknown>[] = [
    { type: 'append', value: 4 },
    { type: 'append', value: 'five' },
    { type: 'append', value: { six: 6 } },
    { type: 'reverse'}
  ];

  return (
    <div>
      <h2>Array Manipulation Visualization</h2>
      <ArrayVisualizer initialArray={initialArray} manipulations={manipulations}/>
    </div>
  )
}

export default App
