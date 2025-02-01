import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "../styles/CodeWindow.css";
import "codemirror/theme/ayu-dark.css";


export default function CodeWindow() {
    const options = {
        lineNumbers: true,
        lineWrapping: true,
        mode: "python",
        theme: "ayu-dark",
    }
    
    return (
        <div className="CodeWindow">
            <CodeMirror
              options={options}
            />
            <button className="vButton">
                Visualize
            </button>

        </div>
    );
}