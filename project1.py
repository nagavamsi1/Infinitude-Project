import requests
import csv
from datetime import datetime

API_KEY = 'AIzaSyCsczrOWyH7WbVc3l_VbzgpYoBrjJ9GHm0'  # Replace with your API key
VIDEO_ID = 'qbINdz0kmjE'  # Replace with your desired video ID


def get_video_statistics(video_id):
    url = f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}'
    response = requests.get(url)

    if response.json()['items']:
        stats = response.json()['items'][0]['statistics']
        return {
            'likes': int(stats.get('likeCount', 0)),
            'commentCount': int(stats.get('commentCount', 0)),
        }
    return {'likes': 0, 'commentCount': 0}


def get_comments(video_id, published_after=None, published_before=None):
    comments = []
    next_page_token = None

    while True:
        comments_url = f'https://www.googleapis.com/youtube/v3/commentThreads?textFormat=plainText&part=snippet&videoId={video_id}&key={API_KEY}&maxResults=20'
        if next_page_token:
            comments_url += f'&pageToken={next_page_token}'

        response = requests.get(comments_url)
        for item in response.json().get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comment_time = comment['publishedAt']
            published_date = datetime.fromisoformat(comment_time[:-1])  # Remove 'Z' for datetime

            if published_after and published_date < published_after:
                continue
            if published_before and published_date > published_before:
                continue

            comments.append({
                'videoId': video_id,
                'commentId': item['id'],
                'commentedChannelName': comment['authorDisplayName'],
                'comment': comment['textDisplay'],
                'publishedAt': comment_time,
                'commentLikesCount': comment.get('likeCount', 0),
            })

        next_page_token = response.json().get('nextPageToken')
        if not next_page_token:
            break

    return comments


if __name__ == "__main__":
    try:
        # Fetch video statistics
        stats = get_video_statistics(VIDEO_ID)

        # Fetch comments within the specified date range
        all_comments = []
        published_after = datetime(2024, 10, 10)  # Adjust as needed
        published_before = datetime.now()

        comments = get_comments(VIDEO_ID, published_after, published_before)

        for comment in comments:
            comment['videoLikesCount'] = stats['likes']
            comment['videoCommentsCount'] = stats['commentCount']
            all_comments.append(comment)

        if all_comments:
            with open('comments.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                header = ['video_id', 'comment_id', 'commented_channel_name', 'comment', 'published_at',
                          'comment_likes_count', 'video_likes_count', 'video_comments_count']
                writer.writerow(header)

                # Print the header to console
                print(header)

                for comment in all_comments:
                    row = [
                        comment['videoId'],
                        comment['commentId'],
                        comment['commentedChannelName'],
                        comment['comment'],
                        comment['publishedAt'],
                        comment['commentLikesCount'],
                        comment['videoLikesCount'],
                        comment['videoCommentsCount'],
                    ]
                    writer.writerow(row)

                    # Print each row to console
                    print(row)

            print('Comments fetched and saved to comments.csv')
        else:
            print('No comments found.')

    except Exception as e:
        print('An error occurred:', str(e))