import praw
import configparser
import db
import logging
import telegram
import time
import raven
import os
import subprocess
import sys

# Init the config reader
config = configparser.ConfigParser()
config.read("config.ini")

logging.getLogger().setLevel(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# noinspection PyUnreachableCode
if __debug__:
    version = "Dev"
    commit_msg = "_in sviluppo_"
else:
    # Find the latest git tag
    old_wd = os.getcwd()
    try:
        os.chdir(os.path.dirname(__file__))
        version = str(subprocess.check_output(["git", "describe", "--tags"]), encoding="utf8").strip()
        commit_msg = str(subprocess.check_output(["git", "log", "-1", "--pretty=%B"]), encoding="utf8").strip()
    except Exception:
        version = "❓"
    finally:
        os.chdir(old_wd)

sentry = raven.Client(config["Sentry"]["token"],
                      release=version,
                      install_logger_hook=False,
                      hook_libraries=[])


def process():
    logger.info("Retrieving parsed posts...")
    session = db.Session()
    results = session.query(db.ParsedRedditPost).all()
    parsed_post_ids = [x.id for x in results]
    session.close()
    logger.info("Posts retrieved successfully.")

    logger.info("Logging in to reddit...")
    reddit = praw.Reddit(client_id=config["reddit"]["client_id"],
                         client_secret=config["reddit"]["client_secret"],
                         password=config["reddit"]["password"],
                         user_agent='Royal-Bot/4.1',
                         username=config["reddit"]["username"])
    logger.info(f"Login as {reddit.user.me()} successful!")

    logger.info(f"Logging in to Telegram...")
    telegram_bot = telegram.Bot(config["Telegram"]["bot_token"])
    logger.info(f"Login successful.")

    r_royalgames = reddit.subreddit("royalgames")
    for submission in r_royalgames.stream.submissions():
        try:
            if submission.id not in parsed_post_ids:
                logger.info(f"New post found: {submission.id}")
                logger.debug(f"Creating new db session...")
                session = db.Session()
                new_post = db.ParsedRedditPost(id=submission.id)
                session.add(new_post)
                logger.debug(f"Committing...")
                session.commit()
                session.close()
                logger.debug("Sending Telegram notification...")
                while True:
                    try:
                        telegram_bot.send_message(config["Telegram"]["main_group"],
                                                  f'Nuovo post su r/RoyalGames:\n'
                                                  f'<a href="https://reddit.com{submission.permalink}">{submission.title}</a>\n'
                                                  f'da u/{submission.author}',
                                                  parse_mode="HTML", disable_notification=True)
                    except telegram.error.TimedOut:
                        time.sleep(1)
                    else:
                        break
        except Exception:
            sentry.captureException(exc_info=sys.exc_info())
