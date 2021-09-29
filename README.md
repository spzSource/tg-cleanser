# tg-cleanser

## How to use

1. Install python 3.8 or above
2. Run `pip install -r requirements.txt`
3. Generate `TELEGRAM_API_ID` and `TELEGRAM_API_SECRET` using the following instruction: https://core.telegram.org/api/obtaining_api_id and then save these values into ENV variables.
4. Run python3 `./main.py`
5. Enjoy

## How to configure:
```python
async for group in telega.groups(group_ids=[ ... ])
```

 - where group_ids is a list of groups that have to be cleansed
        