import public_config as pc
import utility as util
import random
import time
import praw


def create_log_string_comment(comment, random_phrase) -> str:
    return f"Man like u/{comment.author.name} in r/{comment.subreddit.display_name} commented:" \
           f"\n{comment.body}"                                                                  \
           f"\nComment ID: {comment.id}"                                                        \
           f"\nReplied with: {random_phrase}"                                                   \
           f"\n------------------------------\n"


def create_log_string_submission(submission, random_phrase):
    return f"Man like u/{submission.author.name} in r/{submission.subreddit.display_name} made a submission:"   \
           f"\n{submission.title}"                                                                              \
           f"\nSubmission ID: {submission.id}"                                                                  \
           f"\nReplied with: {random_phrase}"                                                                   \
           f"\n------------------------------\n"


def reply_to_comment(comment: praw.reddit.Comment) -> None:
    random_phrase = random.choice(pc.PHRASES)
    comment.reply(random_phrase)
    util.add_to_txt_file(pc.REPLIED_COMMENTS_FILENAME, f"{comment.id}\n")
    log_entry = create_log_string_comment(comment, random_phrase)
    util.add_to_txt_file(pc.LOG_FILENAME, log_entry)
    print(log_entry)


def reply_to_submission(submission: praw.reddit.Submission) -> None:
    random_phrase = random.choice(pc.PHRASES)
    submission.reply(random_phrase)
    util.add_to_txt_file(pc.REPLIED_SUBMISSIONS_FILENAME, f"{submission.id}\n")
    log_entry = create_log_string_submission(submission, random_phrase)
    util.add_to_txt_file(pc.LOG_FILENAME, log_entry)
    print(log_entry)


def process_comment(comment: praw.reddit.Comment) -> None:
    if comment.id not in util.get_txt_file_as_list(pc.REPLIED_COMMENTS_FILENAME):
        body = comment.body
        normalized_body = body.lower()
        if (pc.SEARCH_NAME1 in normalized_body) or (pc.SEARCH_NAME2 in body):
            reply_to_comment(comment)


def process_submission(submission: praw.reddit.Submission) -> None:
    if submission.id not in util.get_txt_file_as_list(pc.REPLIED_SUBMISSIONS_FILENAME):
        title = submission.title
        normalized_title = title.lower()
        if (pc.SEARCH_NAME1 in normalized_title) or (pc.SEARCH_NAME2 in title):
            reply_to_submission(submission)


def comment_stream(reddit: praw.Reddit) -> None:
    print("Starting comment stream")
    subreddits = reddit.subreddit(pc.SUBREDDIT_NAMES)

    # Loop comment stream. "pause_after" will yield None if there are no new comments
    for comment in subreddits.stream.comments(pause_after=0):
        if comment is None:
            print("Closing comment stream")
            break
        process_comment(comment)


def submission_stream(reddit: praw.Reddit) -> None:
    print("Starting submission stream")
    subreddits = reddit.subreddit(pc.SUBREDDIT_NAMES)

    # Loop submission stream. "pause_after" will yield None if there are no new submissions
    for submission in subreddits.stream.submissions(pause_after=0):
        if submission is None:
            print("Ending submission stream")
            break
        process_submission(submission)


def get_time_now() -> str:
    local_time = time.localtime()  # get struct_time
    time_now = time.strftime("%d.%m.%Y, %H:%M:%S", local_time)
    return time_now


def main() -> None:
    reddit_config = util.get_config_object("reddit")

    reddit = praw.Reddit(
        user_agent=reddit_config["user_agent"],
        client_id=reddit_config["client_id"],
        client_secret=reddit_config["client_secret"],
        username=reddit_config["username"],
        password=reddit_config["password"]
    )

    # Go through comment stream and submission stream (pause_after in each of the streams will stop stream)
    # Then sleep for 5 minutes and start again
    # Might not be best approach for high volume subreddits, since "pause_after" might never kick in? Not sure.
    while True:
        print(f"{get_time_now()} - Starting streams")

        submission_stream(reddit)
        comment_stream(reddit)

        sleep_for_minutes = 5
        print(f"{get_time_now()} - Going to sleep for {sleep_for_minutes} minutes.")
        time.sleep(sleep_for_minutes * 60)


if __name__ == "__main__":
    main()
