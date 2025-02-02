import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "codemirror/theme/oceanic-next.css";
import "../styles/CodeWindow.css";
import { useRef } from "react";

interface CodeWindowProps {
    parseCode: (code: string) => void;
}

export default function CodeWindow({ parseCode }: CodeWindowProps) {
    const editorRef = useRef<any>(null);

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
                onClick={() => parseCode(editorRef.current?.getValue() || "")} // get code on button click
            >
                Compile
            </button>
        </div>
    );
}
