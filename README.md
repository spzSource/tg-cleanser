# tg-cleanser

## Configuration

1. Install python 3.8 or above
2. Run `pip install -r requirements.txt`
3. Generate `TELEGRAM_API_ID` and `TELEGRAM_API_SECRET` using the following instruction: https://core.telegram.org/api/obtaining_api_id and then save these values into ENV variables.
4. Add `TELEGRAM_SESSION` env variable. It can contain any value **or** session string, like described here https://docs.pyrogram.org/topics/storage-engines#session-strings . Second option is useful when deploying the script to heroku.

## Commands:
1. List all available groups/supergroups:
```shell
python main.py list
```
2. Removed 1 day old messages from selected groups:
```shell
python main.py remove -g 1 2 3
```
        