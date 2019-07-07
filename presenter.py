
import subprocess
import asyncio

class Presenter:
	def __init__(self):
		self.player = None

	def setPlayer(self, w):
		self.player = w
		
	def getEqualizer(self):
		if self.player is None:
			return None
		return self.player.getEqualizer()
		
	def setEqualizer(self, band, value):
		if self.player is None:
			return
		self.player.setEqualizer(band, value)
		
	def setEqualizerPreamp(self, value):
		if self.player is None:
			return
		self.player.setEqualizerPreamp(value)
	
	def getRate(self):
		return self.player.mediaplayer.get_rate()
	
	def setRate(self, val):
		return self.player.mediaplayer.set_rate(val)
		
	def setPlaylist(self, pl):
		self.player.setPlaylist(pl)
		
	def openFile(self, file):
		self.player.playlistList = []
		self.player.openFile([file])
		
	def playById(self, id):
		self.player.playById(id)
		
	def setDelay(self, delay, type):
		self.player.setDelay(delay, type)
		
	def torrentGo(self, id, magnetLink, torrentPath):
		asyncio.ProactorEventLoop().run_until_complete(self.player.playTorrentSubprocess(id, magnetLink, torrentPath))
	