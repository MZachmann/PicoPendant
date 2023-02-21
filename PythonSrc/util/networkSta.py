# connect to the local wifi network
#               MZ Jan 2023
#
#   METHODS
#
# StaStart - start up the wifi and connect using saved settings
# StaWait - wait some seconds for connection to happen
# StaStop - disconnect and stop the wifi
#
# so we can segue to an AP if unable to find a network
#
from network import WLAN, STA_IF
from util.picoPendant import GlobalPico
from utime import ticks_ms, sleep_ms

def StaStart() :
	''' define and start the Access Point '''
	# Set WiFi access point name (formally known as SSID) and WiFi channel
	wlan = WLAN(STA_IF)
	wlan.active(True)
	# get ssid, password from global settings
	gls = GlobalPico()
	wlan.connect(gls['wlan_ssid'], gls['wlan_password'])

def StaStop() :
	''' turn off the Access Point'''
	wlan = WLAN(STA_IF)
	if wlan.isconnected():
		wlan.disconnect()
	if wlan.active():
		wlan.active(False)

def StaWait(maxtimems) :
	''' wait some amount of time for a connection, return success/fail '''
	tuntil = ticks_ms() + maxtimems
	wlan = WLAN(STA_IF)
	while ticks_ms() < tuntil and not wlan.isconnected():
		sleep_ms(100)
	return wlan.isconnected()