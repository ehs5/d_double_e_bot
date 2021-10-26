import configparser
import random
import time

import praw

search_name1 = " d double"
search_name2 = "D Double"
bot_username = "d_double_e_bot"
subreddit_names = "grime+ukdrill+ukhiphopheads"
replied_comments_filename = "d_double_e_bot_replied_comments.txt"
replied_submissions_filename = "d_double_e_bot_replied_submissions.txt"
log_filename = "d_double_e_bot_log.txt"

phrases = [
    "Oooahh ooooaaah",
    "Buda-bup-bup",
    "Supadupe oooaah oooaah",
    "Diirtty-tyyy",
    "That's mmuuee muuue",
    "Head get mangled then dangled, to the side just like I wear my Kangol",
    "Head get mangled then dangled",
    "Bluku blukuuu",
    "That's very original, never heard that from another individual",
    "Jackuuuum",
    "Oh my wooord"
    # "This one's a Percy Ingle... Jackuum!"
]


def get_config_object(configObjectName):
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    config_object = config[configObjectName]
    return config_object


def add_to_txt_file(fileName, string):
    file = open(fileName, 'a')
    file.write(string)
    file.close()


def get_txt_file_as_list(fileName):
    txtFileAsList = open(fileName).read().splitlines()
    return txtFileAsList


def create_log_string_comment(comment, randomPhrase):
    str1 = f"Man like u/{comment.author.name} in r/{comment.subreddit.display_name} commented:"
    str2 = f"\n{comment.body}"
    str3 = f"\nComment ID: {comment.id}"
    str4 = f"\nReplied with: {randomPhrase}"
    str5 = f"\n------------------------------\n"
    return str1 + str2 + str3 + str4 + str5


def create_log_string_submission(submission, randomPhrase):
    str1 = f"Man like u/{submission.author.name} in r/{submission.subreddit.display_name} made a submission:"
    str2 = f"\n{submission.title}"
    str3 = f"\nSubmission ID: {submission.id}"
    str4 = f"\nReplied with: {randomPhrase}"
    str5 = f"\n------------------------------\n"
    return str1 + str2 + str3 + str4 + str5


def reply_to_comment(comment):
    randomPhrase = random.choice(phrases)
    comment.reply(randomPhrase)
    add_to_txt_file(replied_comments_filename, f"{comment.id}\n")
    logEntry = create_log_string_comment(comment, randomPhrase)
    add_to_txt_file(log_filename, logEntry)
    print(logEntry)


def reply_to_submission(submission):
    randomPhrase = random.choice(phrases)
    submission.reply(randomPhrase)
    add_to_txt_file(replied_submissions_filename, f"{submission.id}\n")
    logEntry = create_log_string_submission(submission, randomPhrase)
    add_to_txt_file(log_filename, logEntry)
    print(logEntry)


def process_comment(comment):
    if comment.author.name != bot_username:
        if comment.id not in get_txt_file_as_list(replied_comments_filename):
            body = comment.body
            normalized_body = body.lower()
            if (search_name1 in normalized_body) or (search_name2 in body):
                reply_to_comment(comment)


def process_submission(submission):
    if submission.author.name != bot_username:
        if submission.id not in get_txt_file_as_list(replied_submissions_filename):
            title = submission.title
            normalized_title = title.lower()
            if (search_name1 in normalized_title) or (search_name2 in title):
                reply_to_submission(submission)


def comment_stream(reddit):
    print("Starting comment stream")
    subreddits = reddit.subreddit(subreddit_names)

    # Loop comment stream. "pause_after" will yield None if there are no new comments
    for comment in subreddits.stream.comments(pause_after=0):
        if comment is None:
            print("Closing comment stream")
            break
        process_comment(comment)


def submission_stream(reddit):
    print("Starting submission stream")
    subreddits = reddit.subreddit(subreddit_names)

    # Loop submission stream. "pause_after" will yield None if there are no new submissions
    for submission in subreddits.stream.submissions(pause_after=0):
        if submission is None:
            print("Ending submission stream")
            break
        process_submission(submission)


def get_time_now():
    local_time = time.localtime()  # get struct_time
    time_now = time.strftime("%d.%m.%Y, %H:%M:%S", local_time)
    return time_now


def main():
    redditConfig = get_config_object("reddit")

    reddit = praw.Reddit(
        user_agent=redditConfig["user_agent"],
        client_id=redditConfig["client_id"],
        client_secret=redditConfig["client_secret"],
        username=redditConfig["username"],
        password=redditConfig["password"]
    )

    # Go through comment stream and submission stream (pause_after in each of the streams will stop stream)
    # Then sleep for 5 minutes and start again
    # Probably shouldnt be done like this for high volume subreddits, since "pause_after" might never kick in? Not sure.
    while True:
        time_now_string = get_time_now()
        print(f"{get_time_now()} - Starting streams")

        submission_stream(reddit)
        comment_stream(reddit)

        sleepForMinutes = 5
        print(f"{get_time_now()} - Going to sleep for {sleepForMinutes} minutes.")
        time.sleep(sleepForMinutes * 60)


if __name__ == "__main__":
    main()