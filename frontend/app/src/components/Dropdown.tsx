import React from 'react';

interface DropdownProps {
  setCode: React.Dispatch<React.SetStateAction<string>>; // Set the type for setCode function
}

const Dropdown: React.FC<DropdownProps> = ({ setCode }) => {
  const algo = ['Bubble Sort', 'Insertion Sort', 'Selection Sort', 'Quick Sort'];

  const algoCode: { [key: string]: string } = {
    'Bubble Sort': `# Bubble Sort Algorithm in Python\n\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\narr = [64, 34, 25, 12, 22, 11, 90]\nbubble_sort(arr)`,
    'Insertion Sort': `# Insertion Sort Algorithm in Python\n\ndef insertion_sort(arr):\n    for i in range(1, len(arr)):\n        key = arr[i]\n        j = i-1\n        while j >= 0 and key < arr[j]:\n            arr[j+1] = arr[j]\n            j -= 1\n        arr[j+1] = key\n    return arr\n\narr = [64, 34, 25, 12, 22, 11, 90]\ninsertion_sort(arr)`,
    'Selection Sort': `# Selection Sort Algorithm in Python\n\ndef selection_sort(arr):\n    for i in range(len(arr)): \n        min_idx = i\n        for j in range(i+1, len(arr)):\n            if arr[j] < arr[min_idx]:\n                min_idx = j\n        arr[i], arr[min_idx] = arr[min_idx], arr[i]\n    return arr\n\narr = [64, 34, 25, 12, 22, 11, 90]\nselection_sort(arr)`,
    'Quick Sort': `# Quick Sort Algorithm in Python\n\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\narr = [64, 34, 25, 12, 22, 11, 90]\nquick_sort(arr)`
  };

  // Update the code based on the selected algorithm
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedAlgo = event.target.value;
    setCode(algoCode[selectedAlgo] || ''); // Update code state with selected algorithm's code
  };

  return (
    <div>
      <label htmlFor="algorithm-dropdown">Select an Algorithm:</label>
      <select id="algorithm-dropdown" onChange={handleChange}>
        <option value="">--Choose an algorithm--</option>
        {algo.map((algorithm, index) => (
          <option key={index} value={algorithm}>
            {algorithm}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;
