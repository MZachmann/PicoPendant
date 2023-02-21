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

	
import web.ureq as urequests
from util.picoPendant import GlobalPico
from utime import ticks_ms
import uasyncio as asyncio

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
		self._WebAccessLock = asyncio.Lock()
		self.doExit = False
		self._Pending = 0
		self.IsRunning = False
		self.doPosition = False

	@property
	def AccessLock(self) :
		return self._WebAccessLock

	@property
	def HasData(self) :
		# asyncio.sleep_ms(100)
		return len(self.qResponses) > 0

	async def Exit(self) :
		#async with self.AccessLock :
		self.doExit = True

	async def AddPacket(self, text, timeoutMs) :
		#await self.AccessLock.acquire()
		# print("adding packet")
		self.qPackets.append( WebQPacket(text, timeoutMs))
		# await asyncio.sleep_ms(100)

	async def GetResponse(self, timeout) :
		timechk = ticks_ms() + (timeout if timeout else 10000)
		while len(self.qResponses) == 0 and timechk > ticks_ms() :
			await asyncio.sleep_ms(100)
		#async with self.AccessLock :
		if len(self.qResponses) > 0 :
			u = self.qResponses.pop(0)
			return u
		return None

	async def doThreadStep(self) :
		#async with self.AccessLock :
		if self.doExit :
			return True
		if self._Pending == 0 and len( self.qPackets) > 0 :
			qp : WebQPacket = self.qPackets.pop(0)
			if qp != None :
				#print('Sending packet %d' % ticks_ms())
				await self._SendPacket(qp.text, qp.timeout)
				#print('Sent packet %d' % ticks_ms())
		return False

	async def RunForever(self) :
		while self.IsRunning :
			await asyncio.sleep_ms(1000)

	def EnablePosition(self) :
		self.doPosition = True

	async def RunAsync(self):
		try:
			self.IsRunning = True
			while True:
				if await self.doThreadStep() :
					print('exiting gracefully')
					break
				await asyncio.sleep_ms(70)
		except Exception as e:
			print(str(e))
		finally:
			self.IsRunning = False

	async def _SendPacket(self, text, timeoutMs = 0) :
		try :
			response = await urequests.get(GlobalPico()['printer_ip'] + '/' + text)
			#print('response gotten at %d' % ticks_ms())
			# print('response=' + response.text)
			self.qResponses.append(response)
		except Exception as e:
			print(str(e))

_webQ = WebQueue()
