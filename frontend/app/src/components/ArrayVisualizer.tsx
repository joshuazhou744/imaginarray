import { useState, useRef  } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Manipulation } from '../utils/manipulateTypes';
import { arrayItemVariants } from '../animations/arrayItemVariants';
import Loader from './Loader';
import "../styles/ArrayVisualizer.css";
import { v4 as uuidv4 } from 'uuid';
import Variables from './Variables';

interface Item<T> {
  id: string;
  value: T;
}

interface ArrayVisualizerProps<T> {
  initialArray: T[];
  manipulations: Manipulation<T>[];
  lineNums: number[]; 
  setHighlightedLine: (line: number | null) => void;
  isProcessing: boolean;
  setIsProcessing: (isProcessing: boolean) => void;
}

const ArrayVisualizer = <T,>({ initialArray, manipulations, lineNums, setHighlightedLine, isProcessing, setIsProcessing }: ArrayVisualizerProps<T>): JSX.Element => {

  const initialItems: Item<T>[] = initialArray.map((val) => ({
    id: uuidv4(),
    value: val,
  }));

  const [displayItems, setDisplayItems] = useState<Item<T>[]>(initialItems);
  const currentItemsRef = useRef<Item<T>[]>(initialItems);
  const processingRef = useRef(false);
  const [reverseTrigger, setReverseTrigger] = useState(false);
  const [swappedIDs, setSwappedIDs] = useState<[string, string] | null>(null);
  const [replacedID, setReplacedID] = useState<string | null>(null);
  const [removedID, setRemovedID] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const [variables, setVariables] = useState<{ [key: string]: unknown }>({});

  const dynamicSize = Math.max(20, 80 - displayItems.length * 5);

  const updateItems = (newArray: Item<T>[]) => {
    setDisplayItems(newArray);
    currentItemsRef.current = newArray;
  };

  const processManipulations = () => {
    if (processingRef.current) return;
    processingRef.current = true;
    setIsProcessing(true);

    let currentIndex = 0;
    let delay = 400;

    const processNext = () => {
      if (currentIndex < manipulations.length) {
        const instruction = manipulations[currentIndex];
        const lineNum = lineNums[currentIndex];
        delay = 400;

        setHighlightedLine(lineNum);

        if (instruction.type === 'append') {
          const newItem: Item<T> = {
            id: uuidv4(),
            value: instruction.value,
          };
          const newItems = [...currentItemsRef.current, newItem];
          updateItems(newItems);
        } else if (instruction.type === 'pop') {
          const newItems = [...currentItemsRef.current];
          newItems.pop();
          updateItems(newItems);
        } else if (instruction.type === 'reverse') {
          const newItems = [...currentItemsRef.current].reverse();
          updateItems(newItems);
          setReverseTrigger(prev => !prev);
          delay = 1000;
        } else if (instruction.type === 'swap') {
          const [i, j] = instruction.indices;
          if (
            i < 0 ||
            j < 0 ||
            i >= currentItemsRef.current.length ||
            j >= currentItemsRef.current.length ||
            i === j
          ) {
            alert('Invalid swap indices. Please provide two different indices within the array bounds.');
          } else {
            const id1 = currentItemsRef.current[i].id;
            const id2 = currentItemsRef.current[j].id;
            setSwappedIDs([id1, id2]);
            setTimeout(() => {
              const newItems = [...currentItemsRef.current];
              [newItems[i], newItems[j]] = [newItems[j], newItems[i]];
              updateItems(newItems);
              setTimeout(() => {
                setSwappedIDs(null);
              }, 600);
            }, 100);
            delay = 1000;
          }
        } else if (instruction.type === 'replace') {
          const { index, value } = instruction;
          if (index < 0 || index >= currentItemsRef.current.length) {
            alert('Invalid replace index. Please provide an index within the array bounds.');
          } else {
            const itemId = currentItemsRef.current[index].id;
            setReplacedID(itemId);
            const newItems = [...currentItemsRef.current];
            newItems[index] = { ...newItems[index], value };
            updateItems(newItems);
            delay = 600;
            setTimeout(() => {
              setReplacedID(null);
            }, 500);
          }
        } else if (instruction.type === 'remove') {
          const value = instruction.value;
          const index = currentItemsRef.current.findIndex(item => item.value === value);
          if (index === -1) {
            alert('Value not found in array. Please provide a valid value to remove.');
          } else {
            const itemId = currentItemsRef.current[index].id;
            setRemovedID(itemId);
            delay = 2000;
            setTimeout(() => {
              const newItems = currentItemsRef.current.filter(item => item.id !== itemId);
              updateItems(newItems);
              setRemovedID(null);
            }, 700);
          }
        } else if (instruction.type === 'delete') {
          const index = instruction.index;
          if (index < 0 || index >= currentItemsRef.current.length) {
            alert('Invalid remove index. Please provide an index within the array bounds.');
          } else {
            const itemId = currentItemsRef.current[index].id;
            setRemovedID(itemId);
            delay = 2000;
            setTimeout(() => {
              const newItems = currentItemsRef.current.filter(item => item.id !== itemId);
              updateItems(newItems);
              setRemovedID(null);
            }, 700);
          }
        } else if (instruction.type === 'variable') {
          const { name, value } = instruction;;
          setVariables(prev => ({ ...prev, [name]: value }));
        } else if (instruction.type === 'clear') {
          updateItems([]);
        }
        currentIndex += 1;
        setTimeout(processNext, delay);
      } else {
        processingRef.current = false;
        setIsProcessing(false);
        setHighlightedLine(null); // remove highlight when done
        setHasRun(true);
      }
    };
    processNext();
  };

  return (
    <div className='container'>
      <div className='perspective'>
        <motion.div
          animate={{ rotateY: reverseTrigger ? 360 : 0 }}
          transition={{ duration: 0.9 }}
          className="flip-container"
        >
          <AnimatePresence>
            {displayItems.map((item) => {
              const isSwapped = swappedIDs !== null && (swappedIDs[0] === item.id || swappedIDs[1] === item.id);
              const isReplaced = replacedID === item.id;
              const isRemoved = removedID === item.id;
              const animateProp = isRemoved
                ? { opacity: 1, y: 0, scale: [1, 0.8, 0] }
                : isSwapped || isReplaced
                  ? { opacity: 1, y: 0, scale: [1, 1.2, 1] }
                  : "animate";
              return (
                <motion.div
                  key={item.id}
                  layout
                  variants={arrayItemVariants}
                  initial="initial"
                  exit="exit"
                  animate={animateProp}
                  transition={{ duration: 0.5 }}
                  className="array-item"
                  style={{
                    width: `${dynamicSize}px`,
                    height: `${dynamicSize}px`
                  }}
                >
                  {JSON.stringify(item.value)}
                </motion.div>
              )
            })}
          </AnimatePresence>
        </motion.div>
      </div>
      <div className="variables">
        <Variables variables={variables}/>
      </div>
      <div className="bottom-group">
        {isProcessing && <Loader />}
        {displayItems.length > 0 && !hasRun && (
          <button onClick={processManipulations} className='manipulate-button'>
            Visualize
          </button>
        )}
      </div>
    </div>
  );
};

export default ArrayVisualizer;
