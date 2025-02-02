import { UnControlled as CodeMirror } from "react-codemirror2";
import { Editor } from 'codemirror';
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "codemirror/theme/oceanic-next.css";
import "../styles/CodeWindow.css";
import { useRef, useEffect } from "react";

interface CodeWindowProps {
  parseCode: (code: string) => void;
  highlightedLine: number | null;
  code: string;
  setCode: React.Dispatch<React.SetStateAction<string>>;
}

export default function CodeWindow({ parseCode, highlightedLine, code }: CodeWindowProps) {
  const editorRef = useRef<Editor | null>(null);
  const prevHighlightRef = useRef<number | null>(null);

  const options = {
    lineNumbers: true,
    lineWrapping: true,
    mode: "python",
    theme: "oceanic-next",
  };

  useEffect(() => {
    if (editorRef.current) {
      const editor = editorRef.current;
      const currentLineCount = editor.lineCount();

      if (
        prevHighlightRef.current !== null &&
        prevHighlightRef.current <= currentLineCount
      ) {
        editor.removeLineClass(prevHighlightRef.current - 1, "background", "highlight-line");
      }

      if (highlightedLine !== null && highlightedLine <= currentLineCount) {
        console.log("ADDED")
        editor.addLineClass(highlightedLine - 1, "background", "highlight-line");
      }

      prevHighlightRef.current = highlightedLine;
    }
  }, [highlightedLine]);

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.setValue(code);
      console.log(editorRef.current.getValue())
    }
  }, [code])

  return (
    <div className="CodeWindow">
      <CodeMirror
        options={options}
        editorDidMount={(editor) => (editorRef.current = editor)}
      />
      <button 
        className="vButton" 
        onClick={() => parseCode(editorRef.current?.getValue() || "")}
      >
        Compile
      </button>
    </div>
  );
}