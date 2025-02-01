import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "../styles/CodeWindow.css";
import "codemirror/theme/oceanic-next.css";
import { useState } from "react";

interface CodeWindowProps {
    parseCode: (code: string) => void;
}

export default function CodeWindow({ parseCode }: CodeWindowProps) {
    const [code, setCode] = useState("");

    const options = {
        lineNumbers: true,
        lineWrapping: true,
        mode: "python",
        theme: "oceanic-next"
        
    }
    
    return (
        <div className="CodeWindow">
            <CodeMirror
              options={options}
              value={code}
              onChange={(_editor, _data, value) => setCode(value)}
            />
            <button className="vButton" onClick={() => parseCode(code)}>
                Compile
            </button>

        </div>
    );
}
