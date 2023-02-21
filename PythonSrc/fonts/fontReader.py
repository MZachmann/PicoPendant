# the provided font python files just take up too much RAM
# so this parser extracts the binary data without loading the python source
# modules

import ujson as json
from fonts.typeFont import TypeFont
import gc

def _parseEqual( txt, look) :
	''' get the assigned value '''
	rslt = 0
	u = txt.find(look)
	if u > 0 :
		ucr = txt.find('\r', u)
		if ucr < 0 :
			ucr = txt.find('\n', u)
		if ucr > 0 :
			rslt = int(txt[(u+len(look)) : ucr])
	# print('equal ' + str(rslt))
	return rslt

def ParseFontFile(filename:str) :
	height = 0
	width = 0
	aline = ''
	state = 0
	numchars = 0
	fontData = 'a'
	fontIndex = 'b'

	try :
		with open(filename) as o1:
			aline = o1.read()
			# get font height and width
			height = _parseEqual(aline, 'self.height =')
			width =  _parseEqual(aline, 'self.width =')

			# get the font info 
			u = aline.find('[ [')
			ub = aline.find('] ]', u)
			if u > 0 and ub > 0 :
				fontIndex = json.loads(aline[u:ub+3])
			else :
				fontIndex = None

			u = aline.find('bytes((', ub)
			ub = aline.find('))', u)

			subset = aline[u:ub+2]
			del aline
			gc.collect()
			fontData = eval(subset)
	except Exception as e:
		print('Exception' + str(e))
	finally:
		pass
	return TypeFont(fontIndex, fontData, width, height)
