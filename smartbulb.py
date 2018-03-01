from protocol import TPLinkSmartHomeProtocol
from typing import Optional, Dict, Tuple


class SmartBulb(object):
	#simple text used for JSON queries to lightbulb
	cmd1 = "smartlife.iot.smartbulb.lightingservice"
	cmd2 = "transition_light_state"

	#creates a new SmartBulb instance
	def __init__(self,
		     	 host: str,
		     	 protocol: 'TPLinkSmartHomeProtocol' = None) -> None:
		self.host = host
		if not protocol:
			protocol = TPLinkSmartHomeProtocol()
		self.protocol = protocol

	def _query_helper(self,
			  		  target: str,
			  		  cmd: str,
			  		  arg: Optional[Dict] = None) -> None:
		"""
		sends a query of a JSON object using protocol.py
		protocol.query returns a JSON object
		"""
		if arg is None:
			arg = {}
		try:
			response = self.protocol.query(
				host = self.host,
				request = {target: {cmd: arg}}
			)
		except Exception as ex:
			pass
		return response[target][cmd]

	#turns the light ON or OFF
	def state(self,
			  bulb_state: str) -> None:
		if bulb_state == 'ON':
			new_state = 1
		else:
			new_state = 0
		light_state = {"on_off": new_state,}
			
		self._query_helper(self.cmd1, self.cmd2, light_state)		 

	#switches bulb ON if state is currently 'OFF' and vice versa
	def switch_state(self) -> None:
		#getting current state of light bulb
		lightState = self._query_helper(self.cmd1, "get_light_state")
		if lightState['on_off']:
			self.state('OFF')
		else:
			self.state('ON')

	#sets the brightness of the bulb from range [0: 100]
	def brightness(self,
				   brightness: int) -> None:
		light_state = {"brightness": brightness,}
		
		self._query_helper(self.cmd1, self.cmd2, light_state)

	#sets the color temperature of the bulb from range [2500: 9000]
	def color_temp(self,
				   temp: int) -> None:
		light_state = {"color_temp": temp,}

		self._query_helper(self.cmd1, self.cmd2, light_state)

	#takes in RGB tuple and converts it to HSV, the sets bulb color
	def rgb(self,
			rgb: Tuple[int, int, int]) -> None:
		#RGB -> HSV process
		r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
		mx = max(r, g, b)
		mn = min(r, g, b)
		diff = mx - mn
		if mx == mn:
			h = 0
		elif mx == r:
			h = (60 * ((g-b)/diff) + 360) % 360
		elif mx == g:
			h = (60 * ((b-r)/diff) + 120) % 360
		elif mx == b:
			h = (60 * ((r-g)/diff) + 240) % 360
		if mx == 0:
			s = 0
		else:
			s = (diff/mx) * 100
		v = (mx) * 100

		light_state = {
			"hue": h,
			"saturation": s,
			"brightness": int(v * 100 / 255),
			"color_temp": 0
			}

		self._query_helper(self.cmd1, self.cmd2, light_state)
