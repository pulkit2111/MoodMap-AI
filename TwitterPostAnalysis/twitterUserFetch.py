import tweepy
import os
from tweepy import OAuthHandler
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials
Access_Token = os.getenv('ACCESS_TOKEN')
Access_Secret = os.getenv('ACCESS_SECRET')
API_Key = os.getenv('API_KEY')
API_Secret = os.getenv('API_SECRET')
Bearer_Token = os.getenv('BEARER_TOKEN')

def extract_username(url):
    """
    Extract the Twitter username from the URL.
    Example URL: https://x.com/PrakashJavdekar/status/1399737199956938757
    Expected output: PrakashJavdekar
    """
    try:
        # Extracting the username part from the URL
        username = url.strip().split('/')[3]  # The username comes after "https://x.com/"
        if username:
            return username
        else:
            return None
    except Exception as e:
        return f"Error: Could not extract username ({e})"

def get_user_info(username):
    """
    Retrieve user information from Twitter by username.
    """
    # Set up authentication
    client = tweepy.Client(bearer_token=Bearer_Token)

# auth = tweepy.OAuth2BearerHandler(os.environ.get("TWITTER_API_KEY"))
    try:
        # Get user details using the username
        response = client.get_user(username=username, user_fields=['description', 'public_metrics', 'created_at', 'profile_image_url', 'location'])
        if response.data:
            user = response.data
            
            # Prepare and return user info
            user_info = {
                "Username": user.username,
                "Name": user.name,
                "Bio": user.description,
                "Location": user.location,
                "Followers Count": user.public_metrics['followers_count'],
                "Following Count": user.public_metrics['following_count'],
                "Total Tweets": user.public_metrics['tweet_count'],
                "Account Created At": user.created_at,
                "Profile Image URL": user.profile_image_url
            }
            return user_info
        else:
            return "User not found."
    
    except tweepy.TweepyException as e:
        return f"Error: {e}"