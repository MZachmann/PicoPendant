#    Support for a laddersw
#               MZ Jan 2023
#
#    A ladder switch is a (rotary) switch where the contacts are all connected
#	together with resistors of similar value. When the center and the end are connected
#	to an ADC and dropping resistor the read value indicates the switch angle.
#	So, to start the two are connected, then R, then 2xR, then 3xR etc. The reading will be
#   Rtotal = nRlad where Rlad is each resistors impedance (more or less)
#   Vreading = Vref * Rtotal / (Rtotal + Rref)
#   or Rtotal = (Rtotal + Rref) * Vreading  / Vref
# 	Rtotal = Rtotal * Vreading / Vref + Rref * Vreading / Vref
# 	Rtotal * (1 - Vreading / Vref) = Rref * Vreading / Vref
#                       or
#   Rtotal = Rref * Vreading / (Vref * (1 - Vreading/Vref))
#         on the current board Rref = 10K
#
#    x = LadderSw(adcport, [values in k])
#            mine = 6.7, 13.5, 20.3, 27, 31.75, 36.5
#
# -----------------------------------------------------------
#
# Properties
#
#     Switch - integer + == clockwise pips, immediate so takes some resources to ADC

from machine import Pin, ADC

class LadderSw :
	'''This class supports a 2 pin ladder sw
	Port number = adc port and 
	the ladder passed in is an approximate list of total resistance values
	the reference pullup resistor is 10K here
	'''
	def __init__(self, whichPort, ladder) :
		self.numAverage = 3 		# average 3 readings?
		self.maxReading = 53661 	# empirical
		self._Ladder = ladder		# a list [r1, r1+r2, r1+r2+r3,...] of total resistance in KOhms
		self._channel = whichPort
		self._lastRead = 0

	@property
	def Switch(self) :
		''' the current reading as a switch position '''
		total = self.RValue 	# measure/calculate the resistance
		mindist = 3000			# allow a certain amount of error
		subtotal = 0
		best = -1
		#print('total sw = ' + str(total))
		# find the closest resistance in the ladder using abs
		for i in self._Ladder:
			ndist = abs(total - i * 1000)
			# print([total, ndist, i])
			if ndist < mindist:
				mindist = ndist
				best = i
		if best != -1 :
			self._lastRead = self._Ladder.index(best)
		#print('best sw = ' + str(best))
		return self._lastRead

	@property
	def RValue(self):
		''' the current reading as a resistance value '''
		a = self.RawValue
		mx = self.maxReading
		# Rtotal = Rref * Vreading / (Vref * (1 - Vreading/Vref))
		if a < mx:
			b = a / (mx * (1 - a/mx))
			total = 10000 * b	# Rreference
		else:
			total = 1000000		# random fail
		return total

	@property
	def RawValue(self) :
		''' the raw ADC reading, maybe averaged '''
		total = 0
		for i in range(self.numAverage):
			total = total + ADC(self._channel).read_u16()
		return total / self.numAverage

