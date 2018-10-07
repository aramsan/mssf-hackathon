from janome.tokenizer import Tokenizer

t = Tokenizer()
val = 'Panasonic Beauty SALON 銀座では #美容家電 の体験だけではなく、ビューティアーティストによるプチセミナーを平日毎日開催✨（予約不要）\n10月のテーマ🍂は「秋のトレンド #ポイントメイク」いつもの #アイメイク や #リップ を変えてみませんか？\n#パナソニックビューティ #panasonicbeauty'
tokens = t.tokenize(val)
data = []
for token in tokens:
    print(token)
    each_data = []
    partOfSpeech = token.part_of_speech.split(',')[0]
    if partOfSpeech == u'名詞':
        print(token.surface)
        if token.surface != "#":
            data.append(token.surface)

print(data)
