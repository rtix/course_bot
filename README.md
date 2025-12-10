# Course Management Bot

A Telegram bot for managing academic courses. A self-hosted solution for instructors providing extensive functionality:

- Create individual courses for different subjects
- Register users
- Send notifications to students via Telegram or email
- Configure course enrollment periods
- Create and manage assignments
- Track attendance and grades with spreadsheet integration

## Usage

1. Register your telegram bot via `@BotFather`
2. Fill your `settings.cfg`
3. Install `pyYandexTranslateAPI`
4. `python start.py`
5. `/start` in your telegram bot

## Dependencies
```
pyYandexTranslateAPI 4.*
```

## Configuration
Configure your app with `settings.cfg`

### Teacher's telegram username 

```
[default]
username
```
### Telegram bot token

```
[bot]
token
```
### Teacher's email credentials

```
[mail]
email
password
```
### SMTP and Proxy, if needed

```
[optional]
smtp_host
proxy
```
