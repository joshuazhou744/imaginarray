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
        <div className="variables-items">
          {keys.map((key) => (
            <div key={key} className="variable-item">
              <span className="variable-name">{key}:</span>{" "}
              <span className="variable-value">{JSON.stringify(variables[key])}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Variables;
