// ArrayVisualizer.tsx
import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Manipulation } from '../utils/manipulateTypes';
import { arrayItemVariants } from '../animations/arrayItemVariants';
import Loader from './Loader';
import "../styles/ArrayVisualizer.css";


interface ArrayVisualizerProps<T> {
  initialArray: T[];
  manipulations: Manipulation<T>[];
}

const ArrayVisualizer = <T,>({ initialArray, manipulations }: ArrayVisualizerProps<T>): JSX.Element => {
    const [displayArray, setDisplayArray] = useState<T[]>(initialArray);
    const currentArrayRef = useRef<T[]>(initialArray);
    const processingRef = useRef(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [reverseTrigger, setReverseTrigger] = useState(false);
    const [swappedIndices, setSwappedIndices] = useState<[number, number] | null>(null);
    const [replacedIndex, setReplacedIndex] = useState<number | null>(null);

    const updateArray = (newArray: T[]) => {
      setDisplayArray(newArray);
      currentArrayRef.current = newArray;
    };

    const processManipulations = () => {
        if (processingRef.current) return;
        processingRef.current = true;
        setIsProcessing(true);
    
        let currentIndex = 0;
    
        const processNext = () => {
          if (currentIndex < manipulations.length) {
            const instruction = manipulations[currentIndex];
            let delay = 400;

            if (instruction.type === 'append') {
              const newArray = [...currentArrayRef.current, instruction.value];
              updateArray(newArray);
            } else if (instruction.type === 'pop') {
              const newArray = [...currentArrayRef.current];
              newArray.pop();
              updateArray(newArray);
            } else if (instruction.type === 'reverse') {
                const newArray = [...currentArrayRef.current].reverse();
                updateArray(newArray);
                setReverseTrigger(prev => !prev);
            } else if (instruction.type === 'swap') {
                const [i, j] = instruction.indices;
                if (
                  i < 0 ||
                  j < 0 ||
                  i >= currentArrayRef.current.length ||
                  j >= currentArrayRef.current.length ||
                  i === j
                ) {
                  alert('Invalid swap indices. Please provide two different indices within the array bounds.');
                  console.log('Invalid swap indices:', instruction.indices);
                } else {
                  setSwappedIndices(instruction.indices);
                  setTimeout(() => {
                    const newArray = [...currentArrayRef.current];
                    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
                    updateArray(newArray);
                    setTimeout(() => {
                        setSwappedIndices(null);
                    }, 600);
                  }, 100);
                  delay = 1000;
                }
            } else if (instruction.type === 'replace') {
                const { index, value } = instruction;
                if (index < 0 || index >= currentArrayRef.current.length) {
                    alert('Invalid replace index. Please provide an index within the array bounds.');
                    console.log('Invalid replace index:', index);
                } else {
                  setReplacedIndex(index);
                  const newArray = [...currentArrayRef.current];
                  newArray[index] = value;
                  updateArray(newArray);
                  delay = 600;
                  setTimeout(() => {
                  setReplacedIndex(null);
                  }, 500);
                }
            } else if (instruction.type === 'clear') {
              updateArray([]);
            }
            currentIndex += 1;
            setTimeout(processNext, delay);
          } else {
            processingRef.current = false;
            setIsProcessing(false);
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
                        {displayArray.map((item, index) => {
                            const isSwapped = swappedIndices !== null && (swappedIndices[0] === index || swappedIndices[1] === index);
                            const isReplaced = replacedIndex === index;
                            return (
                                <motion.div
                                    key={index}
                                    layout
                                    variants={arrayItemVariants}
                                    initial="initial"
                                    exit="exit"
                                    animate={
                                    isSwapped || isReplaced 
                                        ? { opacity: 1, y: 0, scale: [1, 1.2, 1] } 
                                        : "animate"}
                                    transition={{ duration: 0.5 }}
                                    className="array-item"
                                    >
                                    {JSON.stringify(item)}
                                </motion.div>
                            )
                        })}
                    </AnimatePresence>
                </motion.div>
            </div>
            <div className="bottom-group">
              {isProcessing && <Loader />}
              <button onClick={processManipulations} className='manipulate-button vButton'>
                  Visualize
              </button>
            </div>
        </div>
    );
};

export default ArrayVisualizer;