# this is a torturous bit of code intended to maximize heap storage usage
# the fonts and globalobjects are large chunks of ram as is the lcd so they are all
# allocated first
# then the network is connected
try:
	from util.picoPendant import GlobalObjects
	# initialize some storage
	GlobalObjects().Initialize()
	from fonts import fontCache
	from display.lcdDriver import GlobalLcd
	# initialize more storage now
	fontCache.FontCache().OccupyFontCache(GlobalObjects(), GlobalLcd())
	# finally connect
	from web import wifiConnect
except Exception as e:
	print(str(e))
	
