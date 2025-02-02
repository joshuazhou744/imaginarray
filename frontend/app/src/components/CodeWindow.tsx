// CodeWindow.tsx

import { UnControlled as CodeMirror } from "react-codemirror2";
import { Editor } from 'codemirror';
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "codemirror/theme/oceanic-next.css";
import "../styles/CodeWindow.css";
import { useRef } from "react";

interface CodeWindowProps {
    parseCode: (code: string) => void;
}

export default function CodeWindow({ parseCode }: CodeWindowProps) {
    const editorRef = useRef<Editor | null>(null);

    const options = {
        lineNumbers: true,
        lineWrapping: true,
        mode: "python",
        theme: "oceanic-next",
    };

    return (
        <div className="CodeWindow">
            <CodeMirror
                options={options}
                editorDidMount={(editor) => (editorRef.current = editor)} // ref to editor
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
