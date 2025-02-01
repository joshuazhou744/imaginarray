// ArrayVisualizer.tsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Manipulation } from '../utils/manipulateTypes';


interface ArrayVisualizerProps<T> {
  initialArray: T[];
  manipulations: Manipulation<T>[];
}

const ArrayVisualizer = <T,>({ initialArray, manipulations }: ArrayVisualizerProps<T>): JSX.Element => {
  const [displayArray, setDisplayArray] = useState<T[]>(initialArray);

  useEffect(() => {
    let currentIndex = 0;
    const processNextManipulation = () => {
      if (currentIndex < manipulations.length) {
        const instruction = manipulations[currentIndex];
        if (instruction.type === 'append') {
          setDisplayArray(prevArray => [...prevArray, instruction.value]);
        }
        currentIndex += 1;
        setTimeout(processNextManipulation, 1000);
      }
    };

    processNextManipulation();
  }, [manipulations]);

  return (
    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
      <AnimatePresence>
        {displayArray.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}     
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.5 }}      
            style={{
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '5px',
              backgroundColor: '#f0f0f0'
            }}
          >
            {JSON.stringify(item)}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ArrayVisualizer;
