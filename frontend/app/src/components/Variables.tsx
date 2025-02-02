// Variables.tsx
import React from "react";
import "../styles/Variables.css";

interface VariablesProps {
  variables: { [key: string]: unknown };
}

const Variables: React.FC<VariablesProps> = ({ variables }) => {
  const keys = Object.keys(variables);

  return (
    <div className="variables-container">
      <h3>Tracked Variables</h3>
      {keys.length === 0 ? (
        <p>No variables tracked.</p>
      ) : (
        <ul className="variables-list">
          {keys.map((key) => (
            <li key={key} className="variable-item">
              <span className="variable-name">{key}:</span>{" "}
              <span className="variable-value">{JSON.stringify(variables[key])}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Variables;
