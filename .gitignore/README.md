# Automated Bitcoin Trading System

This project is an automated trading system designed to analyze various factors that impact the Bitcoin price and make trading decisions based on the calculated probabilities. The system incorporates nine different factors or modules, each returning two values (bullish and bearish), which are then used in a Multi-Criteria Decision Analysis (MCDA) system to calculate the weighted score for the price going up and down. Based on the normalized scores, the system determines when to open a long or short position trade or when to close an open position.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/automated-bitcoin-trading.git
2. Install the required Python packages:
pip install -r requirements.txt


## Usage

1. Configure the `config.py` file with your API keys, trading parameters, and other settings.

2. Run the main script:
 python main.py

3. Monitor the logs to view the trading decisions made by the system and the resulting profit or loss after each trade.

## Contributing

1. Fork the repository on GitHub.
2. Create a branch for your changes.
3. Commit your changes and push to your fork.
4. Create a pull request to the original repository.

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for more information.




