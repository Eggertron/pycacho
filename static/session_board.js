'use strict';

class Timer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { seconds: 0 };
  }

  tick() {
    fetch("http://localhost:5000/session/2").then(res => res.json()).then(
      (result) => {
        this.setState({
          scores: result
        });
      },
      // Note: it's important to handle errors here
      // instead of a catch() block so that we don't swallow
      // exceptions from actual bugs in components.
      (error) => {
        this.setState({
          scores: error
        });
      }
    )
  }

  componentDidMount() {
    this.interval = setInterval(() => this.tick(), 1000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    return (
      <div>
        Scores: {this.state.scores}
      </div>
    );
  }
}

ReactDOM.render(
  <Timer />,
  document.getElementById('session_board')
);