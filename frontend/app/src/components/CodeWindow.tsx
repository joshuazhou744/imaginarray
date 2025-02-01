import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "../styles/CodeWindow.css";


export default function CodeWindow() {
    const options = {
        lineNumbers: true,
        mode: "python",
    }

    return (
        <div className="CodeWindow">
            <CodeMirror
              options={options}
            />
            <button>
                Visualize
            </button>

        </div>
    );
}