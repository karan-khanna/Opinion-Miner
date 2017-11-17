import bs4,requests,sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import pygal
from pygal.style import DefaultStyle
from nltk.corpus import wordnet
from application import app
from flask import render_template,flash,redirect
from collections import defaultdict

from .forms import LoginForm

from collections import Counter

from nltk.corpus import stopwords

from pygal.style import Style

d=defaultdict(list)
ar=[]
poscount=0
negcount=0
nuecount=0
storing_goodwords=[]
finalDict = {}
pos_word_list = []
neu_word_list = []
neg_word_list = []
good_frequencies = {}
bad_frequencies = {}
mostPosSentence = ''
mostPosSentencePolarity = 0.0
mostNegSentence = ''
mostNegSentencePolarity = 0.0

allSentencesPolarity = []


stop_words = set(stopwords.words('english'))

def split_line(text):
    counter = 0
    global poscount
    global negcount
    global nuecount

    global mostPosSentence
    global mostPosSentencePolarity
    global mostNegSentence
    global mostNegSentencePolarity

    negateWords =['not']
    sid = SentimentIntensityAnalyzer()

    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()

    for sentence in tokenizer.tokenize(text):
        sentencePolarity = sid.polarity_scores(sentence)['compound']
        #-------------------------new code(4th nov)------------------------
        allSentencesPolarity.append(sentencePolarity)

        if(sentencePolarity>0.0):
            poscount+=1;
            if(sentencePolarity>mostPosSentencePolarity):
                mostPosSentence=sentence
                mostPosSentencePolarity=sentencePolarity
        elif(sentencePolarity<0.0):
            negcount+=1
            if(sentencePolarity<mostNegSentencePolarity):
                mostNegSentence=sentence
                mostNegSentencePolarity=sentencePolarity
        else:
            nuecount+=1

        counter=0
        print("The sentence is :>" + sentence)
        words = sentence.split()
        adjectives = []
        taggedSentence = nltk.pos_tag(words)
        print(taggedSentence)
        for key, value in taggedSentence:
            key = key.upper()
            key = key.replace(",","");
            key = key.replace(".","");
            key = key.replace("!","");
            print("COuNTER IS ::>" + str(counter))
            if (value == "JJ"):
                #adjectives.append(key)
                if (sid.polarity_scores(key)['compound']) >= 0.2:
                    if(counter>0 and taggedSentence[counter-1][0] in negateWords):
                        neg_word_list.append(taggedSentence[counter-1][0].upper() + "-" + key.upper())
                    else:
                        pos_word_list.append(key.upper())
                        print("positive adjective " + str(key))

                elif (sid.polarity_scores(key)['compound']) <= -0.2:
                    if(counter>0 and taggedSentence[counter-1][0] in negateWords):
                        pos_word_list.append(taggedSentence[counter-1][0].upper() + "-" + key.upper())
                    else:
                        neg_word_list.append(key.upper())
                        print("negative adjective " + str(key))

                else:
                    neu_word_list.append(key.upper())

            elif value == 'NN':
                print("ENTERED NOUN")
                if counter>0:
                    print("COUNTER GREATER THAN ZERO")
                    if(taggedSentence[counter-1][1]=="JJ" ):
                        if(taggedSentence[counter-2][0] in negateWords):
                            d[key.upper()].append(-(sid.polarity_scores(taggedSentence[counter - 1][0])['compound']))
                        else:
                            d[key.upper()].append(sid.polarity_scores(taggedSentence[counter-1][0])['compound'])
                            print("word------------------->" + str(key) + "  value---------------------->" + str(sid.polarity_scores(taggedSentence[counter-1][0])['compound']))

                    else:

                        d[key.upper()].append(sentencePolarity)
                        print("word------------------->"+str(key)+"  sentence---------------->"+ str(sentence)+ "  value---------------------->"+str(sid.polarity_scores(sentence)['compound']))

                else:
                    print("COUNTER LESS THAN ZERO")
                    d[key.upper()].append(sentencePolarity)
                    print("word------------------->" + str(key) + "  sentence---------------->" + str(sentence) + "  value---------------------->" + str(sid.polarity_scores(sentence)['compound']))
            else:
                print("IN NEITHER")
            counter += 1

    #print(adjectives)
    print("CHANGES ::")
    print(d.items())

    for k, v in d.items():
        count = 0
        sum = 0.0
        for value in v:
            count += 1
            sum = sum + float(value)
        #sum = sum / count
        if (sum>1.0 or sum<(-1.0)):
            finalDict[k] = sum
    print(finalDict)

    print('////////////////////////////////////////////')
    # global pos_word_list
    # global neu_word_list
    # global neg_word_list

    print('Positive :', pos_word_list)
    print('Neutral :', neu_word_list)
    print('Negative :', neg_word_list)





def getUpdatedUrl(url,page_num):
    newUrl = url._replace(query="page="+str(page_num))
    return newUrl.geturl()

def amazonReviews(pageBs) :
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    elems = pageBs.find_all("span", attrs={'data-hook': 'review-body'})
    for e in elems:
        print(e.text.translate(non_bmp_map))
        split_line(e.text)

def snapdealReviews(pageBs) :
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    divtag = pageBs.find_all("div", attrs={'class': 'jsUserAction'})
    for divtags in divtag:
        print(divtags.text.translate(non_bmp_map))
        split_line(divtags.text)

def shopcluesReviews(pageBs) :
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    divtag = pageBs.find_all("div", attrs={'class': 'review_desc'})
    for divtags in divtag:
        p = divtags.find("p")
        print(p.text.translate(non_bmp_map))
        split_line(divtags.text)

def getReviews(url):
    global poscount
    global negcount
    global nuecount
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    parsedUrl = urlparse(url)
    site = parsedUrl.netloc

    for page_num in range(1, 4):
        if site == "www.amazon.in":
            url = parsedUrl._replace(query="pageNumber=" + str(page_num))
        elif site == "www.snapdeal.com":
            url = parsedUrl._replace(query="page=" + str(page_num))
        elif site == "www.shopclues.com":
            url = parsedUrl._replace(query="page=" + str(page_num))

        url=url.geturl()

        page = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
        })
        page.raise_for_status()
        pageBs = BeautifulSoup(page.content, "html.parser")

        if site == "www.amazon.in":
            amazonReviews(pageBs)
        elif site == "www.snapdeal.com":
            snapdealReviews(pageBs)
        elif site == "www.shopclues.com":
            shopcluesReviews(pageBs)

    # pcount = len(pos_word_list);
    # ncount = len(neg_word_list);

    #Another method for counting
    #s=sum(Counter(storing_goodwords).values())
    #print("total good reviews="+str(s))


    print("\n\n\n\n\nTotal count for Good reviews="+str(poscount))
    print("\nTotal count for Bad reviews=",str(negcount))
    print("\nTotal count for Bad reviews=", str(nuecount))

    global good_frequencies
    good_frequencies=Counter(pos_word_list)
    global bad_frequencies
    bad_frequencies=Counter(neg_word_list)
    print(good_frequencies)
    print(bad_frequencies)
    #max_freq = max(Counter(storing_goodwords).values())
    print("Maximum occured word in Good Reviews:")
    for k, v in good_frequencies.most_common(1):
            print("Word is : "+str(k)+" occured "+str(v)+" times")
    print("Maximum occured word in Bad Reviews:")
    for k, v in bad_frequencies.most_common(1):
        print("Word is : "+str(k)+" occured "+str(v)+" times")

def createBarGraph(title, dict, hash, print_value):
    local_style = Style(
        #background='transparent',
        #plot_background='transparent',
        background='#E0E0E0',
        title_font_size=30,
        legend_font_size=20,
        opacity='1',
        opacity_hover='1',
        colors=(hash, '#BBDEFB', '#FF8A80', '#E87653', '#E89B53')
    )
    localDict = {}
    if(len(dict) > 14):
        for k,v in dict.items():
            if(v > 1):
                localDict[k] = v
    else:
        localDict = dict
    bar_chart = pygal.Bar(dynamic_print_values=True, explicit_size=True, width=1200, height=500, disable_xml_declaration=True, style=local_style)

    bar_chart.title = title;
    bar_chart.x_labels = localDict.keys()
    bar_chart.add(print_value, localDict)
    return bar_chart

def createLineGraph(title, hash, print_value):
    local_style = Style(
        background='#E0E0E0',
        title_font_size=30,
        legend_font_size=20,
        opacity='1',
        opacity_hover='1',
        colors=(hash, '#BBDEFB', '#FF8A80', '#E87653', '#E89B53')
    )
    localDict = {}
    i = 0
    for item in allSentencesPolarity:
        i+=1
        localDict[i]=item

    line_chart = pygal.Line(dynamic_print_values=True, explicit_size=True, width=1200, height=500, disable_xml_declaration=True, style=local_style)
    line_chart.title = title
    line_chart.x_labels = localDict.keys()
    line_chart.show_x_labels=False
    line_chart.add(print_value, localDict)
    # line_chart.add('Value', localDict)
    return line_chart

def createPieChart(title):
    local_style = Style(
        background='#E0E0E0',
        title_font_size=30,
        legend_font_size=20,
        opacity='1',
        opacity_hover='1',
        colors=('#69F0AE', '#BBDEFB', '#FF8A80', '#E87653', '#E89B53')
    )

    pie_chart= pygal.Pie(dynamic_print_values=True, explicit_size=True, width=1200, height=500,  disable_xml_declaration=True, style=local_style)
    pie_chart.title = title;

    pie_chart.add('Positive', poscount)
    pie_chart.add('Neutral', nuecount)
    pie_chart.add('Negative', negcount)
    return pie_chart()


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        url = form.openid.data;
        global ar
        ar = []
        global poscount
        poscount = 0
        global negcount
        negcount = 0
        global nuecount
        nuecount = 0
        global storing_goodwords
        storing_goodwords = []
        global finalDict
        finalDict = {}
        global pos_word_list
        pos_word_list = []
        global neu_word_list
        neu_word_list = []
        global neg_word_list
        neg_word_list = []
        global good_frequencies
        good_frequencies = {}
        global bad_frequencies
        bad_frequencies = {}
        global mostPosSentence
        mostPosSentence = ''
        global mostPosSentencePolarity
        mostPosSentencePolarity = 0.0
        global mostNegSentence
        mostNegSentence = ''
        global mostNegSentencePolarity
        mostNegSentencePolarity = 0.0
        global allSentencesPolarity
        allSentencesPolarity = []

        getReviews((url))

        good_graph = createBarGraph("Positive/Good words with frequencies", good_frequencies, '#00C853', 'frequencies')
        bad_graph = createBarGraph("Negative/Bad words with frequencies", bad_frequencies, '#F44336','frequencies')
        noun_graph = createBarGraph("Rating of Features", finalDict, '#BA68C8', 'Score')
        line_graph = createLineGraph("Reviews", '#00796B','Polarity')
        pie_chart = createPieChart("Total Reviews")

        print("MOST POSITIVE :" + mostPosSentence)
        print("MOST NEGATIVE : " + mostNegSentence)
        return render_template('result.html', title='result', good_graph=good_graph, bad_graph=bad_graph,
                               noun_graph=noun_graph,line_graph=line_graph, pie_chart=pie_chart, pos=poscount,neg=negcount,
                               nue=nuecount,mostPositive=mostPosSentence,mostNegative=mostNegSentence)
    return render_template('home.html', title='Enter', form=form)
