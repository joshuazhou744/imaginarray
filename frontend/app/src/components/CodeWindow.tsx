import { Controlled as CodeMirror } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "codemirror/theme/oceanic-next.css";
import "../styles/CodeWindow.css";
import { FC } from "react";

interface CodeWindowProps {
  parseCode: (code: string) => void;
  highlightedLine: number | null;
  code: string;
}

const CodeWindow: FC<CodeWindowProps> = ({ parseCode, highlightedLine, code }) => {
  const options = {
    lineNumbers: true,
    lineWrapping: true,
    mode: "python",
    theme: "oceanic-next",
  };

  return (
    <div className="CodeWindow">
      <CodeMirror
        value={code}
        options={options}
        onBeforeChange={(editor, data, value) => {
          // You can handle changes here if you want a two-way binding.
        }}
      />
      <button
        className="vButton"
        onClick={() => parseCode(code)}
      >
        Compile
      </button>
    </div>
  );
};

export default CodeWindow;
