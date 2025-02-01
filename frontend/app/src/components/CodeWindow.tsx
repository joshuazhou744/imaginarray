import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "../styles/CodeWindow.css";
import "codemirror/theme/oceanic-next.css";
import axios from 'axios';
import { useState } from "react";



export default function CodeWindow() {
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
                Visualize
            </button>

        </div>
    );
}

const parseCode = async(code: string) => {
    const lines = code.split("\n");
    console.log(lines)
    const response = await axios.post('http://172.30.145.175:4000/submit_code', {
       code: lines 
    })
}