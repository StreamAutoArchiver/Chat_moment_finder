import time
import requests
import json
import argparse
import datetime

class TwitchChatDownloader:
    def __init__(self, vod_id):
        self.next_chat = ""
        self.comments = []
        self.rechat_gql_payload = {
                'operationName': 'VideoCommentsByOffsetOrCursor',
                'variables': {
                    'cursor': ''
                },
                'extensions': {
                    'persistedQuery': {
                        'version': 1,
                        'sha256Hash': 'b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a'
                    }
                }
            }
        self.rechat_gql_payload['variables']['videoID'] = str(vod_id)
    
    def get_chat(self):
        while self.download_next_chat_segment():
            pass
        return self.comments
    
    def download_next_chat_segment(self):
        try:
            json_gql = self.download_chat_segment_gql()
            if json_gql == {}:
                return False
            if not json_gql['data']['video']:
                return False
            else:
                cursor = json_gql['data']['video']['comments']['edges'][0]['cursor']
                self.comments += json_gql['data']['video']['comments']['edges']
                if json_gql['data']['video']['comments']['pageInfo']['hasNextPage']:
                    self.rechat_gql_payload['variables']['cursor'] = cursor
                    return True
                return False
        except Exception as e:
            print(f'Error: {e}')
        return False

    def download_chat_segment_gql(self):
        attempts = 0
        while True:
            try:
                r = requests.post('https://gql.twitch.tv/gql', data=json.dumps(self.rechat_gql_payload), headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, timeout=60)
                if r.status_code == 200:
                    return r.json()
                else:
                    attempts += 1
                    print(f"Failed to get json. R-code:{r.status_code}")
                    time.sleep(3)
                    if attempts > 4:
                        print(f"ERROR: Failed to get next part of Chat Json {r.status_code}")
                        return {}
            except Exception as e:
                print(f"ERROR: Error with Request: {e}")
                attempts = 0

def parse_chat(chatjson, resolution, emote_name, threshold):
    emote_time_stamps = {}
    
    for message in chatjson:
        time = int(message['node']['contentOffsetSeconds'])
        bucket = resolution * int(time/ resolution)
        for fragment in message['node']['message']['fragments']:
            if fragment['emote']:
                if emote_name.lower() == fragment['text'].lower():
                    if bucket not in emote_time_stamps:
                        emote_time_stamps[bucket] = 0
                    emote_time_stamps[bucket] += 1
    
    print(emote_name)
    for time in emote_time_stamps:
        if emote_time_stamps[time] >= threshold:
            print(f'Timestamp {datetime.timedelta(0, time)} | count:{emote_time_stamps[time]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Twitch Vod Moment Finder')
    parser.add_argument('vod', help='Id of vod')
    parser.add_argument('-r', dest='resolution', action='store', type=int, default=60, help='How many seconds per time slice of search')
    parser.add_argument('-e', dest='emote', action='store', default='pog', help='Emote to look for events for')
    parser.add_argument('-t', dest='threshold', action='store', type=int, default=20, help='Emote to look for events for')
    parser.add_argument('-j', dest='json', action='store', help='Json file of gql chat, bypass redownloading on subsequent runs')
    parser.add_argument('-c', dest='chatjson', action='store', default='chat.json', help='Output file of chat json from gql')
    args = parser.parse_args()
    
    if not args.json:
        chatjson = TwitchChatDownloader(args.vod).get_chat()
        if args.chatjson:
            with open(args.chatjson, encoding="utf-16", mode="w") as json_file:
                json.dump(chatjson, json_file)
    else:
        with open(args.json, encoding='utf-16') as json_file:
            chatjson =  json.load(json_file)
    
    parse_chat(chatjson, args.resolution, args.emote, args.threshold)