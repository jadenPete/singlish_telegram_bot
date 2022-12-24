# Singlish Translation Bot

Automatically translates messages on [Telegram](https://telegram.org/) containing Singlish
(Singaporean English) to American English and defines Singlish terminology.

## How It Works

`scraper.py` parses an [online Singlish dictionary](http://www.mysmu.edu/faculty/jacklee),
downloading over 1,200 Singlish terms and their potentially multiple definitions into the SQLite
database `singlish_telegram_bot.db`.

`app.py` executes the bot, which assembles a prefix tree to match those terms as detected in
sentences and send responses containing their definitions.

## Execution

```
$ echo '{"token": "<TELEGRAM TOKEN>"}' > config_private.json

$ ./create_schema.py
$ ./scraper.py
$ ./app.py
```
