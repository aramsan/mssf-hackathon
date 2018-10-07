CONSUMER_KEY        = 'Yv0bhw3UuaqQudLRvjkJedi2d'
CONSUMER_SECRET_KEY = 'vwu8z3uNxNh0xCpvR8UmmBVE3wn5uvRRwDGoFxJdk2NXSnb3wa'
ACCESS_TOKEN        = '219330389-KTcnHtvS1XNOyvSLVadDSK8uM7H0AuRZxh01bOFv'
ACCESS_TOKEN_SECRET = 'lrrQNjsWA3XmeU6xN9DzFQfFBAarTEekhgiTK2KBdpFGS'
    
from twitter import *

t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET_KEY))

timelines = t.statuses.user_timeline(screen_name="PanasonicBeauty", exclude_replies="true", tweet_mode="extended", count=1)
for timeline in timelines:
    print(timeline)
    print('-------------------------------------')
    tl = '({id}) [{username}]:{text}'.format(
        id=timeline['id'], username=timeline['user']['screen_name'], text=timeline['full_text'])
    print (tl)
