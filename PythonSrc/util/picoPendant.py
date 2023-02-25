# application globals
#               MZ Jan 2023
#
# the GlobalPendant dictionary has the global settings
# along with load and save methods using a Json file in root
#
#      GlobalPico() - the global object
#   PicoPendant::
#      Initialize() - set defaults and load current settings
#      load() - read the Json configuration file
#      Save() - save the object to Json file
#
# The GlobalObjects dictionary contains loaded and cached stuff but not serialized
#		GlobalObjects() - the set of fonts, and caches
#
import ujson as json
from secrets_file import secrets
from fonts.fontReader import ParseFontFile
from display.colorSet import DarkTheme as Theme
from fonts.fontCache import FontCache
import gc

# local file name
JsonFile = 'config.json'

def GlobalPico() :
	global _GlobalPendant
	return _GlobalPendant

def GlobalObjects() :
	global _GlobalObjects
	return _GlobalObjects

class PicoObjects(dict):
	''' Global Data storage of loaded objects '''
	def Initialize(self) :
		print("Initializing")
		# font loading is the worst
		# we don't use the smaller lucidas so remove them for more storage
		#self['fontList'] = ['fontLucida40', 'fontLucida28', 'fontArial28', 'fontLucida22','fontArial22','fontArial11']
		self['fontList'] = ['fontLucida40', 'fontArial28', 'fontArial22']
		self.LoadFontFiles()
		self['theme'] = Theme
		# all the really big stuff gets allocated very early...
		try :
			self['dispBuffer'] = bytearray(480*32*2)
		except Exception as e:
			print(str(e))
		gc.collect()
		print('memory free after display bfr = %d' % (gc.mem_free()))
		FontCache().AllocateFontCache()

	def LoadFontFiles(self) :
		print('memory free before fonts = %d' % (gc.mem_free()))
		for fName in self['fontList'] :
			self[fName] = ParseFontFile('fonts/' + fName + '.py')
			gc.collect()
		print('memory free after fonts = %d' % (gc.mem_free()))

class PicoPendant(dict):
	''' Global Data Storage and serialization '''
	def _SetDefault(self) :
		self['ap_ssid'] = 'PicoPendant'
		self['ap_password'] = 'pendant1234'
		self['wlan_ssid'] = secrets['wlan_ssid']
		self['wlan_password'] = secrets['wlan_password']
		self['units'] = 'm' # 'i' or 'm'
		# hokie but useful
		self['devices'] = ['CNC', 'Mill', 'Printer', 'Null']  # all
		self['device'] = 'CNC'	# current
		self['token'] = ''
		self['CNC'] =		{ 'ip' : 'http://192.168.0.58', 'sbc' : 'N', 'pwd' : '' }
		self['Mill'] = 		{ 'ip' : 'http://192.168.0.53', 'sbc' : 'N', 'pwd' : '' }
		self['Printer'] = 	{ 'ip' : 'http://192.168.0.57', 'sbc' : 'N', 'pwd' : '' }
		self['Null'] = 	{ 'ip' : '0.0.0.0', 'sbc' : 'N', 'pwd' : '' } # dummy to not affect anything

	def Initialize(self) :
		'''setup the default settings and then load overrides and other settings'''
		self._SetDefault()
		# load any overrides & settings
		self.Load()

	def Save(self):
		'''save to JSon'''
		try:
			with open(JsonFile, 'w') as o1:
				json.dump(self, o1)
		except :
			print("save failed")

	def Load(self):
		'''load from JSon'''
		# clear() 
		try:
			data = None
			 # read the file and parse
			with open(JsonFile) as o1:
				data = json.load(o1)
			 # copy to self
			if data != None:
				for i in data.keys():
					# don't copy if we don't have this property any more
					if i in self.keys() :
						self[i] = data[i]
					else :
						print('skip load : ' + i)
			else:
				print('no data')
		except :
			print('open failed')

_GlobalPendant = PicoPendant()
_GlobalObjects = PicoObjects()

