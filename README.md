# Chat_moment_finder

Basic usage:

```
python Chat_moment_finder.py <vod_id> -e <emote_name>
```

additional args

```
-r <resolution> , size of splits for searching. defualt is 60 seconds
-t <threshold> , how many emote occurances needed to conside a point of intrest
-j <json_file> , gql json file to bypass the need to keep redownloading chat, generated on inital run
-c <chat_json> , name of json file to export gql chat to, default is chat.json
```
