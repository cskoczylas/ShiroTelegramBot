from protocol import TPLinkSmartHomeProtocol
from typing import Optional, Dict, Tuple

text1 = "smartlife.iot.smartbulb.lightingservice"
text2 = "transition_light_state"

class SmartBulb(object):
	def __init__(self,
		     	 host: str,
		     	 protocol: 'TPLinkSmartHomeProtocol' = None) -> None:
		#creating new SmartBulb instance
		self.host = host
		if not protocol:
			protocol = TPLinkSmartHomeProtocol()
		self.protocol = protocol

	def _query_helper(self,
			  		  target: str,
			  		  cmd: str,
			  		  arg: Optional[Dict] = None) -> None:
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

	def state(self, bulb_state: str) -> None:
		#Turn the bulb ON or OFF
		if bulb_state == 'ON':
			new_state = 1
		else:
			new_state = 0
		light_state = {"on_off": new_state,}
			
		self._query_helper(text1, text2, light_state)		 

	def switch_state(self) -> None:
		#Switches bulb ON if OFF and vice versa
		lightState = self._query_helper(text1, "get_light_state")
		if lightState['on_off']:
			self.state('OFF')
		else:
			self.state('ON')

	def brightness(self, brightness: int) -> None:
		#Sets the brightness [0: 100]
		light_state = {"brightness": brightness,}
		
		self._query_helper(text1, text2, light_state)

	def color_temp(self, temp: int) -> None:
		#sets color temperature of bulb [2500: 9000k]
		light_state = {"color_temp": temp,}

		self._query_helper(text1, text2, light_state)

	def rgb(self, rgb: Tuple[int, int, int]) -> None:
		#RGB -> HSV then set color
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

		#print("{} {} {}".format(h, s, v))

		light_state = {
			"hue": h,
			"saturation": s,
			"brightness": int(v * 100 / 255),
			"color_temp": 0
			}

		self._query_helper(text1, text2, light_state)
