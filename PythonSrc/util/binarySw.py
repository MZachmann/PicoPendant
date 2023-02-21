#    Support for a binary (on/off) switch
#               MZ Jan 2023
#
#    This code is interrupt driven for performance reasons
#    it's easy to add a callback for on-change if desired
# -----------------------------------------------------------
#
# Properties
#
#     State - true or false, read-only

from machine import Pin

class BinarySw :
	'''This class supports a 2 pin ladder sw
	Port number = adc port and 
	the ladder passed in is an approximate list of total resistance values
	the reference pullup resistor is 10K here
	'''
	def __init__(self, whichGpPin, usePullup = True) :
		self.numAverage = 3 		# average 3 readings?
		if usePullup:
			self._Pin = Pin(whichGpPin, Pin.IN, Pin.PULL_UP)
		else
			self._Pin = Pin(whichGpPin, Pin.IN)

	@property
	def State(self) :
		''' the raw ADC reading, maybe averaged '''
		total = 0
		for i in range(self.numAverage):
			total = self._Pin.value()
		return 1 == round(total / self.numAverage)

