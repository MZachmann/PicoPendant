from display.ioBox import IoBox
from display.lcdDriver import GlobalLcd, LCD_3inch5
from util.encoder import EncoderSw
from util.ladderSw import LadderSw
from util.picoPendant import GlobalObjects
from display.colorSet import SolidClr
from network import WLAN, STA_IF

# simply demo code

def ShowDemo() :
	lspace = 4
	
	oled : LCD_3inch5 = GlobalLcd()
	oled.set_brightness(70)
	oled.draw_filled_box(0, 0, oled.displayWidth, oled.displayHeight, SolidClr['darkgreen'])

	fnt = GlobalObjects()['fontArial11']
	fnt2 = GlobalObjects()['fontArial28']
	ibxl  = IoBox(oled, fnt2)
	ibx  = IoBox(oled, fnt)

	yBase = lspace

	ibxl.SetText('Pico Pendant V1.00', SolidClr['white'], SolidClr['darkgreen'], IoBox.JUST_CENTER)
	ibxl.Draw(0, yBase)
	yBase = yBase + fnt2.height + lspace

	ibxl.SetText('for Duet3d', SolidClr['white'], SolidClr['darkgreen'], IoBox.JUST_CENTER)
	ibxl.Draw(0, yBase)
	yBase = yBase + fnt2.height + lspace*3

	ibx.SetText('Network: %s' % str(WLAN(STA_IF)), SolidClr['red'], SolidClr['darkgreen'])
	ibx.Draw(20, yBase)
	yBase = yBase + fnt.height + lspace

	LCD = oled._MyFrame
	LCD.fill(SolidClr['black'])
	display_color = SolidClr['darkgreen'] << 1
	bsize = (int)(oled.width / 10)
	for i in range(0,12):      
		LCD.fill_rect(i*bsize, 0, bsize, oled.height, (display_color))
		display_color = display_color << 1
	oled.show_area(0, yBase, oled.width-1, yBase + oled.height-1)
	yBase = yBase + oled.height + lspace

	ibxNumber : IoBox = IoBox(oled, fnt2)
	ibxNumber.SetText( '0', SolidClr['black'], SolidClr['darkgreen'])
	#ibxNumber.Draw(90, yBase)
	yBase = yBase + fnt2.height + lspace

	ibxNumb2 : IoBox = IoBox(oled, fnt)
	ibxNumb2.SetText( '0', SolidClr['red'], SolidClr['darkgreen'])
	#ibxNumb2.Draw(90, yBase)
	yBase = yBase + fnt2.height + lspace

	esw = EncoderSw(2)
	esw1 = EncoderSw(1)
	esLast = 0
	esbLast = False
	es1Last = 0
	esb1Last = False
	lsw = LadderSw(0, [6.7,13.5,20.3,27,31.75,37])
	lsLast = 0

	yline2 = yBase + fnt2.height + lspace
	yline3 = yline2 + fnt2.height + lspace
	ewidth = 10 + (int)(ibxNumber.drawer.GetStringWidth('Encoder 1'))
	numwidth = 10 + (int)(ibxNumber.drawer.GetStringWidth('9999'))
	e2offset = 240
	xdlast = 0
	ydlast = 0
	ibxNumber.SetText('Encoder 1', SolidClr['white'])
	ibxNumber.Draw(10, yBase)
	ibxNumber.SetText('Encoder 2')
	ibxNumber.Draw(e2offset, yBase)
	ibxNumber.SetText('LadderSw')
	ibxNumber.Draw(10, yline2)
	ibxNumber.SetText('Touch At')
	ibxNumber.Draw(10, yline3)

	while True :
		p = esw.Position
		b = esw.ButtonState
		if p != esLast  or b != esbLast:
			ibxNumber.SetText(str(p) + '  ', (SolidClr['white'] if b else SolidClr['red']))
			ibxNumber.Draw(ewidth+5, yBase)
			esLast = p
			esbLast = b

		p = esw1.Position
		b = esw1.ButtonState
		if p != es1Last  or b != esb1Last:
			ibxNumber.SetText(str(p) + '  ', (SolidClr['white'] if b else SolidClr['red']))
			ibxNumber.Draw(ewidth+e2offset + 5, yBase)
			es1Last = p
			esb1Last = b

		lst = lsw.Switch
		if lst != lsLast :
			ibxNumber.SetText(str(lst) + '  ', SolidClr['white'])	
			ibxNumber.Draw(ewidth+5, yline2)
			lsLast = lst
			if lst == 1:
				break

		xtg = oled.touch_get() # 
		xd = int(xtg[1])
		yd = int(xtg[2])
		if xd != xdlast or yd != ydlast :
			ibxNumber.SetText('%d,%d    ' % (xd, yd))
			ibxNumber.Draw(ewidth+5, yline3)
			xdlast = xd
			ydlast = yd


def ShowFontFiles() :
	lspace = 4
	
	oled = GlobalLcd()
	oled.set_brightness(70)
	oled.draw_filled_box(0, 0, oled.displayWidth, oled.displayHeight, SolidClr['darkgreen'])

	fntList = GlobalObjects()['fontList']
	ypos = 10
	xpos = 20

	for fntName in fntList :
		fnt = GlobalObjects()[fntName]
		ibx = IoBox(oled, fnt)
		ibx.SetText('Big Thinker', SolidClr['white'])
		ibx.Draw(xpos, ypos)
		ypos += fnt.height + lspace

