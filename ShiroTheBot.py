#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging, functions, time
import config

##setting up bot##
updater = Updater(config.api_token)
dispatcher = updater.dispatcher

#simple logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#starting some functions useful for the bot
functions.findLight()
functions.findAnimalFolders()

#adding commands to the bot ~ message handler must be added last
dispatcher.add_handler(CommandHandler('sleep', functions.bot_sleep))
dispatcher.add_handler(CommandHandler('uptime', functions.up_time))
dispatcher.add_handler(CommandHandler('help', functions.botHelp))
dispatcher.add_handler(CommandHandler('about', functions.botAbout))
dispatcher.add_handler(CommandHandler('magic8', functions.send_random_tiger_sticker))
dispatcher.add_handler(CommandHandler('animal_pic', functions.send_animal_pic,
									  pass_args=True))

#conversation handler for handling the lights via Telegram Bot
light_conv = ConversationHandler(
	entry_points = [CommandHandler('lights', functions.change_lights)],
	states = {
		functions.CHOICE: [CallbackQueryHandler(functions.light_choice)],
		functions.LIGHTBRIGHT: [MessageHandler(Filters.text, functions.change_light_bright)],
		functions.LIGHTCOLOR: [CallbackQueryHandler(functions.change_light_color)],
		functions.LIGHTCUSTOMCOLOR: [MessageHandler(Filters.text, functions.change_light_color_custom)],
		functions.LIGHTCUSTOMTEMP: [MessageHandler(Filters.text, functions.change_light_temp_custom)]
	},
	fallbacks = [CommandHandler('lights', functions.change_lights)]
)
dispatcher.add_handler(light_conv)

#adding message handlers to the bot
dispatcher.add_handler(MessageHandler(Filters.text, functions.chat_messages))
dispatcher.add_handler(MessageHandler(Filters.photo, functions.chat_photos))

#have bot continuously poll for messages
updater.start_polling()

updater.idle()
