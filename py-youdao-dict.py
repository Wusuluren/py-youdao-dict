#coding=utf-8

import os
import sys
from urllib import request
from urllib import parse
import simplejson as json
import platform
import datetime

API_KEY = '1437381740'
KEYFROM = 'py-youdao-dict'

def GetTranslate(txt):
	url = 'http://fanyi.youdao.com/openapi.do'
	data = {
		'keyfrom': KEYFROM,
		'key': API_KEY,
		'type': 'data',
		'doctype': 'json',
		'version': 1.1,
		'q': txt
	}
	data = parse.urlencode(data)
	url = url+'?'+data
	req = request.Request(url)
	response = request.urlopen(req)
	result = json.loads(response.read())
	return result

def Sjson(jsonData, cmdDict):
	query = jsonData.get('query', '')
	translation = jsonData.get('translation', '')

	basic = jsonData.get('basic', '')

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

	print_format = '*'*40+'\n'
	print_format += u'查询对象： %s [%s]\n' %(query, phonetic)
	print_format += explains_txt
	print_format += '-'*20+'\n'+seq_txt
	print_format += '*'*40+'\n'
	print(print_format)

	if not cmdDict['noSave']:
		choices = 'y'
		if not cmdDict['autoSave']:
			choices = input(u'是否写入单词本，回复(y/n):')
		if choices in ['y', 'Y']:
			filepath = r'%s.xml' % datetime.date.today()
			fp = open(filepath, 'a+')
			file = fp.readlines()
			if not file:
				fp.write('<wordbook>\n')
				fp.write(u"""    <item>\n    <word>%s</word>\n    <trans><![CDATA[%s]]></trans>\n    <phonetic><![CDATA[[%s]]]></phonetic>\n    <tags>%s</tags>\n    <progress>1</progress>\n    </item>\n\n""" \
					%(query,log_word_explains,phonetic,datetime.date.today()))
				fp.close()
				print(u'写入单词本成功')	



def Usage(cmdDict):
	print('*' * 40)
	print(u'0:显示帮助')
	print(u'1:退出')
	print(u'2:自动/手动保存到单词本 - 当前%s保存' \
		%(u'自动' if cmdDict['autoSave'] else u'手动'))
	print(u'3:不保存到单词本')
	print(u'4:打开/关闭简洁模式 - 当前%s模式' \
		%(u'打开' if cmdDict['simpleMode'] else u'关闭') )
	print('*' * 40)

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

	Usage(cmdDict)

	while True:
		txt = input(u'请输入要查询的文本：')
		if txt:
			if txt in usageDict:
				DecodeCommand(txt, usageDict, cmdDict)
			else:
				Sjson(GetTranslate(txt), cmdDict)

if __name__ == '__main__':
	main()
