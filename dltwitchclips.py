import requests, json, praw, os
from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo
from bs4 import BeautifulSoup

reddit = praw.Reddit(
    client_id="id here",
    client_secret="secret here",
    password="password here",
    user_agent="user agent here",
    username="username here",
)

class Video:
    def __init__(self, url, title, top_comment, already_exists):
        self.url = url
        self.title = title
        self.top_comment = top_comment
        self.already_exists = already_exists


def twitch_scrape(clip_url, title):
    slug = clip_url.split('/')[-1]

    url = 'https://gql.twitch.tv/gql'

    headers = {
        'Client-Id': 'client id here',
        'Content-Type': 'text/plain;charset=UTF-8',
        'Origin': 'https://clips.twitch.tv',
        'Referer': f'https://clips.twitch.tv/{slug}',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    }

    payload = [{"operationName":"VideoAccessToken_Clip","variables":{"slug": slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9bfcc0177bffc730bd5a5a89005869d2773480cf1738c592143b5173634b7d15"}}}]

    r = requests.post(url, data=json.dumps(payload[0]), headers=headers)
    video_url = json.loads(r.text)
    video_url = video_url['data']['clip']['videoQualities'][0]['sourceURL']

    filename = f"{title}.mp4"

    with open(filename, 'wb') as f:
        print('Downloading', f'"{video_url}"', 'as', f'"{filename}"')
        r = requests.get(video_url)
        f.write(r.content)

def get_urls(name, limit):
    videos = []
    limit = limit
    for submission in reddit.subreddit(name).hot(limit=limit):
        submission.comment_sort = "top"

        top_comment = ""
        if len(submission.comments) > 0:
            top_comment = [comment.body for comment in submission.comments if (hasattr(comment, "body") and comment.distinguished==None)][0]
            #print("top: " + top_comment + " " + submission.title)

        if str(submission.url).find("https://clips.twitch.tv/") != -1:
            v = Video(str(submission.url), submission.title, top_comment, False)
            videos.append(v)
    return videos
    
def download_videos(videos):
    arr = os.listdir()
    print(arr)
    for video in videos:
        if video.title + ".mp4" not in arr:
            twitch_scrape(video.url, video.title)
        else:
            video.already_exists = True
            print("Video already exists: " + video.title + " com " + video.top_comment)

# loggin into the channel
channel = Channel()
channel.login("client_secret.json", "credentials.storage")

def upload_videos(videos):
    for m_video in videos:
        if not m_video.already_exists:
            # setting up the video that is going to be uploaded
            video = LocalVideo(file_path=m_video.title + ".mp4")
            # setting snippet
            video.set_title(m_video.title)
            video.set_description(m_video.top_comment)
            #video.set_category("gaming")
            video.set_default_language("en-US")

            # setting status
            video.set_embeddable(True)
            video.set_privacy_status("public")
            video.set_public_stats_viewable(True)

            # setting thumbnail
            #video.set_thumbnail_path("test_thumb.png")
            #video.set_playlist("PLDjcYN-DQyqTeSzCg-54m4stTVyQaJrGi")

            # uploading video and printing the results
            video = channel.upload_video(video)
            print(video)

            # liking video
            #video.like()