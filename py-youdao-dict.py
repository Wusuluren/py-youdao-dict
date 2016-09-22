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
import string
from tkinter import *

#GUI程序
class Application(object):
	def __init__(self):
		self.InitApp()
		self.CreateWidgets()
		self.top.mainloop()

	def InitApp(self):
		#有道词典的OPEN API
		self.API_KEY = '1437381740'
		self.KEYFROM = 'py-youdao-dict'

		self.spellCorrector = SpellCorrector()
		self.predictor = Predictor()
		self.fileSets = [[] for i in range(26)]
		self.listboxIdx = -1
		self.currentText = ''
		self.correctUserInput = ''

		self.LoadSavedFile()

	def CreateWidgets(self):
		self.top = Tk()
		self.top.wm_attributes('-topmost', 1)
		self.top.title('py-youdao-dict')

		self.inputFrame = Frame(self.top)
		self.inputFrame.pack()
		self.userText = StringVar()
		self.userTextEntry = Entry(self.inputFrame, vcmd=self.userTextChanged, textvariable=self.userText)
		self.userTextEntry.grid(row=0, column=0)
		self.userTextEntry.bind('<Key>', self.userTextChanged)
		self.userTextEntry.focus_set()
		self.searchButton = Button(self.inputFrame, text=u'查询', command=self.Search)
		self.searchButton.grid(row=0, column=1)

		self.translateFrame = Frame(self.top)
		self.translateText = Text(self.translateFrame, width=60, height=20)
		# self.translateText.grid(row=1, column=0, columnspan=2)
		self.translateText.grid(row=0, column=0)

		self.predictFrame = Frame(self.top)
		self.userTextPredictListbox = Listbox(self.predictFrame)
		self.userTextPredictListbox.grid(row=0, column=0)

		self.correctFrame = Frame(self.top)
		self.correctUserInput = StringVar()
		self.correctEntry = Entry(self.correctFrame, vcmd=self.correctGetInput, textvariable=self.correctUserInput)
		self.correctEntry.grid(row=0, column=0)
		self.correctEntry.bind('<Key>', self.correctGetInput)

	def correctGetInput(self, event):
		# txt = self.correctUserInput.get()
		if event.keysym in ['y', 'Y']:
			self.correctInput = True
		elif event.keysym in ['n', 'N']:
			self.correctInput = False
		# self.correctEntry.delete(0, END)
		# self.correctEntry.insert(0, txt)	

	def userTextChanged(self, event):
		predictFlag = False
		idx = self.userTextEntry.index(INSERT)-1
		listboxLines = self.userTextPredictListbox.size()

		#print(event.keysym, event.char, event.keycode)
		if event.keysym == 'BackSpace':
			self.listboxIdx = -1
			self.translateFrame.forget()
			self.translateText.forget()

			self.currentText = self.userText.get()[:idx] + self.userText.get()[idx+1:]
			#print('---:'+self.currentText)
			if self.currentText:
				predictFlag = True
			else:
				self.userTextPredictListbox.delete(0, listboxLines)
				self.userTextPredictListbox.forget()
				self.predictFrame.forget()
		elif event.keysym == 'Delete':
			self.listboxIdx = -1
			self.translateFrame.forget()
			self.translateText.forget()

			self.currentText = self.userText.get()[:idx+1] + self.userText.get()[idx+2:]
			if self.currentText:
				predictFlag = True
			else:
				self.userTextPredictListbox.delete(0, listboxLines)
				self.userTextPredictListbox.forget()
				self.predictFrame.forget()
		elif event.keysym == 'Return':
			self.Search()
		elif event.keysym == 'Up':
			if self.listboxIdx > 0:
				self.listboxIdx -= 1
				self.userTextPredictListbox.activate(self.listboxIdx)
				t = self.userTextPredictListbox.get(self.listboxIdx)
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, t)
			elif self.listboxIdx == 0:
				self.listboxIdx = listboxLines	
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, self.currentText)
			elif self.listboxIdx == -1:
				self.listboxIdx = listboxLines-1
				self.userTextPredictListbox.activate(self.listboxIdx)
				t = self.userTextPredictListbox.get(self.listboxIdx)
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, t)
		elif event.keysym == 'Down':
			if self.listboxIdx < listboxLines-1:
				self.listboxIdx += 1
				self.userTextPredictListbox.activate(self.listboxIdx)
				t = self.userTextPredictListbox.get(self.listboxIdx)
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, t)
			elif self.listboxIdx == listboxLines-1:
				self.listboxIdx += 1
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, self.currentText)
			elif self.listboxIdx == listboxLines:
				self.listboxIdx = 0	
				self.userTextPredictListbox.activate(self.listboxIdx)
				t = self.userTextPredictListbox.get(self.listboxIdx)
				self.userTextEntry.delete(0, END)
				self.userTextEntry.insert(0, t)
		elif event.keysym in string.ascii_lowercase:
			self.currentText = self.userText.get() + event.char
			predictFlag = True

		if predictFlag:	
			predictText = self.predictor.Predict(self.currentText)
			#print(self.currentText)
			#print(predictText)

			if predictText:
				self.predictFrame.pack()
				self.userTextPredictListbox.pack()
				self.userTextPredictListbox['height'] = len(predictText)
				self.userTextPredictListbox.delete(0, listboxLines)
				line = 0
				for predict in predictText:
					self.userTextPredictListbox.insert(line, predict)
					line += 1
			else:
				listboxLines = self.userTextPredictListbox.size()
				self.userTextPredictListbox.delete(0, listboxLines)
				self.userTextPredictListbox.forget()
				self.predictFrame.forget()

	def Search(self):
		if not self.currentText:
			return

		self.listboxIdx = -1
		listboxLines = self.userTextPredictListbox.size()
		self.userTextPredictListbox.delete(0, listboxLines)
		self.userTextPredictListbox.forget()
		self.predictFrame.forget()

		txt = self.userTextEntry.get().lower()
		correctTxt = self.spellCorrector.correct(txt)
		if txt != correctTxt:
			self.correctFrame.pack()
			self.correctEntry.delete(0, END)
			self.correctEntry.insert(0, u'您是否想要输入'+correctTxt+'?(y/n)')
			self.correctEntry.pack()
			self.correctEntry.focus_set()
			while True:
				self.correctEntry.wait_variable(self.correctUserInput)
				if self.correctInput:
					txt = correctTxt
					self.userTextEntry.delete(0, END)
					self.userTextEntry.insert(0, txt)
					break
				elif not self.correctInput:
					break
			self.correctEntry.forget()
			self.correctFrame.forget()
			self.userTextEntry.focus_set()	
		
		translate = self.Sjson(self.GetTranslate(txt))
		
		num = 0
		head = 0
		for i in translate:
			head += 1
			if head >= self.translateText['width']:
				num += 1
				head = 0
			if i == '\n':
				num += 1
				head = 0
		#print(num)
		#print(self.translateText['width'])
		#print(len(translate))
		self.translateText['height'] = num
		self.translateText.delete(0.0, END)
		self.translateText.insert(0.0, translate)

		self.translateFrame.pack()
		self.translateText.pack()

	def LoadSavedFile(self):
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
			self.fileSets[setIdx].append(json.loads(line))

	'''
		for i in self.fileSets:
			if i != []:
				print('*' * 40)
				for j in i:
					print(j)
	'''		

	def GetTranslateFromFile(self, query):
		query = query.lower()
		findWord = False
		setIdx = ord(query[0]) - ord('a')
		if [] != self.fileSets[setIdx]:
			for wordSaved in self.fileSets[setIdx]:
				if query == wordSaved.get('query', ''):
					findWord = True
					break
				
		if findWord:	
			return wordSaved
		else:
			return None	

	def SaveWordToFile(self, query, jsonData):
		query = query.lower()
		choices = 'y'
		if choices in ['y', 'Y']:
			alreadySaved = False
			setIdx = ord(query[0]) - ord('a')
			#print(self.fileSets[setIdx])
			if [] == self.fileSets[setIdx]:
				self.fileSets[setIdx].append(jsonData)
			else:	
				for wordSaved in self.fileSets[setIdx]:
					if query == wordSaved.get('query', ''):
						alreadySaved = True
						break

			if alreadySaved:
				print(u'单词已经在单词本\r\n')
			else:
				self.fileSets[setIdx].append(jsonData)
				filepath = r'py-youdao-dict.json'
				fp = open(filepath, 'a+')
				fp.write(json.dumps(jsonData)+'\n')
				#fp.write('\r\n')
				fp.close()
				print(u'写入单词本成功\r\n')

	def GetTranslate(self, query):
		query = query.lower()
		url = 'http://fanyi.youdao.com/openapi.do'
		data = {
			'keyfrom': self.KEYFROM,
			'key': self.API_KEY,
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

	def Sjson(self, jsonData):
		if None == jsonData:
			return u'单词本中没有收录该单词，请联网查询！\r\n'

		query = jsonData.get('query', '')
		translation = jsonData.get('translation', '')
		basic = jsonData.get('basic', '')
		if basic == '':
			return u'查询单词出现错误'

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

		result = ''
		result += u'查询对象： %s [%s]\n' %(query, phonetic)
		result += explains_txt
		result += '-'*20+'\n'+seq_txt	

		self.SaveWordToFile(query, jsonData)

		return result	

	def WordbookSample(self):
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
					Sjson(GetTranslate(txt.lower()))
			print(u'单词本收录完毕')	


#拼写检查
class SpellCorrector(object):
	def __init__(self):
		self.NWORDS = self.train(self.words(open('big.txt', 'r').read()))
		self.alphabet = string.ascii_lowercase

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

#用户输入预测
class Predictor(object):
	def __init__(self):
		with open('big.txt', 'r') as f:
			self.model = collections.defaultdict(lambda: 1)
			self.text = re.findall('[a-z]+', f.read().lower())
			for word in self.text:
				self.model[word] += 1
	
	def Predict(self, txt):
		predictText = re.findall(txt+'[a-z]*', str(self.text))
		predictText = list(set(predictText))
		# predictText.sort()
		predictText.sort(key=lambda x:self.model[x], reverse=True)
		#for x in predictText:
		#	print(self.model[x])
		return predictText[0:5] if len(predictText) > 5 else predictText
		

def gui_main():
	app = Application()

if __name__ == '__main__':
	gui_main()
