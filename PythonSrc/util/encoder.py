#    Support for the Arduino Rotary Encoder
#               MZ Jan 2023
#
#    This has 3 pins. 
#      Sw = momentary push button column
#      Dt, Clk are A,B of an encoder and randomly labeled
#    the Dt, Clk lines go low between clicks
#
#    PicoPendant port settings-> (the GPnn pin numbers)
#     IN0 = 4,3,2
#     IN1 = 21,7,6
#     IN2 = 18,19,20 (Clk, Dt, Sw)
#
#    x = EncoderSw(port, usePullups = False)
#
#    This encoder code is interrupt driven for performance reasons
#    it's easy to add a callback for on-change if desired
# -----------------------------------------------------------
#
# Properties
#
#     ButtonState - true or false, read-only (immediate)
#     Position - integer + == clockwise pips, settable, interrupt driven

from machine import Pin

class EncoderSw :
	'''This class supports a 5-pin arduino Encoder
	Pin numbers = GPxx number
	Since there are three ports, this uses port # as input
	'''
	def __init__(self, whichPort, usePullups = False) :
		PinSets = [[4,3,2],[21,7,6],[18,19,20]] # port pins
		self._Lastvalue = 0
		# the usual encoder card has pullups on it but doesn't really need them or power
		# it's just a wiper switch
		whom = PinSets[whichPort]
		if usePullups:
			self._ClkPin = Pin(whom[0], Pin.IN, Pin.PULL_UP)
			self._DtPin =  Pin(whom[1], Pin.IN, Pin.PULL_UP)
			self._SwPin =  Pin(whom[2], Pin.IN, Pin.PULL_UP)
		else:
			self._ClkPin = Pin(whom[0], Pin.IN)
			self._DtPin =  Pin(whom[1], Pin.IN)
			self._SwPin =  Pin(whom[2], Pin.IN)
		# when clk changes update the position
		self._ClkPin.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=self.handle_interrupt)
		self._SwPin.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_switch)
		self._Position = 0		# initial position at start
		self._Clicked = False
	
	def handle_interrupt(self, pin):
		'''The interrupt handler for the Clock line. 
		increment if clock != data else decrement'''
		v = self._ClkPin.value()
		u = self._DtPin.value()
		# if we lost a step, this won't be right so just ignore the click
		if v != self._Lastvalue:
			delta = (1 if (v != u) else -1)
			self._Position = delta + self._Position
			self._Lastvalue = v
			#print(self._Position)

	def handle_switch(self, pin):
		'''The interrupt handler for the Clock line. 
		increment if clock != data else decrement'''
		self._Clicked = True

	# ButtonClicked = true if button was clicked since last check
	@property
	def ButtonClicked(self, reset = True) :
		x = self._Clicked
		if reset :
			self._Clicked = False
		return x

	# ButtonState = true if button is pressed (0 == down)
	@property
	def ButtonState(self) :
		return self._SwPin.value() == 0

	# Position tracks the number of clicks clockwise (+) or counterclockwise (-)
	# this is quadrature so ignore half-steps since they have no physical stop
	@property
	def Position(self) :
		return int(self._Position/2)

	@Position.setter
	def Position(self, pos) :
		self._Position = 2*pos


