#coding=utf-8

import os
import sys
from urllib import request
from urllib import parse
from urllib import error
import simplejson as json
import re
import time
import collections

class SpellCorrector(object):
	def __init__(self):
		self.NWORDS = self.train(self.words(open('big.txt', 'r').read()))
		self.alphabet = 'abcdefghijklmnopqrstuvwxyz'

	def words(self, text): 
		return re.findall('[a-z]+', text.lower()) 

	def train(self, features):
		model = collections.defaultdict(lambda: 1)
		for f in features:
			model[f] += 1
		return model

	def edits1(self, word):
		splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		deletes    = [a + b[1:] for a, b in splits if b]
		transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
		replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
		inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
		return set(deletes + transposes + replaces + inserts)

	def known_edits2(self, word):
		return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.NWORDS)

	def known(self, words): 
		return set(w for w in words if w in self.NWORDS)

	def correct(self, word):
		candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
		return max(candidates, key=self.NWORDS.get)

API_KEY = '1437381740'
KEYFROM = 'py-youdao-dict'

global g_fileSets

g_fileSets = [[] for i in range(26)]

def LoadSavedFile():
	global g_fileSets

	try:
		filepath = r'py-youdao-dict.json'
		fp = open(filepath, 'r+')
	except FileNotFoundError:
		print(u'%s文件不存在' %filepath)	
		return
	fp.seek(os.SEEK_SET)
	file = fp.readlines()
	file.sort(key=lambda x:json.loads(x).get('query', ''))
	#for line in file:
	#	print(line)
	fp.close()
	
	for line in file:
		currentQuery = json.loads(line).get('query', '')
		setIdx = ord(currentQuery.lower()[0]) - ord('a')
		g_fileSets[setIdx].append(json.loads(line))

	'''
	for i in g_fileSets:
		if i != []:
			print('*' * 40)
			for j in i:
				print(j)
	'''

def GetTranslateFromFile(query):
	global g_fileSets

	query = query.lower()
	findWord = False
	setIdx = ord(query[0]) - ord('a')
	if [] != g_fileSets[setIdx]:
		for wordSaved in g_fileSets[setIdx]:
			if query == wordSaved.get('query', ''):
				findWord = True
				break
			
	if findWord:	
		return wordSaved
	else:
		return None	

def SaveWordToFile(query, jsonData, cmdDict):
	global g_fileSets

	query = query.lower()
	if not cmdDict['noSave']:
		choices = 'y'
		if not cmdDict['autoSave']:
			choices = input(u'是否写入单词本，回复(y/n):')
		if choices in ['y', 'Y']:
			alreadySaved = False
			setIdx = ord(query[0]) - ord('a')
			#print(g_fileSets[setIdx])
			if [] == g_fileSets[setIdx]:
				g_fileSets[setIdx].append(jsonData)
			else:	
				for wordSaved in g_fileSets[setIdx]:
					if query == wordSaved.get('query', ''):
						alreadySaved = True
						break

			if alreadySaved:
				print(u'单词已经在单词本\r\n')
			else:
				g_fileSets[setIdx].append(jsonData)
				filepath = r'py-youdao-dict.json'
				fp = open(filepath, 'a+')
				fp.write(json.dumps(jsonData))
				fp.write('\r\n')
				fp.close()
				print(u'写入单词本成功\r\n')


def GetTranslate(query):
	query = query.lower()
	url = 'http://fanyi.youdao.com/openapi.do'
	data = {
		'keyfrom': KEYFROM,
		'key': API_KEY,
		'type': 'data',
		'doctype': 'json',
		'version': 1.1,
		'q': query
	}
	data = parse.urlencode(data)
	url = url+'?'+data
	req = request.Request(url)
	offline = False
	try:
		response = request.urlopen(req)
	except error.URLError:
		offline = True
		result = GetTranslateFromFile(query)
	if not offline:	
		result = json.loads(response.read())
	return result

def Sjson(jsonData, cmdDict):
	if None == jsonData:
		print(u'单词本中没有收录该单词，请联网查询！\r\n')
		return

	query = jsonData.get('query', '')
	translation = jsonData.get('translation', '')
	basic = jsonData.get('basic', '')
	if basic == '':
		print(u'查询单词出现错误')
		return

	sequence = ''
	if not cmdDict['simpleMode']:	
		sequence = jsonData.get('web', [])	
	phonetic, explains_txt, seq_txt, log_word_explains = \
		'', '', '', ''

	if basic:
		phonetic = basic.get('phonetic', '')
		explains = basic.get('explains', '')
		for obj in explains:
			explains_txt += obj+'\n'
			log_word_explains += obj+','

	if sequence:
		for obj in sequence:
			seq_txt += obj['key']+'\n'
			values = ''
			for i in obj['value']:
				values += i+','
			seq_txt += values+'\n'

	print_format = ''
	print_format += '*'*40+'\n'
	print_format += u'查询对象： %s [%s]\n' %(query, phonetic)
	print_format += explains_txt
	print_format += '-'*20+'\n'+seq_txt
	print_format += '*'*40+'\n'
	print(print_format, end='')

	SaveWordToFile(query, jsonData, cmdDict)
		

def Usage(cmdDict):
	print('*' * 40)
	print(u'0:显示帮助')
	print(u'1:退出')
	print(u'2:自动/手动保存到单词本 - 当前%s保存' \
		%(u'自动' if cmdDict['autoSave'] else u'手动'))
	print(u'3:不保存到单词本')
	print(u'4:打开/关闭简洁模式 - 当前%s模式' \
		%(u'打开' if cmdDict['simpleMode'] else u'关闭') )
	print('*' * 40 + '\r\n')

def DecodeCommand(cmd, usageDict, cmdDict):
	if 'showUsage' == usageDict[cmd]:
		Usage(cmdDict)
	elif 'quitProgram' == usageDict[cmd]:
		exit(0)	
	else:
		if 'simpleMode' == usageDict[cmd]:
			cmdDict['simpleMode'] = not cmdDict['simpleMode']
		if 'autoSave' == usageDict[cmd]:	
			cmdDict['autoSave'] = not cmdDict['autoSave']
			cmdDict['noSave'] =  False
		if 'noSave' == usageDict[cmd]:
			cmdDict['autoSave'] = False
			cmdDict['noSave'] = True	

def WordbookSample(cmdDict):
	with open('wordbook-sample.txt', 'r') as fp:
		print(u'单词本开始收录')	
		file = fp.readlines()
		txtCounter = 0
		for line in file:
			wordbookSample = list(filter(lambda x:x!= '', re.split(r'[^a-zA-Z]+', line)))
			for txt in wordbookSample:
				txtCounter += 1
				if 0 == (txtCounter & 15):
					time.sleep(1)
				#使用API查询，请求频率限制为每小时1000次，超过限制会被封禁	
				if txtCounter >= 900:
					return	
				Sjson(GetTranslate(txt.lower()), cmdDict)
		print(u'单词本收录完毕')	


def main():
	usageDict = {
		u'0': 'showUsage', 
		u'1': 'quitProgram',
		u'2': 'autoSave',
		u'3': 'noSave',
		u'4': 'simpleMode',
	}
	cmdDict = {
		'showUsage': False,
		'quitProgram': False,
		'autoSave': True,
		'noSave': False,
		'simpleMode': False,
	}	

	spellCorrector = SpellCorrector()

	LoadSavedFile()	
	#WordbookSample(cmdDict)
	#return

	Usage(cmdDict)

	while True:
		txt = input(u'请输入要查询的文本：')
		if txt:
			if txt in usageDict:
				DecodeCommand(txt, usageDict, cmdDict)
			else:
				correctTxt = spellCorrector.correct(txt) 
				if correctTxt != txt:
					print(u'您想要输入的是'+correctTxt+'吗(y/n/r)：')
					correctChoice = input()
					if correctChoice in ['y', 'Y']:
						txt = correctTxt
					elif correctChoice in ['r', 'R']:
						continue
				Sjson(GetTranslate(txt.lower()), cmdDict)

if __name__ == '__main__':
	main()
