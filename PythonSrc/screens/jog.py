# Jog Screen
# --------------------------
from network import WLAN, STA_IF
import ujson as json
import urequests
# import web.ureqorig as urequests
from utime import ticks_ms, ticks_diff, ticks_add
from display.colorSet import SolidClr
from display.ioBox import IoBox
from screens.screen import pp_screen
from util.picoPendant import GlobalPico
from display.lcdDriver import GlobalLcd

# show X,Y,Z position, let an encoder move left/right
# touch-screen for x-y-z or switch ? or 2 encoders for x,y
# to get position from RRF use  http:/rrf/rr_status and get a stream back with machine and pos

def RunJogger() :
	''' run the thing. if you do x = RunJogger() then you can use x.Loop() to rerun it '''
	x=JogScreen()
	x.Setup()
	x.Loop()
	return x

class JogScreen(pp_screen) :

	def __init__(self) :
		self.Xtext = None
		self.Ytext = None
		self.Ztext = None
		self.Xmtext = None
		self.Ymtext = None
		self.Zmtext = None
		self.Locn = [0,0,0] # location in user coords
		self.Mach = [0,0,0] # location in machine coords
		self.lspace = 4
		self.indent = 10
		self.dialEdit = 'T'	# tic size
		self.showMachine = False
		self.Brightness = 70
		self.LastTouch = [0,0,0,0,0]
		self.WhenTouch = 0
		self.lastDial1Pos = 0
		self.lastDial2Pos = 0
		super().__init__()

	def toEight(self, fio) :
		''' pretty format a number and do unit conversion '''
		if self.IsMetric :
			return '%5.3f' % fio
		else :
			return '%4.4f' % (fio/25.4)

	@property
	def UnitStr(self) :
		''' unit of measure string '''
		return ('mm' if self.IsMetric else 'inch')

	@property
	def AxisIdx(self) :
		''' current axis as an integer index '''
		return 'XYZ'.find(self.whichAxis)

	def DrawValues(self,x,y,z) :
		''' draw the X,Y,Z values and cache the text '''
		a = self.toEight(x)
		if a != self.Xtext :
			self.bigNumbers.DrawText(a, self.xXYZData, self.yX)
			self.Xtext = a
		a = self.toEight(y)
		if a != self.Ytext :
			self.bigNumbers.DrawText(a,  self.xXYZData, self.yY)
			self.Ytext = a
		a = self.toEight(z)
		if a != self.Ztext :
			self.bigNumbers.DrawText(a,  self.xXYZData, self.yZ)
			self.Ztext = a

	def DrawMachine(self,x,y,z) :
		''' draw the X,Y,Z values and cache the text '''
		a = self.toEight(x)
		if a != self.Xmtext :
			self.medText.DrawText(a, self.xXYZData + 10*self.bigWidth + 10, self.yX+3)
			self.mXtext = a
		a = self.toEight(y)
		if a != self.Ymtext :
			self.medText.DrawText(a,  self.xXYZData + 10*self.bigWidth + 10, self.yY+3)
			self.Ymtext = a
		a = self.toEight(z)
		if a != self.Zmtext :
			self.medText.DrawText(a,  self.xXYZData + 10*self.bigWidth + 10, self.yZ+3)
			self.Zmtext = a

	def DrawTicsize(self) :
		''' draw the tic size '''
		u = self.HighlightColor if (self.dialEdit=='T' and self.Dial2Enabled) else self.BackColor
		self.medText.SetText(backclr=u)
		a = self.toEight(self.ticSize)
		self.medText.DrawText(a, self.xUserData, self.ySpeedInfo)
		self.medText.SetText(backclr=self.BackColor)

	def DrawDevice(self) :
		''' draw the device name and ip '''
		self.medText.DrawText(GlobalPico()['device'] + '  ', self.xUserInfo, self.yDeviceInfo)
		u = self.HighlightColor if self.dialEdit=='D' else self.BackColor
		self.medText.SetText(backclr=u, just=None)
		x = self.medText.width
		self.medText.Resize(0,0)
		self.medText.DrawText(self.GetDeviceIp(), self.xUserData, self.yDeviceInfo)
		self.medText.Resize(x, 0)
		self.medText.SetText(backclr=self.BackColor, just=IoBox.JUST_RIGHT)

	def DrawWhichAxis(self) :
		''' draw the axis '''
		self.medText.DrawText(self.whichAxis, self.xUserData, self.yAxisInfo)

	def DrawDesired(self) :
		''' draw the desired value '''
		if self.desiredMove == None :
			self.medText.DrawText('--', self.xUserData, self.yDesired)
		else :
			a = self.toEight(self.desiredMove)
			self.medText.DrawText(a, self.xUserData, self.yDesired)

	def DrawEnabledIcon(self) :
		''' draw something to show ticsize editing is disabled '''
		if self.Dial2Enabled :
			a = ' '
		else:
			a = '*'
		self.medText.SetText(just=IoBox.JUST_LEFT)
		self.medText.DrawText(a, self.xUnitPlus, self.ySpeedInfo)
		self.medText.SetText(just=IoBox.JUST_RIGHT)

	def HighltColor(self, axis) :
		return self.BackColor if (axis != self.whichAxis) else self.HighlightColor

	def DrawAxes(self) :
		self.bigLetters.SetText(backclr = self.HighltColor('X'))
		self.bigLetters.DrawText('X', self.xXYZ, self.yX)
		self.bigLetters.SetText(backclr = self.HighltColor('Y'))
		self.bigLetters.DrawText('Y', self.xXYZ, self.yY)
		self.bigLetters.SetText(backclr = self.HighltColor('Z'))
		self.bigLetters.DrawText('Z', self.xXYZ, self.yZ)

	def DrawStatics(self) :
		''' draw the labels '''
		# self.titleBox.SetText(just = None)
		self.titleBox.DrawText('Jog Screen', self.indent, self.yTitle)
		nets = 'Network: %s' % str(WLAN(STA_IF))
		self.medText.Resize(0,0)	# autosize this
		self.medText.SetText(just=None)
		self.medText.DrawText(nets, self.indent, self.yNet)
		self.DrawValues(100, 200.123, 432.789)
		self.medText.DrawText(('mm' if self.IsMetric else 'inch'), self.xXYZData + 12*self.bigWidth, self.yX)
		self.medText.DrawText('Axis', self.xUserInfo, self.yAxisInfo)
		self.medText.DrawText('Tic Size', self.xUserInfo, self.ySpeedInfo)
		self.medText.DrawText('Desired', self.xUserInfo, self.yDesired)
		self.xUserData = self.xUserInfo + self.medText.drawer.GetStringWidth('Tic Size') + 30
		medsize = self.medText.drawer.GetStringWidth('00000.00000')
		self.xUnitPlus = self.xUserData + medsize + 20 + self.medText.drawer.GetStringWidth('think')
		self.medText.DrawText(self.UnitStr, self.xUserData + medsize + 20, self.ySpeedInfo)
		self.medText.Resize(medsize, self.medText.font.height)
		self.medText.SetText(just=IoBox.JUST_RIGHT)
		self.DrawAxes()
		self.DrawWhichAxis()
		self.DrawTicsize()
		self.DrawDesired()
		self.DrawDevice()

	def Setup(self) :
		''' draw the base screen and set up variables '''
		self.Dial2Enabled = True
		self.ClearScreen()
		# font info and io boxes
		self.titleBox = self.MakeIoBox('fontArial28')
		self.titleBox.SetText(just=IoBox.JUST_CENTER)
		self.bigNumbers = self.MakeIoBox('fontLucida40')
		self.bigLetters = self.MakeIoBox('fontLucida40')
		self.medText = self.MakeIoBox('fontArial22')
		self.bigWidth = self.bigNumbers.drawer.GetStringWidth('0')
		self.bigNumbers.SetText(cached = True, just = IoBox.JUST_RIGHT)
		self.bigNumbers.Resize(10*self.bigWidth, self.bigNumbers.font.height)
		# now decide on position stuff
		self.yTitle = 10
		self.yNet = self.yTitle + self.titleBox.font.height + self.lspace
		self.yX = self.yNet + self.medText.font.height + 3*self.lspace
		self.yY = self.yX + self.bigLetters.font.height + self.lspace
		self.yZ = self.yY + self.bigLetters.font.height + self.lspace
		self.xXYZ = self.indent*3
		self.xXYZData = self.xXYZ + 35

		self.xUserInfo = self.indent
		self.yAxisInfo = self.yZ + self.bigLetters.font.height + self.lspace*2
		self.ySpeedInfo = self.yAxisInfo + self.medText.font.height + self.lspace*2
		self.yDesired = self.ySpeedInfo + self.medText.font.height + self.lspace*2
		self.yDeviceInfo = self.yDesired + self.medText.font.height + self.lspace*2

		self.whichAxis = 'X'
		self.ticSize = 1		# 1 mm
		self.ticValue = 0
		self.desiredMove = None
		self.checkTime = ticks_ms()

		self.DrawStatics()

	def GetDeviceIp(self) :
		s = None
		try :
			s = GlobalPico()['device']
			s = GlobalPico()[s]['ip']
		except Exception as e:
			print('dip: ' + str(e))
		finally:
			return s

	def UpdatePosition(self, data) :
		status = json.loads(data)
		self.Locn = status['pos']
		self.Mach = status['machine']
		posn = self.Locn
		self.DrawValues(posn[0], posn[1], posn[2])
		if self.showMachine :
			posn = self.Mach
			self.DrawMachine(posn[0], posn[1], posn[2])

	def _parseStatus(self) :
		''' send and parse the result of an RRF status request'''
		print('request rr_status')
		try :
			u = None
			uText = ''
			s = self.GetDeviceIp()
			if s is not None :
				u = urequests.get(s + '/rr_status')
				# await WebQ().AddPacket('rr_status', 0)
				# u = await WebQ().GetResponse(1500)
				if u is not None :
					uText = u.text
					u.close() # required for mem cleanup
					self.UpdatePosition(uText)
		except Exception as e:
			print('pst: ' + s + '  ' + str(e) + uText)

	def _SendGoTo(self, axis, position) :
		''' send and parse the result of an RRF status request'''
		# move in mm?
		gcode = '/rr_gcode?gcode=G0' + axis + str(position)
		print('gcode = %s' % gcode)
		try :
			s = self.GetDeviceIp()
			if s is not None :
				# await WebQ().AddPacket(gcode, 0)
				# u = await WebQ().GetResponse(1500) # wait for ok ?
				u = urequests.get(s + gcode)
				if u is not None :
					self.UpdatePosition(u.text)
					u.close() # required for mem cleanup
		except Exception as e:
			print('goto: ' + str(e))


	def HandleDial1(self) :
		''' set location by rotary and units of measure via button'''
		# switch to metric if clicked down
		u = self.Dial1.ButtonClicked
		# swap on click only
		if u :
			if self.showMachine == False :
				self.showMachine = True
				psn = self.Mach
				self.DrawMachine(psn[0], psn[1], psn[2])
			else :
				self.showMachine = False
				self.didCheck = True
				GlobalPico()['units'] = ('i' if self.IsMetric else 'm')
				self.ClearScreen()
				self.DrawStatics()

		# read position
		u = self.Dial1.Position
		if u != self.lastDial1Pos and self.dialEdit == 'T':
			if u == 0 :
				newtic = None
			else:
				newtic = self.ticSize * self.Dial1.Position + self.currentPos # use maybe newer dial1
			if newtic != self.desiredMove :
				# self.didCheck = True
				self.desiredMove = newtic
				self.DrawDesired()
				u = ticks_ms()
				self.moveTime = ticks_add(u, 300)
				self.checkTime = ticks_add(u, 1000)
		self.lastDial1Pos = self.Dial1.Position

	def HandleDial2(self) :
		# disable on button
		u = self.Dial2.ButtonClicked
		# swap on click only
		if u :
			if self.dialEdit == 'T' :
				# if self.Dial2Enabled :
				self.Dial2Enabled = not self.Dial2Enabled
				if self.Dial2Enabled :
					self.Dial2.Position = self.ticValue
			self.didCheck = True
			self.DrawTicsize()
			self.DrawEnabledIcon()

		po = self.Dial2.Position
		if po != self.lastDial2Pos :
			if self.dialEdit == 'T' :	# tic size
				if not self.Dial2Enabled :
					return
				p1 = min(14, max(0, po))
				if p1 != po :
					self.Dial2.Position = p1
					self.lastDial2Pos = p1
				if p1 != self.ticValue :
					self.ticValue = p1
					decade = int(p1 / 3) # so 0...4
					maxval = 10 if self.IsMetric else 25.4
					newtic =  maxval * (10 ** (decade - 4)) * [1,2,5][p1 - decade * 3] # in mm
					self.didCheck = True
					self.ticSize = newtic # in mm
					self.DrawTicsize()
					self.Dial1.Position = 0
					self.desiredMove = None
					self.DrawDesired()
			elif self.dialEdit == 'D' :	# device
				devices = GlobalPico()['devices']
				p1 = po % 3
				if devices[p1] != GlobalPico()['device'] :
					GlobalPico()['device'] = devices[p1]
					self.DrawDevice()
					self.didCheck = True
					self.Dial1.Position = 0
					self.lastDial1Pos = 0
					self.desiredMove = None
					self.DrawDesired()
			elif self.dialEdit == 'B' : # brightness
				p1 = min(20, max(0, po))
				if p1 != po :
					self.Dial2.Position = p1
				if self.Brightness != p1 :
					GlobalLcd().set_brightness(5 * p1)
					self.Brightness = p1
		self.lastDial2Pos = po


	def HandleSwitch(self) :
		u = self.Switch.Switch
		if u >= 0 and u <= 2 :
			amm = 'XYZ'[u]
			if amm != self.whichAxis :
				self.didCheck = True
				self.whichAxis = amm
				self.DrawWhichAxis()
				self.DrawAxes()
				self.Dial1.Position = 0

	def HandleTouch(self) :
		if not self.Dial2Enabled :
			return
		u = ticks_ms()
		tch = GlobalLcd().touch_get(True) # touchdown, downx, downy, touchx, touchy
		if ticks_diff(u, self.WhenTouch) > 500 :
			if tch[1] != self.LastTouch[1] or tch[2] != self.LastTouch[2] :
				# moved
				self.WhenTouch = ticks_ms()
				if self.dialEdit == 'B' :
					self.dialEdit = 'T'
					self.Dial2.Position = GlobalPico()['devices'].index(GlobalPico()['device'])
				elif self.dialEdit == 'T' :
					self.dialEdit = 'D'
					self.Dial2.Position = self.ticValue
				elif self.dialEdit == 'D' :
					self.dialEdit = 'B'
					self.Dial2.Position = self.Brightness
				self.didCheck = True
				self.LastTouch = tch
				self.DrawTicsize()
				self.DrawDevice()
		else :
			self.LastTouch = tch

	def Loop(self) :
		self.Dial1.Position = 0
		self.Dial2.Position = 0
		self.didCheck = False
		self.checkTime = ticks_ms()
		self.moveTime = ticks_ms()
		self.currentPos = 0
		self.doRun = True

		''' do a control loop responding to stuff '''
		while self.doRun :
			# on timer request send to web
			if self.desiredMove != None and ticks_diff(self.moveTime, ticks_ms()) < 0 :
				if self.desiredMove != self.currentPos : # do a move
					self._SendGoTo(self.whichAxis, self.desiredMove) # in mm
					self.desiredMove = None # don't keep trying...
					u = ticks_ms()
					self.checkTime = ticks_add(u, 1000)
					self.moveTime = ticks_add(u, 300)

			# only check position if we're in usual move mode
			if self.dialEdit=='T' and ticks_diff(self.checkTime, ticks_ms()) < 0 :
					self._parseStatus()		# update x,y,z
					if self.desiredMove is None :
						self.currentPos = self.Locn[self.AxisIdx]
						self.Dial1.Position = 0
					self.DrawDesired()
					u = ticks_ms()
					self.checkTime = ticks_add(u, 1000)
					self.moveTime = ticks_add(u, 200) # can move now

			self.HandleDial2()	# dial2 is the tic size and device

			self.HandleDial1()	# dial 1 is the location

			self.HandleSwitch()	# switch for axis

			self.HandleTouch() # check the touchscreen

			# if something changed, don't send to web for a bit
			if self.didCheck :
				self.checkTime = ticks_add(ticks_ms(),1000)
				self.didCheck = False

			u = self.Dial1.ButtonState
			if u and u == self.Dial2.ButtonState :
				self.doRun = False	# quit this

	def CleanUp(self) :
		''' do any cleanup '''
		pass

