# Cointracker

A simple Telegram bot made with pure python3 for tracking your precious cryptocurrencies.

## Installation

### Install dependencies
```bash
pip install .
```

### Configure TelegramBot API and CoinmarketcapPRO API

*__User way__*. Specify env variables
```bash
export TELEGRAM_BOT_API_KEY=<yours_bot_api_key>
export COINMARKETCAP_API_KEY=<yours_cmc_api_key>
```
***OR***

*__Developer way__*. Edit parameters via default config inside the project
```bash
cp cointracker/config.yml cointracker/config-local.yml
nano cointracker/config-local.yml
```

***OR***

*__Production way__*. Create /etc/cointracker/config.yml with ony overriding values.
```bash
cp -R cointracker/config.yml /etc/cointracker/config.yml 
nano /etc/cointracker/config.yml
```
    
## Run the bot
```bash
python cointracker/main.py
```

## Run the test
```bash
pytest
```