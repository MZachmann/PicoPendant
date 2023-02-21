# create an Access Point network
#               MZ Jan 2023
#
#   METHODS
#
#   APStart - start AP mode
#   ApStop - stop the AP mode
#

from network import WLAN, AP_IF
from util.picoPendant import GlobalPico

def ApStart() :
	''' start the Access Point
	get ssid, password from global settings '''
	gls = GlobalPico()
	ap = WLAN(AP_IF)
	# Set WiFi access point name (formally known as SSID) and WiFi channel
	ap.config(essid=gls['ap_ssid'], password=gls['ap_password'])
	ap.active(True)  
	while ap.active == False:
		pass

def ApStop() :
	''' turn off the Access Point'''
	ap = WLAN(AP_IF)
	if ap.active():
		ap.active(False)

