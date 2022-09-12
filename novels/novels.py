import novel

f = open('ptt.txt', 'r', encoding='utf-8')
text = []
flag = True
for line in f:
    if flag == True:
        flag = False
    elif flag == False:
        line = line.strip(('\n'))
        text.append(line)
        flag = True
# print(text)

for i in range(len(text)):
    novel.ptt(text[i], i)
