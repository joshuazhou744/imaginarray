// ArrayVisualizer.tsx
import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Manipulation } from '../utils/manipulateTypes';


interface ArrayVisualizerProps<T> {
  initialArray: T[];
  manipulations: Manipulation<T>[];
}

const ArrayVisualizer = <T,>({ initialArray, manipulations }: ArrayVisualizerProps<T>): JSX.Element => {
    const [displayArray, setDisplayArray] = useState<T[]>(initialArray);
    const processingRef = useRef(false);

    const processManipulations = () => {
        if (processingRef.current) return;
        processingRef.current = true;
    
        let currentIndex = 0;
    
        const processNext = () => {
          if (currentIndex < manipulations.length) {
            const instruction = manipulations[currentIndex];
            if (instruction.type === 'append') {
              setDisplayArray(prevArray => [...prevArray, instruction.value]);
            } else if (instruction.type === 'pop') {
              setDisplayArray(prevArray => {
                const newArray = [...prevArray];
                newArray.pop();
                return newArray;
              });
            }
            currentIndex += 1;
            setTimeout(processNext, 1000);
          } else {
            processingRef.current = false;
          }
        };
    
        processNext();
      };

    return (
        <div>
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
            <button onClick={processManipulations} style={{ marginTop: '20px' }}>
                manipulate
            </button>
        </div>
    );
};

export default ArrayVisualizer;
