# A screen class
from util.picoPendant import GlobalObjects, GlobalPico
from display.lcdDriver import GlobalLcd
from display.ioBox import IoBox
from display.colorSet import SolidClr
from util import encoder, ladderSw

# pp_screen is the base class for screens


class pp_screen :

	def __init__(self) :
		self.encoder1 = encoder.EncoderSw(2)
		self.encoder2 = encoder.EncoderSw(1)
		self.switch1 = ladderSw.LadderSw(0, [6.7,13.5,20.3,27,31.75,37])

	@property
	def BackColor(self) :
		return GlobalObjects()['theme']['background']

	@property
	def TextColor(self) :
		return GlobalObjects()['theme']['foreground']

	@property
	def HighlightColor(self) :
		return GlobalObjects()['theme']['highlight']

	@property
	def IsMetric(self) :
		return GlobalPico()['units'] == 'm'

	@property
	def Dial1(self) :
		return self.encoder1

	@property
	def Dial2(self) :
		return self.encoder2
	
	@property
	def Switch(self) :
		return self.switch1

	def ClearScreen(self) :
		oled = GlobalLcd()
		oled.set_brightness(40) # testing...
		oled.draw_filled_box(0, 0, oled.displayWidth, oled.displayHeight, self.BackColor)

	def MakeIoBox(self, fontName) :
		ibx : IoBox = IoBox(GlobalLcd(), GlobalObjects()[fontName])
		ibx.SetText(foreclr=self.TextColor, backclr=self.BackColor)
		return ibx

	def Setup(self) :
		''' draw the base screen and set up variables '''
		pass

	def Loop(self) :
		''' do a control loop responding to stuff '''
		pass

	def CleanUp(self) :
		''' do any cleanup '''
		pass

