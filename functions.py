from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from random import randint
from typing import Any
import os, time, re

from discover import Discover
from smartbulb import SmartBulb
import config


#setting up directory path and moderator username
picPath = config.picPath
adminName = config.adminName
userNames = config.userNames
startTime = time.time()
lights = []
animalFolders = []

#variables for the light conversation
CHOICE, LIGHTBRIGHT, LIGHTCOLOR, LIGHTCUSTOMCOLOR, LIGHTCUSTOMTEMP, LIGHTSTATE = range(6)

##setup functions for bot##

#finds all lights on the network
def findLight() -> None:
	for dev in Discover.discover():
		lights.append(SmartBulb(dev))

#finds all folders in '/botpics'
def findAnimalFolders() -> None:
	for name in os.listdir("./botpics"):
		if os.path.isdir(os.path.join("./botpics", name)):
			animalFolders.append(name)
	animalFolders.remove('userpics')


##functions for bot##

#functions for Command Handlers

#shuts the program down if moderator calls it
def bot_sleep(bot,
			  update) -> None:
	if(update.message.from_user.username != adminName):
		bot.send_message(chat_id = update.message.chat_id, text = "You don't have permission")
		return
	bot.send_message(chat_id = update.message.chat_id, text = "Goodnight! [BOT SHUTTING DOWN]")
	print("ending program")
	os._exit(0)

#give user uptime of bot
def up_time(bot,
			update) -> None:
	if(update.message.from_user.username != adminName):
		bot.send_message(chat_id = update.message.chat_id, text = "You don't have permission")
		return
	currentTime = int(time.time() - startTime)
	m, s = divmod(currentTime, 60)
	h, m = divmod(m, 60)
	bot.send_message(chat_id = update.message.chat_id, text = "I've been up for {:02d}:{:02d}:{:02d}".format(h, m, s))

#show user list of commands
def botHelp(bot,
			update) -> None:
	bot.send_message(chat_id = update.message.chat_id, text = "{}".format(config.helpMessage), parse_mode = ParseMode.MARKDOWN)

#show user about section
def botAbout(bot,
			 update) -> None:
	bot.send_message(chat_id = update.message.chat_id, text = config.aboutMessage)

#sends a random tiger sticker from sticker pack 'WhiteTigerNL'
def send_random_tiger_sticker(bot,
							  update) -> None:
	numOfStickers = len(bot.get_sticker_set("WhiteTigerNL").stickers)
	stickerNum = randint(0, numOfStickers - 1)
	bot.send_sticker(chat_id = update.message.chat_id, sticker = bot.get_sticker_set("WhiteTigerNL").stickers[stickerNum])

#send an animal pic from folder
def send_animal_pic(bot,
				  update,
				  args) -> None:
	if not args:
		botMessage = "Please include animal as argument. `/animal_pic animal_name`\n List of animals: "
		bot.send_message(chat_id = update.message.chat_id, text = "{}{}".format(botMessage, ' '.join(animalFolders)), parse_mode = ParseMode.MARKDOWN)
		return
	else:	
		animal = args[0]
		if animal not in animalFolders:
			botMessage = "List of animals: "
			bot.send_message(chat_id = update.message.chat_id, text = "{}{}".format(botMessage, ' '.join(animalFolders)))
			return

	filePath = "./{}/{}".format(picPath, animal)
	numOfPics = len(next(os.walk(filePath))[2])
	picNum = randint(0, numOfPics - 1)
	bot.send_photo(chat_id = update.message.chat_id, photo = open('{}/{}.jpg'.format(filePath, picNum), 'rb'))
	

#functions for Light Conversation Handler
	
#changes the lights state
def change_lights(bot,
				  update) -> Any:
	if update.message.from_user.username not in userNames:
		return
	keyboard = [[InlineKeyboardButton("Brightness", callback_data='LIGHTBRIGHT'),
				 InlineKeyboardButton("Color", callback_data='LIGHTCOLOR')],
				[InlineKeyboardButton("Custom Color", callback_data='LIGHTCUSTOMCOLOR'),
				 InlineKeyboardButton("Custom Temp", callback_data='LIGHTCUSTOMTEMP')]]
	if update.message.from_user.username == adminName:
		keyboard.append([InlineKeyboardButton("ON/OFF", callback_data='LIGHTSTATE')])

	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Please choose:', reply_markup=reply_markup)
	return CHOICE

#respond to button choices for /lights
def light_choice(bot,
				 update) -> Any:
	query = update.callback_query
	data = query.data

	if data == 'LIGHTBRIGHT':
		bot.edit_message_text(chat_id = query.message.chat_id, message_id = query.message.message_id, text = "Enter Brightness [0 - 100]:")
		return LIGHTBRIGHT
	elif data == 'LIGHTCOLOR':
		keyboard = [[InlineKeyboardButton("Red", callback_data='RED'),
					 InlineKeyboardButton("Orange", callback_data='ORANGE'),
					 InlineKeyboardButton("Yellow", callback_data='YELLOW')],
					[InlineKeyboardButton("Green", callback_data='GREEN'),
					 InlineKeyboardButton("Blue", callback_data='BLUE'),
					 InlineKeyboardButton("Purple", callback_data='PURPLE')]]
	
		reply_markup = InlineKeyboardMarkup(keyboard)
		bot.edit_message_text(chat_id = query.message.chat_id, message_id = query.message.message_id, text = "Pick a color:")
		bot.edit_message_reply_markup(chat_id = query.message.chat_id, message_id = query.message.message_id, reply_markup = reply_markup)
		return LIGHTCOLOR
	elif data == 'LIGHTCUSTOMCOLOR':
		bot.edit_message_text(chat_id = query.message.chat_id, message_id = query.message.message_id, text = "Enter RGB or HEX Value")
		return LIGHTCUSTOMCOLOR
	elif data == 'LIGHTCUSTOMTEMP':
		bot.edit_message_text(chat_id = query.message.chat_id, message_id = query.message.message_id, text = "Enter Color Temperature [2500 - 9000]:")
		return LIGHTCUSTOMTEMP
	elif data == 'LIGHTSTATE':
		change_light_state() 
	else:
		return

#change light brightness
def change_light_bright(bot,
						update) -> Any:
	value = update.message.text

	if value.isdigit():
		value = int(value)
	else:
		bot.send_message(chat_id = update.message.chat_id, text = "Not a number")
		return
	if value < 0 or value > 100:
		bot.send_message(chat_id = update.message.chat_id, text = "Value out of range")
		return
	for light in lights:
			light.brightness(value)
	bot.send_message(chat_id = update.message.chat_id, text = "Brightness Changed!")

#change light color to a preset color
def change_light_color(bot,
					   update) -> Any:
	query = update.callback_query
	data = query.data
	
	if data == 'RED':
		color = (255, 0, 0)
	elif data == 'ORANGE':
		color = (255, 127, 0)
	elif data == 'YELLOW':
		color = (255, 255, 0)
	elif data == 'GREEN':
		color = (0, 255, 0)
	elif data == 'BLUE':
		color = (0, 0, 255)
	elif data == 'PURPLE':
		color = (127, 0, 255)
	else:
		return

	for light in lights:
		light.rgb(color)
	bot.edit_message_text(chat_id = query.message.chat_id, message_id = query.message.message_id, text = "Color Changed!")
	
#change light color to a custom color
def change_light_color_custom(bot,
							  update) -> None:
	value = update.message.text
	
	if '(' in value:
		value = value.lstrip('(')
		value = value.r.strip(')')
		color = tuple(map(int, value.split(',')))
	elif '#' in value:
		value = value.lstrip('#')
		color = tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
	else:
		bot.send_message(chat_id = update.message.chat_id, text = "Incorrect format.")

	for light in lights:
		light.rgb(color)
	bot.send_message(chat_id = update.message.chat_id, text = "Color Changed!")

#change light temp to custom temp
def change_light_temp_custom(bot,
							 update) -> Any:
	value = update.message.text

	if value.isdigit():
		value = int(value)
	else:
		bot.send_message(chat_id = update.message.chat_id, text = "Not a number")
		return
	if value < 2500 or value > 9000:
		bot.send_message(chat_id = update.message.chat_id, text = "Value out of range")
		return
	
	for light in lights:
		light.color_temp(value)
		bot.send_message(chat_id = update.message.chat_id, text = "Color Temp Changed!")

#switches_light_state
def change_light_state() -> None:
	for light in lights:
		light.switch_state()


#functions for Message Handlers

#responding to general messages that don't use "/" in the beginning
def chat_messages(bot,
				  update) -> None:
	if("@ShiroTheBot" in update.message.text or "@shirothebot" in update.message.text):
		talk_to_bot(bot,update)

#responds to simple messages via keywords
def talk_to_bot(bot,
				update) -> None:
	if("boop" in update.message.text):
		bot.send_message(chat_id = update.message.chat_id, text = "boops @{} ~".format(update.message.from_user.username))

	elif("<3" in update.message.text):
		bot.send_sticker(chat_id = update.message.chat_id, sticker = 'CAADAQADqC0AAq8ZYgf_JREBEDXfiQI')

#responding to photos that people send
def chat_photos(bot,
				update) -> None:
	caption = ''
	re1 = re.compile(r"^[^<>/{}\~`#%&*:+?|]*$")

	if("@ShiroTheBot" in update.message.caption):
		caption = update.message.caption.split('@ShiroTheBot')[1]
	elif("@shirothebot" in update.message.caption):
		caption = update.message.caption.split('@shirothebot')[1]	
	if(caption == '' or caption.isspace()):
		bot.send_message(chat_id = update.message.chat_id, text = "Incorrect format for picture. It should be: @ShiroTheBot [description]")
		return
	if(not re1.search(caption)):
		bot.send_message(chat_id = update.message.chat_id, text = "Invalid characters")
		return
		
	caption = "{}_{}_{}".format(caption[1:], update.message.from_user.id, time.strftime("%d-%m-%Y %H-%M-%S"))
	photoFileID = update.message.photo[-1].file_id
	newPhoto = bot.getFile(photoFileID)
	newPhoto.download('./{}/userpics/{}.jpg'.format(picPath, caption))
	bot.send_message(chat_id = update.message.chat_id, text = "I got your picture!")