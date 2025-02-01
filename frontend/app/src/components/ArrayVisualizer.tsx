// ArrayVisualizer.tsx
import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Manipulation } from '../utils/manipulateTypes';
import { arrayItemVariants } from '../animations/arrayItemVariants';
import "../styles/ArrayVisualizer.css";


interface ArrayVisualizerProps<T> {
  initialArray: T[];
  manipulations: Manipulation<T>[];
}

const ArrayVisualizer = <T,>({ initialArray, manipulations }: ArrayVisualizerProps<T>): JSX.Element => {
    const [displayArray, setDisplayArray] = useState<T[]>(initialArray);
    const processingRef = useRef(false);
    const [reverseTrigger, setReverseTrigger] = useState(false);

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
            } else if (instruction.type === 'reverse') {
                setDisplayArray(
                    prevArray => {
                        return [...prevArray].reverse()
                    }
                );
                setReverseTrigger(prev => !prev);
            }
            currentIndex += 1;
            setTimeout(processNext, 400);
          } else {
            processingRef.current = false;
          }
        };
    
        processNext();
      };

    return (
        <div className='container'>
            <div className='perspective'>
                <motion.div
                    animate={{
                        rotateY: reverseTrigger ? 360 : 0
                    }}
                    transition={{ duration: 0.6 }}
                    className="flip-container"
                >
                    <AnimatePresence>
                        {displayArray.map((item, index) => (
                            <motion.div
                            key={index}
                            layout
                            variants={arrayItemVariants}
                            initial="initial"
                            animate="animate"
                            exit="exit"
                            transition={{ duration: 0.5 }}
                            className="array-item"
                            >
                            {JSON.stringify(item)}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </motion.div>
            </div>
            <button onClick={processManipulations} className='manipulate-button'>
                manipulate
            </button>
        </div>
    );
};

export default ArrayVisualizer;
