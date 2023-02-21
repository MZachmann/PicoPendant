from network import WLAN, STA_IF
from util.picoPendant import GlobalPico
from util import networkSta

# this is the primary wifi connect 'application'
# the GlobalPico object must be initialized before this

# connect to the wifi
wlan = WLAN(STA_IF)
wlan.active(True)

info = GlobalPico()
wlan.connect(info['wlan_ssid'], info['wlan_password'])

# this could never connect, so don't check
print(wlan.ifconfig())
# clean ram
info = None
wlan = None
del info
del wlan

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
