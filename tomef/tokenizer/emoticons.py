from collections import defaultdict

#based on: https://en.wikipedia.org/wiki/List_of_emoticons
western = [':-))','O:-)','0:-)','>:-)',':-)','}:-)','3:-)',':-)',
    ':))','O:)','0:)','>:)','}:)','3:)',':)',
    '0:3',':3',
    '0:-3',':-3',
    ':-]',':]',':->',':>','8-)','8)',':-}',':}',':o)',':c)',':^)','=]','=))','=)',
    ':-D',':D','8-D','8D','x-D','xD','X-D','XD','=D','=3','B^D',':-(',':(',':-c',':c',':-<',
    ':<',':-[',':[',':-||','>:[',':{',':@','>:(',':\'-(',':\'(',':\'-)',':\')','D-\':','D:<','D:','D8','D;',
    'D=','DX',':-O',':O',':-o',':o',':-0','8-0','>:O',':-*',':*',':×',';-)',';)','*-)','*)',';-]',';]',
    ';^)',':-,',';D',':-P',':P','X-P','XP','x-p','xp',':-p',':p',':-Þ',':Þ',':-þ',':þ',':-b',':b',
    'd:','=p','>:P',':-/',':/',':-.','>:\\','>:/',':\\','=/','=\\',':L','=L',':S',':-|',':|',':$',
    ':-X',':X',':-#',':#',':-&',':&','0;^)',
    '>;)','|;-)','|-O',':-J','#-)','%-)','%)',':-###..',':###..','<:-|','\',:-|',
    '\',:-l','<_<','>_>']

western_dict = defaultdict(list)
for emote in western:
    western_dict[emote[0]].append(emote[1:])
