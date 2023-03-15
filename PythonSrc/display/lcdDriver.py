from machine import Pin,SPI,PWM
import framebuf
from utime import sleep_ms, sleep_us
from util.picoPendant import GlobalObjects
from fonts.fontCache import FontCache
from fonts.fontDrawer import FontDrawer
from machine import disable_irq, enable_irq

# --------------------------------------------------------------------------
# a small amount of support for the waveshare display Pico-ResTouch-LCD-3.5
# the display is 480x320 
# the pins for the display are defined by the hardware and fixed
# --------------------------------------------------------------------------

LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17

# a single instance is created when this file is imported
def GlobalLcd() :
    return _GlobalLcd

# the display class and some helpers
class LCD_3inch5():

    def __init__(self):
        # RGB565
        # self.RED   =   0x07E0
        # self.GREEN =   0x001f
        # self.BLUE  =   0xf800
        self.SLOWSPEED = 12_000_000
        self.HIGHSPEED = 64_000_000
        
        self.cs = Pin(LCD_CS, Pin.OUT)
        self.rst = Pin(LCD_RST, Pin.OUT)
        self.dc = Pin(LCD_DC, Pin.OUT)

        self.sck = Pin(LCD_SCK)
        self.mosi = Pin(LCD_MOSI)
        self.miso = Pin(LCD_MISO)
        
        self.tp_cs =Pin(TP_CS, Pin.OUT)
        self.irq = Pin(TP_IRQ, Pin.IN)
        self.irq.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_touch)
        self.inTouch = False

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        # empirically the Pico works at 64MHz and quite well but any power of 2 divisor here works
        # all the way down to 4MHz were tested
        # the high speeds work fine with the display but the touch needs a much slow spi
        # touch=4MHz, display=64MHz
        self.spi = SPI(1, self.HIGHSPEED, sck=self.sck, mosi=self.mosi, miso=self.miso) # , bits=8, polarity=1, phase=1

        self.touchX  = 0.0
        self.touchY  = 0.0
        self.downX  = 0.0
        self.downY  = 0.0
        self.touchDown = False

        self.bufheight = 32         # allocated amount of data
        self.bufwidth = 480
        self.displayWidth = 480     # physical display dimensions
        self.displayHeight = 320
        self.buffer = GlobalObjects()['dispBuffer'] # bytearray(self.bufwidth * self.bufheight * 2)
        self.set_frame_size(self.bufwidth, self.bufheight)  # default size
        self._pwm = PWM(Pin(LCD_BL))
        self._init_display()

    def _write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def _write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

    def _writeCommand(self, cmd, buf = None):
        self._write_cmd(cmd)
        if buf is not None:
            hf = len(buf)
            for i in range(0, hf):
                self._write_data(bytearray([buf[i]]))

    def _writeOne(self, cmd, buf):
        self._write_cmd(cmd)
        self._write_data(bytearray([buf]))

    def _init_display(self):
        '''Initialize display'''
        self.rst(1)
        sleep_ms(5)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(5)
        self._writeOne(0xC2,  0x33)     # Power Ctrl 3
        self._writeCommand(0xC5, b"\x00\x1e\x80") # VCom
        # self.writeCommand(0x20)       # display inversion off
        self._writeOne(0xB1, 0xB0)      # frame rate control - Fosc @ 68.36
        self._writeOne(0x36, 0x28)      # memory access control - rowcol exchange, BGR
        self._writeCommand(0x21)        # display inversion on
        self._writeCommand(0xE0, b"\x00\x13\x18\x04\x0f\x06\x3a\x56\x4d\x03\x0a\x06\x30\x3e\x0f") # gamma 1
        self._writeCommand(0xE1, b"\x00\x13\x18\x01\x11\x06\x38\x34\x4d\x06\x0d\x0b\x31\x37\x0f") # gamma 2
        self._writeOne(0X3A, 0x55)      # pixel format set 16 bpx 65K colors
        self._writeCommand(0x11)        # sleep off
        sleep_ms(120)
        self._writeCommand(0x29)        # display on
        self._writeCommand(0xB6, b"\x00\x62") # display function 
        self._writeOne(0x36, 0x28)      # memory access control - rowcol exchange, BGR

    def set_frame_size(self, w, h):
        ''' create a new FrameBuffer representing the desired rectangle
        but don't reallocate the base bytearray buffer '''
        self.width = w      # for purposes of graphic operations set the implied size
        self.height = h
        self._MyFrame = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        # print('completed %d x %d' % (self.width, self.height))
        
    def show_rect(self, block):
        ''' copy the framebuffer into a block, for testing '''
        xMin = 0
        yMin = block * self.height
        xMax = self.width - 1
        yMax = yMin + self.height - 1
        self.show_area(xMin, yMin, xMax, yMax)

    def show_area(self, xMin, yMin, xMax, yMax):
        ''' copy the framebuffer into a rectangular piece of the display '''
        xMin = int(xMin)
        xMax = int(xMax)
        yMin = int(yMin)
        yMax = int(yMax)
        # state = disable_irq() # given touch code issues this is probably necessary
        tos = [xMin>>8, xMin&0xff, xMax>>8, xMax&0xff]
        self._writeCommand(0x2A, bytearray(tos)) # col address
        tos = [yMin>>8, yMin&0xff, yMax>>8, yMax&0xff]
        self._writeCommand(0x2B,  bytearray(tos)) # row address
        self._write_cmd(0x2C)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self._MyFrame)
        self.cs(1)
        # enable_irq(state)

    def set_brightness(self, duty):
        ''' change the backlight brightness by altering a PWM pin '''
        self._pwm.freq(1000)
        if(duty>=100):
            self._pwm.duty_u16(65535)
        else:
            self._pwm.duty_u16((int)(65535*duty/100))

    def draw_point(self,x,y,color):
        self._MyFrame.pixel(x,y,color)

    def touch_get(self, clear=False) :
        ''' return [status, downX, downY, touchX, touchY], clear status if requested '''
        x = [self.touchDown, self.downX, self.downY, self.touchX, self.touchY]
        if clear :
            self.touchDown = False
        return x

    # we get an interrupt on move and on down and up
    def handle_touch(self, pin) :
        if self.inTouch :
            return
        self.inTouch = True
        xPoint = 0
        yPoint = 0
        if self.irq.value() == 0:
            self.downX = self.downX + 1 # so change downx because what else?
            self.touchDown = True
            # numAve = 3
            # # slow down the spi rate for the flash here
            # # ----------------------------------------------------------------
            # state = disable_irq() # turn off other interrupts during this garp stuff
            # # ----------------------or else we stop getting radio connections
            # self.tp_cs(0)
            # self.spi = SPI(1, self.SLOWSPEED, sck=self.sck, mosi=self.mosi, miso=self.miso) # , bits=8, polarity=1, phase=1

            # for i in range(0,numAve):
            #     self.spi.write(bytearray([0XD0]))
            #     Read_date = self.spi.read(2)
            #     sleep_us(10)
            #     xPoint=xPoint+(((Read_date[0]<<8)+Read_date[1])>>3)
                
            #     self.spi.write(bytearray([0X90]))
            #     Read_date = self.spi.read(2)
            #     sleep_us(10)
            #     yPoint=yPoint+(((Read_date[0]<<8)+Read_date[1])>>3)

            # xPoint=int(xPoint/numAve)
            # yPoint=int(yPoint/numAve)
            # self.spi = SPI(1, self.HIGHSPEED, sck=self.sck, mosi=self.mosi, miso=self.miso) # , bits=8, polarity=1, phase=1
            # self.tp_cs(1) 
            # # ------------------------------------------------------
            # enable_irq(state)

            # if (xPoint > 0 and xPoint < 4095 and yPoint > 0 and yPoint < 4095) :
            #     if not self.touchDown :
            #         self.downX = xPoint
            #         self.downY = yPoint
            #     self.touchX = xPoint
            #     self.touchY = yPoint
            #     self.touchDown = True
            # else:
            #     self.touchDown = False
        else:
            self.touchDown = False
        self.inTouch = False

    def draw_string_box(self, drawer : FontDrawer, text, toffset, x, y, width, height, txtColor, bkgdColor):
        ''' draw a string of the length required to fit it '''
        ulen = drawer.GetStringWidth(text)
        if width <= 0 :
            width = ulen
        w = width # 8 * (int)((7 + width)/8) # round this?
        w = min(w, self.bufwidth)
        h = (drawer.font.height if height <= 0 else height)
        self.set_frame_size(w, h)
        LCD = self._MyFrame
        LCD.fill(bkgdColor)
        drawer.DrawString(text, toffset, 0, txtColor)
        self.show_area(x, y, x + self.width-1, y + self.height-1)
        self.set_frame_size(self.bufwidth, self.bufheight)

    def draw_string_cached(self, drawer : FontDrawer, text, toffset, x, y, width, height, bkgdColor):
        ''' draw a string of the length required to fit it '''
        ulen = drawer.GetStringWidth(text)
        if width <= 0 :
            width = ulen
        w = width # 8 * (int)((7 + width)/8) # round this?
        w = min(w, self.bufwidth)
        h = (drawer.font.height if height <= 0 else height)
        self.set_frame_size(w, h)
        LCD = self._MyFrame
        LCD.fill(bkgdColor)
        fc = FontCache()
        # fc.DrawString(text, self.buffer, 0, 0, self.width * 2)
        offset = toffset
        for i in text :
            bfr = fc.GetCharBuffer(i)
            if bfr != None :
                frb = framebuf.FrameBuffer(bfr, 21, 34, framebuf.RGB565)
                LCD.blit(frb, offset, 0)
            offset = offset + 21
        self.show_area(x, y, x + self.width-1, y + self.height-1)
        self.set_frame_size(self.bufwidth, self.bufheight)

    def draw_filled_box(self, xpos, ypos, width, height, clr) :
        ''' draw a filled box of any size, possibly covering multiple blocks '''
        self._MyFrame.fill(clr)
        if height < self.height :
            self.show_area(xpos, ypos, xpos + width - 1, ypos + height - 1)
        else :
            hnow = 0
            while hnow < height :
                hend = hnow + min( (height-hnow), self.height)
                self.show_area(xpos, ypos + hnow, xpos + width - 1, ypos + hend - 1)
                hnow = hend

# the global object here
_GlobalLcd = LCD_3inch5()

