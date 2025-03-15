import pysrt
import strings
from googletrans import Translator
import asyncio

class Subtitles:
	def __init__(self, file=None):
		self.subs = None
		self.open(file)
		self.id = 0
		self.oldText = ""
		
	def open(self, file):
		if file != None:
			try:
				self.subs = pysrt.open(file)
			except IOError as e:
				print(u'не удалось открыть файл')
				self.subs = None

	def getCurSub(self, ms):
		text = ""
		if self.subs != None:
			i = self.id
			while True:
				if i >= len(self.subs):
					break
				s = self.toMs(self.subs[i].start)
				e = self.toMs(self.subs[i].end)
				if ms < s:
					break
				if ms > s and ms < e:
					text += self.subs[i].text
				if ms > e:
					self.id+=1
				i+=1
		return text
	
	async def translateText(self, text):
		async with Translator() as translator:
			result = await translator.translate(text,dest=strings.TRANSLATE_DEST)
			if not result:
				return ''
			return result.text


	def getTranslateCurSub(self, ms):
		text = self.getCurSub(ms)
		if text == self.oldText:
			return None
		self.oldText = text
		try:
			tr = asyncio.run(self.translateText(text))
		except:
			return ""
		return tr
		
	def toMs(self, time):
		h = time.hours
		m = time.minutes
		s = time.seconds
		ms = time.milliseconds
		return h*3600000+m*60000+s*1000+ms
		
	def translate(self, text):
		if text == self.oldText:
			return None
		self.oldText = text
		try:
			tr = asyncio.run(self.translateText(text))
		except:
			return ""
		return tr
		
		
		