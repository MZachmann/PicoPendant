# cached chars for speeding things up
# this draws the digits into one buffer per digit
# so they can be blitted to the display


from fonts.fontDrawer import FontDrawer
from framebuf import FrameBuffer, RGB565
import gc

def FontCache() :
	global _fontCache
	return _fontCache

class FontCacher :
	def __init__(self) :
		self.IsOccupied = False
		self.bltChars = '0123456789.-'
		self.buffers = dict()
		self.xsize = 21	# from lucida40 direct
		self.ysize = 34

	def AllocateFontCache(self) :
		''' the character cache is big digit bitmaps for speed '''
		print("Allocating Font Cache")
		gc.collect()
		for i in self.bltChars:
			self.buffers[i] = bytearray(self.xsize * self.ysize * 2) # size of a char in bytes
		gc.collect()
		print('memory free after font cache = %d' % (gc.mem_free()))
		pass

	def OccupyFontCache(self, gls, gld) :
		''' put characters into the cache '''
		if not self.IsOccupied :
			self.IsOccupied = True
		# else:
		# 	return
		print("Occupying Font Cache")
		gc.collect()
		print('memory before cache chars = %d' % (gc.mem_free()))
		ff = FontDrawer( gls['fontLucida40'],  gld)
		fsize = ff.GetStringWidth('0') # constant width
		if self.xsize != fsize or self.ysize != ff.font.height :
			print("Invalid font size for font cache")
			print("expected %d,%d but found %d,%d" % (self.xsize, self.ysize, fsize, ff.font.height))
		# print('bltchars is ' + self.bltChars)
		tbt = self.bltChars.encode('UTF-8')
		for i in self.bltChars :
			# print('size is %d x %d' % (fsize, ff.font.height))
			buf = FrameBuffer( self.buffers[i], self.xsize, self.ysize, RGB565)
			buf.fill(gls['theme']['background'])
			ff.DrawChar((i.encode('UTF-8'))[0], 0, 0, 0xffff, buffer=buf)
		del ff
		gc.collect()
		# if we delete the lucida40 font now we save 12K ram...
		print('memory after cache chars = %d' % (gc.mem_free()))

	def GetCharBuffer(self, who) :
		if self.bltChars.find(who) >= 0 :
			return self.buffers[who]
		return None

	def DrawChar(self, who, destbuf, xpos, ypos, stride) :
		u = self.GetCharBuffer(who)
		if u is None :
			return
		
		offset = ypos * stride + xpos * 2 # byte offset to start of destination
		# now blit one buffer to another
		for i in range(0, self.ysize) :
			xo = offset + i * stride
			xi = i * self.xsize * 2 # offset of input
			destbuf[xo : xo + 2*self.xsize] = u[xi : xi + 2 * self.xsize]
			# for j in range(0, 2*self.xsize) :
			# 	# print('at %d x %d' % (xo+j, xi+j))
			# 	destbuf[xo+j] = u[xi+j]

	def DrawString(self, who, destbuf, xpos, ypos, stride) :
		for c in who :
			self.DrawChar(c, destbuf, xpos, ypos, stride)
			xpos += self.xsize # fixed size chars

_fontCache = FontCacher()
