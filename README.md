# Automated Bitcoin Trading Tool
### Link to project visualization dashboard: https://rebrand.ly/threepeaksai

This project is an automated trading system designed to analyze various factors that impact the Bitcoin price and make trading decisions based on the calculated probabilities. The system incorporates nine different factors or modules, each returning two values (bullish and bearish), which are then used in a Multi-Criteria Decision Analysis (MCDA) system to calculate the weighted score for the price going up and down. Based on the normalized scores, the system determines when to open a long or short position trade or when to close an open position.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
git clone https://github.com/williamnordberg/adam_trader.git
2. Install the required Python packages:
pip install -r requirements/requirements.txt
3. Make the directory and files listed in gitignore in your system. 
4. Adjust Placeholder Files and Directories:
Look for files and directories starting with placeholder_.
Rename each one to remove the placeholder_ prefix (e.g., rename placeholder_log to log).
Adjust the contents of each file according to your environment and preferences. For example, for placeholder_config.ini, fill in your API keys and other relevant details.
Configure API Keys and Other Settings:

## Usage

1. Configure the `config.py` file with your API keys, trading parameters, and other settings.

2. Connect your exchange or wallet with API (give just trading permission)
 
3. Run the main script:
 python3 main.py

4. Monitor the logs to view the trading decisions made by the system and the resulting profit or loss after each trade.


## Contributing

1. Fork the repository on GitHub.
2. Create a branch for your changes.
3. Commit your changes and push to your fork.
4. Create a pull request to the original repository.

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for more information.




