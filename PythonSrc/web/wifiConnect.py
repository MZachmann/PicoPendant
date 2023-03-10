from network import WLAN, STA_IF
from util.picoPendant import GlobalPico
from util import networkSta
from time import sleep_ms

def doConnect(ssid) :
	wlan = WLAN(STA_IF)
	try :
		if wlan.active() :
			print("disconnecting")
			wlan.disconnect()
			wlan.active(False)
			sleep_ms(150)
	except Exception as e :
		print(str(e))

	try :
		wlan.active(True)
		gls = GlobalPico()
		idx = gls['wlan_ssids'].index(ssid)
		if idx >= 0 :
			pw = gls['wlan_passwords'][idx]
			print('conn %s %s' % (ssid,pw))
			wlan.connect(ssid, pw)
			gls['wlan_ssid'] = ssid
			sleep_ms(1000)
		else :
			print('ssid %s not found in list', ssid)
	except Exception as e :
		print(str(e))
	pw = None
	ssid = None
	# this could never connect, so don't check
	print(wlan.ifconfig())

# this is the primary wifi connect 'application'
# the GlobalPico object must be initialized before this

# connect to the wifi
doConnect(GlobalPico()['wlan_ssid'])

# -------------------------------------
# look to see if we've connected to a local network
# if not, enable the access point
# -------------------------------------
# x = networkSta.StaWait(3000)
# if not x:
# 	from util import networkAp
# 	networkSta.StaStop()	# just shut it down
# 	networkAp.ApStart()
# 	print("Starting AP")
