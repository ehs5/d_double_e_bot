import configparser
import random
import time

import praw

searchName1 = " d double"
searchName2 = "D Double"
bot_username = "d_double_e_bot"
subredditNames = "grime+ukdrill+ukhiphopheads"
repliedCommentsFileName = "d_double_e_bot_replied_comments.txt"
repliedSubmissionsFileName = "d_double_e_bot_replied_submissions.txt"
logFileName = "d_double_e_bot_log.txt"

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


def getConfigObject(configObjectName):
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    config_object = config[configObjectName]
    return config_object


def addToTxtFile(fileName, string):
    file = open(fileName, 'a')
    file.write(string)
    file.close()


def getTxtFileAsList(fileName):
    txtFileAsList = open(fileName).read().splitlines()
    return txtFileAsList


def createLogStringComment(comment, randomPhrase):
    str1 = f"Man like u/{comment.author.name} in r/{comment.subreddit.display_name} commented:"
    str2 = f"\n{comment.body}"
    str3 = f"\nComment ID: {comment.id}"
    str4 = f"\nReplied with: {randomPhrase}"
    str5 = f"\n------------------------------\n"
    return str1 + str2 + str3 + str4 + str5


def createLogStringSubmission(submission, randomPhrase):
    str1 = f"Man like u/{submission.author.name} in r/{submission.subreddit.display_name} made a submission:"
    str2 = f"\n{submission.title}"
    str3 = f"\nSubmission ID: {submission.id}"
    str4 = f"\nReplied with: {randomPhrase}"
    str5 = f"\n------------------------------\n"
    return str1 + str2 + str3 + str4 + str5


def replyToComment(comment):
    randomPhrase = random.choice(phrases)
    comment.reply(randomPhrase)
    addToTxtFile(repliedCommentsFileName, f"{comment.id}\n")
    logEntry = createLogStringComment(comment, randomPhrase)
    addToTxtFile(logFileName, logEntry)
    print(logEntry)


def replyToSubmission(submission):
    randomPhrase = random.choice(phrases)
    submission.reply(randomPhrase)
    addToTxtFile(repliedSubmissionsFileName, f"{submission.id}\n")
    logEntry = createLogStringSubmission(submission, randomPhrase)
    addToTxtFile(logFileName, logEntry)
    print(logEntry)


def processComment(comment):
    if comment.author.name != bot_username:
        if comment.id not in getTxtFileAsList(repliedCommentsFileName):
            body = comment.body
            normalized_body = body.lower()
            if (searchName1 in normalized_body) or (searchName2 in body):
                replyToComment(comment)


def processSubmission(submission):
    if submission.author.name != bot_username:
        if submission.id not in getTxtFileAsList(repliedSubmissionsFileName):
            title = submission.title
            normalized_title = title.lower()
            if (searchName1 in normalized_title) or (searchName2 in title):
                replyToSubmission(submission)


def commentStream(reddit):
    print("Starting comment stream")
    subreddits = reddit.subreddit(subredditNames)

    # Loop comment stream. "pause_after" will yield None if there are no new comments
    for comment in subreddits.stream.comments(pause_after=0):
        if comment is None:
            print("Closing comment stream")
            break
        processComment(comment)


def submissionStream(reddit):
    print("Starting submission stream")
    subreddits = reddit.subreddit(subredditNames)

    # Loop submission stream. "pause_after" will yield None if there are no new submissions
    for submission in subreddits.stream.submissions(pause_after=0):
        if submission is None:
            print("Ending submission stream")
            break
        processSubmission(submission)


def getTimeNowString():
    local_time = time.localtime()  # get struct_time
    time_now = time.strftime("%d.%m.%Y, %H:%M:%S", local_time)
    return time_now


def main():
    redditConfig = getConfigObject("reddit")

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
        time_now_string = getTimeNowString()
        print(f"{getTimeNowString()} - Starting streams")

        submissionStream(reddit)
        commentStream(reddit)

        sleepForMinutes = 5
        print(f"{getTimeNowString()} - Going to sleep for {sleepForMinutes} minutes.")
        time.sleep(sleepForMinutes * 60)


if __name__ == "__main__":
    main()
