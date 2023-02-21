# This is a CPython app for converting fonts
# includes a set of functions to convert from a bitmap image and fnt to
# C++ compatible data streams for use by LargeFont
# edit the last four lines of code to set file location/name
# see here: https://medium.com/home-wireless/convert-truetype-to-bitmap-for-use-by-c-9dd8196e5c94
import png

# -------------------------------------------------------
# read the png file, crop it and write it out as hex
#   remove the black lines top and bottom
#   crop any black vertical byte-lines from the right
#   then write the output as hex with one line header
# -------------------------------------------------------
def ClipPng(font) :
	img = png.Reader(Basepath + font + '_0.png')
	height,width,imgmap,imgmeta = img.asDirect()
	imgdata = [pi for pi in imgmap] # pixel data as array of arrays of pixel values (bytes)
	bitdata = []
	# convert pixel bytes into bit data
	imglen = len(imgdata)
	for i in range(imglen) :
		bitline = []
		bitval = 0x80
		bitout = 0
		for j in range(len(imgdata[i])) :
			if(imgdata[i][j]) :
				bitout = bitout | bitval
			bitval = bitval >> 1
			if(0 == bitval) :
				bitline.append(bitout)
				bitval = 0x80
				bitout = 0
		# leftover data?
		if(bitval != 0x80) :
			bitline.append(bitout)
		bitdata.append(bitline)
	#
	# now bitdata is the imgdata but as bits with the last byte rounded up
	fndx = -1;
	# crop top and bottom that have no data
	for i in range(imglen) :
		x = [im for im in bitdata[i] if im != 0] # find non-zero elements
		if(len(x)>0) :
			fndx = i
			break
	#
	for i in range(imglen) :
		x = [im for im in bitdata[imglen-i-1] if im != 0] # find non-zero elements
		if(len(x)>0) :
			fndendx = imglen-i
			break
	#
	imgfnd = bitdata[fndx:fndendx] # these lines have data
	# find the byte to clip at on the right. keep the left
	imglen = len(imgfnd)
	maxx = 0;
	for i in range(imglen) :
		rowlen = len(imgfnd[i])
		for j in range(rowlen) :
			if(imgfnd[i][rowlen-j-1] != 0) :
				if(maxx < rowlen-j) :
					maxx = rowlen-j
				break
	#
	# clip on the right and create a flat stream of bytes
	imgstream = []
	for i in range(imglen) :
		imgstream.extend(imgfnd[i][0:maxx])
	#
	# finally we have the clipped data, write it out to file as hex data
	outp = open(Basepath + font + '_0.hex', 'w')
	outp.write('// Image Size: ' + str(maxx) + 'bytes x ' + str(imglen) + 'lines\n')
	outp.write('{\n')
	idh = ['0x'+'%02x' % x + ',' for x in imgstream]
	for i in range(len(idh)-1) :
		outp.write(idh[i])
		if(0 == (1+i)%8) :
			outp.write('\n')
	# write last one without comma
	ido = '0x'+'%02x' % imgstream[len(idh)-1]
	outp.write(ido)
	outp.write('\n};\n')
	outp.close()

# -------------------------------------------------------
# convert the fnt file to a list of structures (.info)
# -------------------------------------------------------
def FntToInfo(font) :
	textdesc = open(Basepath + font + '.fnt','r')
	textdout = open(Basepath + font + '.info', 'w')
	dlines = textdesc.readlines()
	textdesc.close()
	dlines = dlines[4::] # remove header stuff
	textdout.write('{ ')
	for i in range(len(dlines)) :
		if dlines[i].find('kerning') != -1 :
			break
		x = dlines[i].split('=') # one line split by equals
		textdout.write('{ ' + x[1].split(' ')[0] + ', ')
		textdout.write(x[2].split(' ')[0] + ', ')
		textdout.write(x[4].split(' ')[0] + ', ')
		textdout.write(x[6].split(' ')[0] + ', ')
		textdout.write(x[8].split(' ')[0] + '}, \n')
	#
	textdout.write('{ 0,0,0,0,0} }\n')
	textdout.close()

# This requires a variable named font, which is the font name font='Arial11'
Basepath = '/users/mark/Downloads/'
font = 'Lucida40'
ClipPng(font)
FntToInfo(font)