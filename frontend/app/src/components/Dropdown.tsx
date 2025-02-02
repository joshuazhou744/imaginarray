import "../styles/Dropdown.css";

interface DropdownProps {
  handlePreset: (preset: string) => void;
}

const Dropdown: React.FC<DropdownProps> = ({ handlePreset }) => {
  const options = ["Bubble Sort", "Insertion Sort", "Selection Sort", "Quick Sort", "Reverse Bubble Sort"];

  const algoCode: { [key: string]: string } = {
    "Bubble Sort": `# Bubble Sort Algorithm in Python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Fill in the array with your own values
arr = []
bubble_sort(arr)`,
    "Insertion Sort": `# Insertion Sort Algorithm in Python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

# Fill in the array with your own values
arr = []
insertion_sort(arr)`,
    "Selection Sort": `# Selection Sort Algorithm in Python
def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
# Fill in the array with your own values
arr = []
selection_sort(arr)`,
    "Quick Sort": `# Quick Sort Algorithm in Python
def partition(arr, low, high):
    
    # Choose the pivot
    pivot = arr[high]
    
    # Index of smaller element and indicates 
    # the right position of pivot found so far
    i = low - 1
    
    # Traverse arr[low..high] and move all smaller
    # elements to the left side. Elements from low to 
    # i are smaller after every iteration
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            swap(arr, i, j)
    
    # Move pivot after smaller elements and
    # return its position
    swap(arr, i + 1, high)
    return i + 1

# Swap function
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

# The QuickSort function implementation
def quickSort(arr, low, high):
    if low < high:
        
        # pi is the partition return index of pivot
        pi = partition(arr, low, high)
        
        # Recursion calls for smaller elements
        # and greater or equals elements
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)
# Fill in the array with your own values
arr = []
quickSort(arr, 0, len(arr)-1)`,
"Reverse Bubble Sort": `# Reverse Bubble Sort Algorithm in Python
def reverse_bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] < arr[j + 1]:  # Swap if the current element is smaller than the next
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # Optimization: stop if no swaps occurred in the last pass
    arr.reverse()

# Fill in the array with your own values
arr = []
reverse_bubble_sort(arr)`
  };

  const handleSelect = (algoName: string) => {
    handlePreset(algoCode[algoName] || "");
  };

  return (
    <div className="paste-button">
      <button className="button">Preset Algorithms ▼</button>
      <div className="dropdown-content">
        {options.map((option, index) => (
          <a key={index} onClick={() => handleSelect(option)} href="#">
            {option}
          </a>
        ))}
      </div>
    </div>
  );
};

export default Dropdown;
