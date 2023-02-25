# an iobox is the basic thing drawn on-screen for lack of more sophisticaed stuff
# it has text, a font, and colors
# optional rectangle and justification
from fonts.fontDrawer import GetFontDrawer
from fonts.typeFont import TypeFont

class IoBox() :

	JUST_LEFT = 0
	JUST_RIGHT = 1
	JUST_CENTER = 2

	def __init__(self, oled, font, width=0, height=0, xpos=0, ypos=0, just=None, cached=False) :

		self.height : int = height
		self.width : int = width
		self.text : str = 'none'
		self.xpos : int = xpos
		self.ypos : int = ypos
		self.foreColor : int = 0
		self.backColor : int = 0
		self.font : TypeFont = font
		self.drawer = GetFontDrawer(self.font, oled)
		self.oled = oled
		self.justification = just
		self.usecache = cached

	def SetText(self, text=-1, foreclr=None, backclr=None, just=-1, cached=None) :
		if text != -1 :
			self.text = text
		if foreclr != None :
			self.foreColor = foreclr
		if backclr != None :
			self.backColor = backclr
		if just != -1:
			self.justification = just
		if cached != None:
			self.usecache = cached

	def Resize(self, w=-1, h=-1) :
		if w >= 0 :
			self.width = w
		if h >= 0 :
			self.height = h

	def Draw(self, xpos, ypos) :
		self.xpos = xpos
		self.ypos = ypos
		self.Draw()

	def DrawText(self, text, xp=-1, yp=-1) :
		self.text = text
		if xp != -1 :
			self.xpos = xp
		if yp != -1 :
			self.ypos = yp
		self.Draw()

	def Draw(self) :
		xoffset = 0
		xpos = self.xpos
		if self.justification is not None :
			xmax = (self.oled.displayWidth if self.width == 0 else self.width)
			xtotal = self.drawer.GetStringWidth(self.text)
			# print('Xmax = %d Xtotal = %d' % (xmax, xtotal))
			if self.justification == self.JUST_CENTER :
				if self.width == 0 :
					xpos = int((xmax - xtotal) / 2)
				else:
					xoffset = int((xmax - xtotal) / 2)
			elif self.justification == self.JUST_RIGHT :
				if self.width == 0 :
					xpos = xmax - xtotal
				else:
					xoffset = xmax - xtotal
		xoffset = int(xoffset)
		# here xoffset is the offset for the code to draw the chars in the buffer if justified
		# xpos,ypos is where to draw the chars on screen
		if not self.usecache :
			self.oled.draw_string_box(self.drawer, self.text, xoffset, xpos, self.ypos, self.width, self.height, self.foreColor, self.backColor)
		else:
			self.oled.draw_string_cached(self.drawer, self.text, xoffset, xpos, self.ypos, self.width, self.height, self.backColor)
