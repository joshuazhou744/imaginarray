import React, { Component } from 'react';

// Typing the component state and props
type DropdownState = {
  isOpen: boolean;
  haveText: string;
}

const algo = ['Bubble Sort', 'Insertion Sort', 'Selection Sort', 'Quick Sort'];

class Dropdown extends Component<{}, DropdownState> {
  constructor(props: {}) {
    super(props);
    this.state = {
      isOpen: false,
      haveText: "",
    };
  }

  render() {
    const { isOpen, haveText } = this.state;

    return (
      <div
        className={isOpen ? "dropdown active" : "dropdown"}
        onClick={this.handleClick}>
        <div className="dropdown__text">
          {!haveText ? "Select Algorithm" : haveText}
        </div>
        {this.itemList(algo)}
      </div>
    );
  }

  handleClick = () => {
    this.setState((prevState) => ({
      isOpen: !prevState.isOpen,
    }));
  }

  handleText = (ev: React.MouseEvent<HTMLDivElement>) => {
    this.setState({
      haveText: (ev.currentTarget as HTMLElement).textContent || "",
    });
  }

  itemList = (props: string[]) => {
    const list = props.map((item) => (
      <div
        onClick={this.handleText}
        className="dropdown__item"
        key={item}>
        {item}
      </div>
    ));

    return (
      <div className="dropdown__items">{list}</div>
    );
  }
}

// Default export of the Dropdown component
export default Dropdown;
