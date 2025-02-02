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
  isProcessing: boolean;
  setIsProcessing: (isProcessing: boolean) => void;
}

export default function CodeWindow({ parseCode, highlightedLine, code, isProcessing, setIsProcessing }: CodeWindowProps) {
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
      if (highlightedLine !== null && highlightedLine <= currentLineCount) {
        if (prevHighlightRef.current !== null && prevHighlightRef.current <= currentLineCount) {
          editor.removeLineClass(prevHighlightRef.current - 1, "background", "highlight-line");
        }
        if (isProcessing) {
          editor.addLineClass(highlightedLine - 1, "background", "highlight-line");
          prevHighlightRef.current = highlightedLine;
        }
      }
    }
  }, [highlightedLine, isProcessing]);

  useEffect(() => {
    if (editorRef.current && !isProcessing) {
      const editor = editorRef.current;
      const totalLines = editor.lineCount();
      for (let i = 0; i < totalLines; i++) {
        editor.removeLineClass(i, "background", "highlight-line");
      }
      prevHighlightRef.current = null;
    }
  }, [isProcessing]);

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.setValue(code);
    }
  }, [code]);

  return (
    <div className="CodeWindow">
      <CodeMirror
        value={code}
        options={options}
        editorDidMount={(editor) => (editorRef.current = editor)}
      />
      <button 
        className="vButton" 
        onClick={() => {
          parseCode(editorRef.current?.getValue() || "");
          setIsProcessing(false)
        }}
      >
        Compile
      </button>
    </div>
  );
}