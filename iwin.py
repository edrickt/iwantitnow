import praw
import time
import sys
import smtplib
import os
import threading
from email.message import EmailMessage

# Read the password file line by line.
with open("password.txt") as r:
    passwordfile = r.read().splitlines()


# Clear function to clear the console for output purposes.
def clear():
    clear = lambda: os.system('cls')
    clear()


# Email class that has the purpose of sending the alert email.
class Email:
    def __init__(self, email):
        self.email = email

    # Uses smtplib to send an email as an alert.
    def send_email(self, content, keyword, subreddit):
        try:
            # Specific to Google's smpt server.
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login("iwit.itemchecker@gmail.com", passwordfile[0])

            # Contents of the message.
            msg = EmailMessage()
            msg['Subject'] = "KEYWORD \"" + keyword + "\" IN r/" + subreddit + "\n"
            msg['From'] = "iwit.itemchecker@gmail.com"
            msg['To'] = self.email

            msg.set_content(content)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("FAILED TO SEND EMAIL\n")


# Search class with purpose of searching for a new objects.
class Search:
    def __init__(self, email, subreddit, keyword):
        self.recipient = Email(email)
        self.email = email
        self.subreddit = subreddit
        self.keyword = keyword

        # Uses Reddit's Python API wrapper.
        self.reddit = praw.Reddit(client_id=passwordfile[3],
                                  client_secret=passwordfile[4],
                                  user_agent='I Want It Now/0.0.1',
                                  username=passwordfile[1],
                                  password=passwordfile[2])

        self.initialize_search()

    # Will initialize search with the first post. The first post will be the post
    # that will be first compared to find if a new post has been found.
    def initialize_search(self):
        print("DO NOT EXIT THIS WINDOW OR ALERTS WILL NOT BE SENT\n")
        print("ALERT SET FOR KEYWORD \"" + self.keyword + "\" IN r/" + self.subreddit + "")
        print("EMAILS WILL BE SENT TO " + self.email + "\n")

        # From praw. Searches specific subreddit with specific keyword sorted by new.
        post = self.reddit.subreddit(self.subreddit).search(self.keyword, sort="new")
        for i in post:
            self.keyword_to_search = i
            time.sleep(60)
            break
        # Threading. Might be able to use for multiple searches in the future?
        while True:
            t = threading.Thread(target=self.search())
            t.start()
            t.join()

    # Function that loops in order to find if a new post has been found. If a new post has been found,
    # then create the message with the title, link, number of comments, and send the email using the
    # email class. New post will be the post that will now be used for comparisons.
    def search(self):
        try:
            new_post = self.reddit.subreddit(self.subreddit).search(self.keyword, sort="new")
            for i in new_post:
                searched_keyword = i
                break
            if searched_keyword.title != self.keyword_to_search.title:
                string = "TITLE: " + searched_keyword.title + "\n"
                string += "LINK: " + searched_keyword.url + "\n"
                string += "# of COMMENTS: " + str(searched_keyword.num_comments) + "\n"
                print(string)
                self.recipient.send_email(string, self.keyword, self.subreddit)
                self.keyword_to_search = searched_keyword
            time.sleep(60)
        except:
            print("ERROR FETCHING LATEST POST\n")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("USAGE: python3 iwin.py example.email@email.com subreddit \"keyword with spaces\"")
        sys.exit()
    clear()
    new_search = Search(sys.argv[1], sys.argv[2], sys.argv[3])
