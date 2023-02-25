# an object for drawing characters created from TrueType
# given a font this creates a lookup table to the character metadata

from fonts.typeFont import TypeFont

# fontdrawers are large and ioboxes have one, so cache them instead
FontDrawerSet = {}

# a simple struct to convert indexes to names
class Datum() :
    def __init__(self, value) :
        self.TheChar = value[0]     # the character number
        self.Xpos = value[1]        # the X position in the font image
        self.Width = value[2]       # the Width of the glyph in pixels
        self.Offset = value[3]      # the offset of the glyph start in the box
        self.Advance = value[4]     # amount to move after drawing

# so we can cache font drawers
def GetFontDrawer(font, oled) :
    global FontDrawerSet
    if font in FontDrawerSet.keys() :
        return FontDrawerSet[font]
    FontDrawerSet[font] = FontDrawer(font, oled)
    return FontDrawerSet[font]

# the class that draws characters to an Oled display
# on init it creates a lookup table to the font metadata by character
class FontDrawer(object) :
    def __init__(self, font, oled ) :
        self.font : TypeFont = font
        self.oled = oled
        self.chartodata = { }
        numdata = len(font.info)
        for i in range(0, numdata) :
            self.chartodata[font.info[i][0]] = i
        # get N space
        self.emWidth = font.info[self.chartodata[78]][4]
        # print("We have " + str(len(font.data)) + " data points and " + str(len(self.chartodata)) + " datums.")

    # draw a single character to the display
    # this is not optimized at all
    # note theChar is an int (encode('UTF-8'))
    def DrawChar(self, theChar, xpos, ypos, colors, buffer = None) :
        if theChar == 32 : # space character
            return self.emWidth
        if not theChar in self.chartodata.keys() :
            return 0
        idx = self.chartodata[theChar]
        advance = 0
        if idx :
            c = Datum(self.font.info[idx])      # give the entries names
            width = c.Width
            advance = c.Advance
            for y in range(0, self.font.height) :
                # of bits offset (width is in bytes)
                offset = c.Xpos
                starty = ypos + y
                # there are better ways to do this
                for x in range(0, width) :
                    uoff = offset + x
                    bittwid = uoff - 8 * int(uoff/8)
                    bitoff = int(uoff/8) + y * self.font.width
                    bitv = (self.font.data[bitoff] & (0x80 >> bittwid)) != 0
                    if( bitv) :
                        startx = xpos + c.Offset + x
                        if buffer == None :
                            self.oled.draw_point(startx, starty, colors)
                        else :
                            buffer.pixel(startx, starty, colors)
            # print('Draw char %s at (%d,%d)' % (theChar, xpos, ypos))
        return advance

    # get the actual pixel width of a string
    def GetStringWidth(self, text) :
        tbt = text.encode('UTF-8')
        total = 0
        for theChar in tbt:
            if theChar == 32 : # space character
                advance = self.emWidth
            elif not theChar in self.chartodata.keys() :
                advance = 0
            else:
                idx = self.chartodata[theChar]
                advance = 0
                if idx :
                    c = Datum(self.font.info[idx])      # give the entries names
                    advance = c.Advance
            total = total + advance
        return total

    # draw a string to the display using the metadata
    # for positioning
    def DrawString(self, text, xpos, ypos, colors, buffer = None) :
        tbt = text.encode('UTF-8')
        xnow = xpos
        ynow = ypos
        for chars in tbt :
            move = self.DrawChar(chars, xnow, ynow, colors, buffer = buffer)
            xnow += move            

