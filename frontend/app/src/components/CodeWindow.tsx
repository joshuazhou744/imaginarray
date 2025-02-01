import { UnControlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";


export default function CodeWindow() {
    const options = {
        lineNumbers: true,
        mode: "python",
    }

    return (
      <CodeMirror
        options={options}
      />
    );
}