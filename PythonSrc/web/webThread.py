# We want a single point of contact for http requests since
# most apps don't handle interleaved requests at all well
# and for maybe ws:

# according to the rpi Pico implementation doc for Micropython it supports exactly 1 extra thread
# and that uses the second core
# so we'll use the second thread for all of the network i/o
# likely won't play with vscode
# urequests.request(method, url, data=None, json=None, headers={})
# response has text, Content, json() the last returns it json encoded
# 
# this is not currently being used but would make good sense in a thread hint hint

	
# import web.ureq as urequests
import web.ureqorig as urequests
from util.picoPendant import GlobalPico
from utime import ticks_ms, ticks_diff
import _thread

def WebQ() :
	global _webQ
	return _webQ

class WebQPacket :
	def __init__(self, text, wait) :
		self.text = text
		self.timeout = wait

class WebQueue :
	def __init__(self) :
		self.qPackets = []
		self.qResponses = []
		self._WebAccessLock = _thread.allocate_lock()
		self.doExit = False
		self._Pending = 0
		self._IsRunning = False
		self.doPosition = False

	@property
	def AccessLock(self) :
		return self._WebAccessLock

	@property
	def HasData(self) :
		return len(self.qResponses) > 0

	@property
	def IsRunning(self) :
		return self._IsRunning

	def Exit(self) :
		self.doExit = True

	def AddPacket(self, text, timeoutMs) :
		print("adding packet")
		if self._WebAccessLock.acquire(1, 3.0) : # wait 3 secs for lock
			print("adding packet %s" % text)
			self.qPackets.append( WebQPacket(text, timeoutMs))
			self._WebAccessLock.release()
		else :
			print('Unable to lock AddPacket')

	def GetResponse(self, timeout) :
		u = ticks_ms() + timeout
		while ticks_diff(u , ticks_ms()) > 0 :
			if len(self.qResponses) > 0 :
				if self._WebAccessLock.acquire(1, 3.0) : # wait 3 secs for lock
					u = self.qResponses.pop(0)
					print('pop response')
					self._WebAccessLock.release()
				else :
					print('Unable to lock GetResponse')
					u = None
				return u
		return None

	def doThreadStep(self) :
		if self.doExit :
			return True
		qp = None
		#print("Step...")
		if self._Pending == 0 and len( self.qPackets) > 0 :
			if self._WebAccessLock.acquire(1,1) :
				if len( self.qPackets) > 0 :
					qp = self.qPackets.pop(0)
					print("Pop packet")
				self._WebAccessLock.release()
		if qp != None :
			print('Sending packet %d' % ticks_ms())
			self._SendPacket(qp.text, qp.timeout)
			print('Sent packet %d' % ticks_ms())
		return False

	def RunForever(self) :
		if self._WebAccessLock.acquire(1, 3.0) : # wait 3 secs for lock
			self._IsRunning = True
			self._WebAccessLock.release()
			print("Running...F")
		try:
			while  self._IsRunning :
				if self.doThreadStep() :
					print('exiting gracefully')
					self._IsRunning = False
		except Exception as e:
			print(str(e))
		finally:
			 self._IsRunning = False

	def EnablePosition(self) :
		self.doPosition = True

	def RunWebThread(self):
		id = None
		if self._WebAccessLock.acquire(1, 3.0) : # wait 3 secs for lock
			if not self._IsRunning :
				self._WebAccessLock.release()
				id = _thread.start_new_thread(self.RunForever, ())
			else :
				self._WebAccessLock.release()
		return id

	def _SendPacket(self, text, timeoutMs = 0) :
		try :
			print("Send packet: %s" % text)
			response = urequests.get(text)
			print('response gotten at %d' % ticks_ms())
			print('response=' + str(response))
			if self._WebAccessLock.acquire(1, 3.0) : # wait 3 secs for lock
				self.qResponses.append(response)
				self._WebAccessLock.release()
		except Exception as e:
			print(str(e))

_webQ = WebQueue()
