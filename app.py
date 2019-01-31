'''application.py - Flask code for the Word Finder General app'''
from flask import Flask, render_template, request
import random
import sys

COUNT = 2
MINLEN = 3
WORDFILE = 'words.txt'
PUNC = ',+-#.@#_'

app = Flask(__name__)
wordlist = []
global_init_flag = False  # set this to True when app has initialized


def load_words():
    '''load words of matching length from a file into a list of lists by word length'''
    wordlist = [[] for i in range(30)]
    try:
        with open(WORDFILE) as wf:
            for word in wf:
                wordlen = len(word) - 1  # remove linefeed from word
                wordlist[wordlen].append(word[:-1])
    except FileNotFoundError:
        sys.exit('Error: cannot open file ' + WORDFILE)

    return wordlist


def word_match(partial_word, word, wordlen):
    '''return true if partial word matches word'''
    for x in range(wordlen):
        if partial_word[x] == '?':
            continue
        if partial_word[x] != word[x]:
            return False
    return True


def wordfind(partial_word):
    '''finds matching words in a list - '?' is wild'''
    wordlen = len(partial_word)
    resultlist = []
    count = 0
    for word in wordlist[wordlen]:
        if word_match(partial_word, word, wordlen):
            resultlist.append(word)
            count += 1
        if count == 100:
            break
    return resultlist


def anagfind(anagram):
    '''finds an anagram by comparing two sorted strings'''
    wordlen = len(anagram)
    srtdarr = sorted(anagram)
    resultlist = []
    for word in wordlist[wordlen]:
        if srtdarr == sorted(word):
            resultlist.append(word)
    return resultlist


def gen_passphrase(num_passphrases):
    '''generate passwords based on 2 words, random punctuation and numerals'''
    pass_list = []
    for i in range(num_passphrases):
        # first word
        num_letters = random.randint(3, 5)
        word_array = [random.choice(wordlist[num_letters])]
        # second word
        num_letters = random.randint(3, 5)
        word_array.append(random.choice(wordlist[num_letters]))
        passphrase = ''
        for word in word_array:
            # randomly capitalize
            if bool(random.getrandbits(1)):
                word = word.capitalize()
            # randomly replace a letter with number
            if bool(random.getrandbits(1)):
                if 'o' in word:
                    word = word.replace('o', '0')
                elif 'i' in word:
                    word = word.replace('i', '1')
                elif 'e' in word:
                    word = word.replace('e', '3')
                elif 's' in word:
                    word = word.replace('s', '5')
            passphrase += word + random.choice(PUNC)
        # add a random number to the end of password
        passphrase += str(random.randint(0, 99))
        pass_list.append(passphrase)
    return pass_list


def initapp():
    # initialize on first run
    global wordlist, global_init_flag
    wordlist = load_words()
    # initialization complete - set global status
    global_init_flag = True


@app.before_request
def check_for_init():
    if global_init_flag == False:
        initapp()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/find', methods=['POST', 'GET'])
def findword():
    word = request.form['partial'].lower()
    if len(word) > 2 and len(word) < 30 and '?' in word:
        resultlist = wordfind(word)
    else:
        resultlist = ['Error: Partial word of between 3 and 29 letters and question marks required.']
    return render_template('results.html', result=resultlist)


@app.route('/anagram', methods=['POST', 'GET'])
def anagram():
    word = request.form['anagram'].lower()
    if len(word) > 2 and len(word) < 30 and word.isalpha():
        resultlist = anagfind(word)
    else:
        resultlist = ['Error: Between 3 and 29 letters required.']
    return render_template('results.html', result=resultlist)


@app.route('/pwgen', methods=['POST', 'GET'])
def pwgen():
    try:
        numpwds = int(request.form['numpwds'])
    except ValueError:
        resultlist = ['Error: Enter an integer between 1 and 100.']
        return render_template('results.html', result=resultlist)

    if numpwds > 0 and numpwds <= 100:
        resultlist = gen_passphrase(numpwds)
    else:
        resultlist = ['Error: Enter an integer between 1 and 100.']
    return render_template('results.html', result=resultlist)


if __name__ == '__main__':
    app.run()
