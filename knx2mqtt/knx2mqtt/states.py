import logging

class states:

	def __init__(self):
		self._states = dict()


	def set_state(self, address, state):
		logging.debug("Set address {0}, state {1}".format(address, state))
		self._states[str(address)] = str(state)


	def is_state(self, address, state):
		logging.debug("Is address {0}, state {1}".format(address, state))
		return address in self._states and self._states[str(address)] == str(state)
