from database.db import mongo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "futbase.notifications@gmail.com"
password = "Futbase1!"

def send_wishlist_email(player):

    """
    If a new player is created that has an existing base card, anyone that has any version of that player
    on their wishlist are emailed letting them know a new card is out
    """

    # Get emails of user that have any version of this card on their wishlist
    wishlist_emails = mongo.db.users.find(
        {"wishlist.base_id": player["base_id"]}, {"email": 1}
    )

    message = MIMEMultipart("alternative")
    message["Subject"] = f"{player['player_name']} has a new card!"

    text = f"Hi there,\nA player on your wishlist has a new FIFA card!\n\nName: {player['player_name']}\nOverall: {player['overall']}\nPosition: {player['position']}\nQuality: {player['quality']}\nRevision: {player['revision']}\n\nLog in to Futbase to view their new card in full! - http://localhost:5000"

    # Turn this into a plain MIMEText object
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    # Start server, login and send emails
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)

    for user in wishlist_emails:
        receiver_email = user["email"]
        server.sendmail(sender_email, receiver_email, message.as_string())

def send_registration_email(email):

    """
    If a new user is created, the email they provide is sent a registration success email
    """
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Welcome to Futbase!"

    text = f"Hi there,\nYour account was created successfully.\n\nLog in to Futbase to get started! - http://localhost:5000"

    # Turn this into a plain MIMEText object
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    # Start server, login and send emails
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    receiver_email = email
    server.sendmail(sender_email, receiver_email, message.as_string())


def send_deletion_email(email):

    """
    If user is deleted, the email they provide is sent a deletion success email
    """
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"So long for now!"

    text = f"Hi there,\nYour account was deleted successfully.\n\nWe hope to see you back at Futbase soon! - http://localhost:5000"

    # Turn this into a plain MIMEText object
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    # Start server, login and send emails
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    receiver_email = email
    server.sendmail(sender_email, receiver_email, message.as_string())



    
    