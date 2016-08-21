#*******************************************************************************
#	 	Copyright (c) 2016 Ramin Sangesari
#
#Special Thanks to yukuku for this project, Original Source :
#		https://github.com/yukuku/telebot
#
#
#*******************************************************************************
# -*- coding: utf-8 -*-
import StringIO
import json
import requests
import logging
import random
import urllib
import urllib2
import time
import sys
import datetime
from time import gmtime, strftime
import threading
#
import cStringIO
from emoji import Emoji
#

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2


TOKEN = 'YOUR_BOT_TOKEN_HERE'			#Telegram Token
wiotoken = 'YOUR_WIO_TOKEN_HERE '		#Wio Token
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
bot_enable = True
version = '1.02b'

#------------------------------------------------------------------------------
#		Telegram Handler
#------------------------------------------------------------------------------

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
	def post(self):
		admin_id = 97329959 				#This is my Telegram ID
		urlfetch.set_default_fetch_deadline(60)
		body = json.loads(self.request.body)
		logging.info('request body:')
		logging.info(body)
		self.response.write(json.dumps(body))

		update_id = body['update_id']
		try:
			message = body['message']
		except:
			message = body['edited_message']	
		message_id = message.get('message_id')
		date = message.get('date')
		text = message.get('text')
		fr = message.get('from')
		chat = message['chat']
		chat_id = chat['id']

#------------------------------------------------------------------------------
#		Wio Functions
#------------------------------------------------------------------------------
		def timer_pump(value):
			global wiotoken
			time.sleep(value)
			GroveRelay1OFF = "https://us.wio.seeed.io/v1/node/GroveRelayD2/onoff/0?access_token=" + wiotoken
			Wio_Var = requests.post(GroveRelay1OFF)
			reply("Irrigation was done. Period of time : " + str(value)+ " s")
							
		def isint(value):
			try:
				int(value)
				return True
			except:
				return False
		
		def CheckStatusCode(status_code):
			if status_code == 400:
				reply("Bad Request - Wrong Grove/method name provided, or wrong parameter for method provided.")
			elif status_code == 403:
				reply("Forbidden - Your access token is not authorized.")
			elif status_code == 404:
				reply("Not Found - The device you requested is not currently online, or the resource/endpoint you requested does not exist.")
			elif status_code == 408:
				reply("Timed Out - The server can not communicate with device in a specified time out period.")
			elif status_code == 500:
				reply("Server errors - It's usually caused by the unexpected errors of our side.")
			else:
				reply("Unknown error - Please contact Administrator.")
				
#------------------------------------------------------------------------------
#		Send Reply Function
#------------------------------------------------------------------------------
		
		if not text:
			logging.info('no text')
			return

		def reply(msg=None, sendfile=None, uri=None, farstr=None):
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(chat_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_to_message_id': str(message_id),
				})).read()
			elif sendfile:	#send file
				resp = urllib2.urlopen(BASE_URL + 'sendDocument', urllib.urlencode({
					'chat_id': str(chat_id),
					'reply_to_message_id': str(message_id),
					'document' : sendfile,
				})).read()
			elif uri:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(chat_id),
					'text': uri,
					'disable_web_page_preview': 'false',
					'reply_to_message_id': str(message_id),
				})).read()	
			elif farstr:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(chat_id),
					'text': farstr,
					'disable_web_page_preview': 'true',
					'reply_to_message_id': str(message_id),
				})).read()	
				
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)
#------------------------------------------------------------------
#		Commands	
#------------------------------------------------------------------
		text = text.lower()
		w = text.split()
		global bot_enable
		global wiotoken
		
		if (chat_id == admin_id):			#Admin ID
			if text == '/enable':
				reply('Bot enabled.')
				bot_enable = True
			elif text == '/disable':
				reply('Bot disabled.')
				bot_enable = False
				
		if (bot_enable):
			if text == '/about':
				global version
				aboutTXT = 'Wio bot v' + version + '\nCopyright (c) 2016 www.idreams.ir\nProgrammer: @RaminSangesari\nEmail: r_sangsari@yahoo.ca'
				reply(aboutTXT)
			elif text =='/start':
				stxt = 'my friend'
				txt = 'Hello, ' + stxt + '\nThis is the @wiobot.\nFor more information please send /help or ?\nContact @RaminSangesari if have questions about @wiobot'
				reply(txt)				
#############################################################################
##		WIO Commands
#############################################################################

			elif text =='/leakgas':
				Grove_Gas1 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NH3?access_token=" + wiotoken			# Ammonia (ppm)
				Grove_Gas2 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CH4?access_token=" + wiotoken			# Methane
				Grove_Gas3 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C4H10?access_token=" + wiotoken			# Iso-butane
				Grove_Gas4 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/NO2?access_token=" + wiotoken			# Nitrogen dioxide
				Grove_Gas5 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C2H5OH?access_token=" + wiotoken			# Ethanol
				Grove_Gas6 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/CO?access_token=" + wiotoken				# Carbon monoxide
				Grove_Gas7 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/C3H8?access_token=" + wiotoken			# Propane
				Grove_Gas8 = "https://us.wio.seeed.io/v1/node/GroveMultiChannelGasI2C0/H2?access_token=" + wiotoken				# Hydrogen
				#
				Wio_Var1 = requests.get(Grove_Gas1)
				if Wio_Var1.status_code == 200:
					Var1 = json.loads(Wio_Var1.text)
					AmmoniaReading = Var1['concentration_ppm']
					#
					Wio_Var2 = requests.get(Grove_Gas2)
					if Wio_Var2.status_code == 200:
						Var2 = json.loads(Wio_Var2.text)
						MethaneReading = Var2['concentration_ppm']
						#
						Wio_Var3 = requests.get(Grove_Gas3)
						if Wio_Var3.status_code == 200:
							Var3 = json.loads(Wio_Var3.text)
							IsobutaneReading = Var3['concentration_ppm']
							#
							Wio_Var4 = requests.get(Grove_Gas4)
							if Wio_Var4.status_code == 200:
								Var4 = json.loads(Wio_Var4.text)
								NitrogenDioxideReading = Var4['concentration_ppm']		
								#
								Wio_Var5 = requests.get(Grove_Gas5)
								if Wio_Var5.status_code == 200:
									Var5 = json.loads(Wio_Var5.text)
									EthanolReading = Var5['concentration_ppm']		
									#
									Wio_Var6 = requests.get(Grove_Gas6)
									if Wio_Var6.status_code == 200:
										Var6 = json.loads(Wio_Var6.text)
										CarbonMonoxideReading = Var6['concentration_ppm']		
										#
										Wio_Var7 = requests.get(Grove_Gas7)
										if Wio_Var7.status_code == 200:
											Var7 = json.loads(Wio_Var7.text)
											PropaneReading = Var7['concentration_ppm']		
											#
											Wio_Var8 = requests.get(Grove_Gas8)
											if Wio_Var8.status_code == 200:
												Var8 = json.loads(Wio_Var8.text)
												HydrogenReading = Var8['concentration_ppm']		
												TotalResult = "Ammonia : " + str(AmmoniaReading) + " ppm" + "\nMethane : " + str(MethaneReading) + " ppm" + "\nIso-Butane : " + str(IsobutaneReading) + " ppm" + "\nNitrogen Dioxide : " + str(NitrogenDioxideReading) + " ppm" + "\nEthanol : " + str(EthanolReading) + " ppm" + "\nCarbon Monoxide : " + str(CarbonMonoxideReading) + " ppm" + "\nPropane : " + 	str(PropaneReading) + " ppm" + "\nHydrogen : " + str(HydrogenReading) + " ppm"					
												reply(TotalResult)
											else:
												CheckStatusCode(Wio_Var8.status_code)
				else:
					CheckStatusCode(Wio_Var1.status_code)								
			###
			##
			elif text =='/petfood':
				GroveServo = "https://us.wio.seeed.io/v1/node/GroveServoD0/angle/50?access_token=" + wiotoken
				tempReading = requests.post(GroveServo)
				if tempReading.status_code == 200:
					reply(farstr="Feeding was done.")
				else:
					CheckStatusCode(tempReading.status_code)
			####
			elif text =='/garagedoorstatus':
				GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff_status?access_token=" + wiotoken
				Wio_Var = requests.get(GroveRelay1)
				if Wio_Var.status_code == 200:
					Wio_Var = json.loads(Wio_Var.text)
					tmpReading = Wio_Var['onoff']
					if (tmpReading==1):
						reply("Garage Door Status : OPEN")
					else:
						reply("Garage Door : CLOSE")
				else:
					CheckStatusCode(Wio_Var.status_code)
			###
			elif text.startswith('/garagedoor'):
				text = text.encode('utf-8')
				query = text[12:]
				if (query == "open"):
					st_var = 1 
				elif (query == "close"):
					st_var = 0 
				else:
					reply("Invalid value.\nFor example : /garagedoor open")
				if (query == "open") or (query == "close"):	
					GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff/" + str(st_var) + "?access_token=" + wiotoken
					Wio_Var = requests.post(GroveRelay1)
					if Wio_Var.status_code == 200:
						if (st_var == 1):
							reply("Garage Door is OPEN.")
						elif (st_var == 0):
							reply("Garage Door is CLOSE.")
					else:
						CheckStatusCode(Wio_Var.status_code)
					query = ""
			####
			elif text =='/lightstatus':
				GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff_status?access_token=" + wiotoken
				Wio_Var = requests.get(GroveRelay1)
				if Wio_Var.status_code == 200:
					Wio_Var = json.loads(Wio_Var.text)
					tmpReading = Wio_Var['onoff']
					if (tmpReading==1):
						reply("Light Status : ON")
					else:
						reply("Light Status : OFF")
				else:
					CheckStatusCode(Wio_Var.status_code)			
			####
			elif text.startswith('/light'):
				text = text.encode('utf-8')
				query = text[7:]
				if (query == "on"):
					st_var = 1 
				elif (query == "off"):
					st_var = 0 
				else:
					reply("Invalid value.\nFor example : /light on")
				if (query == "on") or (query == "off"):	
					GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff/" + str(st_var) + "?access_token=" + wiotoken
					Wio_Var = requests.post(GroveRelay1)
					if Wio_Var.status_code == 200:
						if (st_var == 1):
							reply("Light is ON.")
						elif (st_var == 0):
							reply("Light is OFF.")
					else:
						CheckStatusCode(Wio_Var.status_code)
					query = ""
			####
			elif text =='/fanstatus':
				GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff_status?access_token=" + wiotoken
				Wio_Var = requests.get(GroveRelay1)
				if Wio_Var.status_code == 200:
					Wio_Var = json.loads(Wio_Var.text)
					tmpReading = Wio_Var['onoff']
					if (tmpReading==1):
						reply("Fan Status : ON")
					else:
						reply("Fan Status : OFF")
				else:
					CheckStatusCode(Wio_Var.status_code)
			####
			elif text.startswith('/fan'):
				text = text.encode('utf-8')
				query = text[5:]
				if (query == "on"):
					st_var = 1 
				elif (query == "off"):
					st_var = 0 
				else:
					reply("Invalid value.\nFor example : /fan on")
				if (query == "on") or (query == "off"):	
					GroveRelay1 = "https://us.wio.seeed.io/v1/node/GroveRelayD1/onoff/" + str(st_var) + "?access_token=" + wiotoken
					Wio_Var = requests.post(GroveRelay1)
					if Wio_Var.status_code == 200:
						if (st_var == 1):
							reply("Fan is ON.")
						elif (st_var == 0):
							reply("Fan is OFF.")
					else:
						CheckStatusCode(Wio_Var.status_code)
					query = ""

			####
			elif text.startswith('/waterpump'):
				query = text[11:]
				if(isint(query)):
					queryint = int(query)
					if (queryint >= 1) and (queryint <= 60):
						GroveRelay1ON = "https://us.wio.seeed.io/v1/node/GroveRelayD2/onoff/1?access_token=" + wiotoken
						Wio_Var = requests.post(GroveRelay1ON)
						if Wio_Var.status_code == 200:
							reply("Running the command.\nPlease Wait ...")
							t = threading.Thread(target=timer_pump(queryint))
							t.start()
						else:
							CheckStatusCode(Wio_Var.status_code)

					else:
						reply("Please enter a value between 0 and 60.")
					
				else:
					reply("Invalid value. Please enter a value between 0 and 60.\nFor example : /waterpump 30")					
			####		
			elif text =='/moisture':
				GroveMoisture = "https://us.wio.seeed.io/v1/node/GroveMoistureA0/moisture?access_token=" + wiotoken
				Wio_Var = requests.get(GroveMoisture)
				if Wio_Var.status_code == 200:
					tempReading = json.loads(Wio_Var.text)
					tempReading = tempReading['moisture']
					reply(farstr="Moisture : " + str(tempReading) + ' %')
				else:
					CheckStatusCode(Wio_Var.status_code)
			####
			elif text =='/temp':
				GroveTemp = "https://us.wio.seeed.io/v1/node/GroveTempHumD0/temperature?access_token=" + wiotoken
				tempReading = requests.get(GroveTemp)
				if tempReading.status_code == 200:
					tempReading = json.loads(tempReading.text)
					tempReading = tempReading['celsius_degree']
					reply(farstr="Temperature : " + str(tempReading) + ' °C')
				else:
					CheckStatusCode(tempReading.status_code)
			####
			elif text =='/humidity':
				GroveHumidity = "https://us.wio.seeed.io/v1/node/GroveTempHumD0/humidity?access_token=" + wiotoken
				tempReading = requests.get(GroveHumidity)
				if tempReading.status_code == 200:
					tempReading = json.loads(tempReading.text)
					tempReading = tempReading['humidity']
					reply(farstr="Humidity : " + str(tempReading) + ' %')
				else:
					CheckStatusCode(tempReading.status_code)			
#############################################################################
##		Get Telegram id and Help Section
#############################################################################					
			elif text =='/id':			
				iid = 'Your telegram id is : '+str(chat_id)			
				reply(iid)
			elif (text == '?') or (text == '/help') or (text == 'h'):
				reply('Commands List:\n\n/leakgas - Gas leak test\n/petfood - Feeding the pet or fish\n/garagedoor - Open\Close Garage Door. For example : [/garagedoor open]\n/garagedoorstatus - Check Garage Door status\n/light - On\Off light. for example : [/light on]\n/lightstatus - Check light status.\n/fan - On\Off Fan. for example : [/fan on]\n/fanstatus - Check Fan status\n/moisture - Check Soil moisture conditions\n/waterpump - Open Water Pump for Irrigation and close pump after selected time (Time based on the second.). For example : [/waterpump 12]\n/temp - Show temperature\n/humidity - Show humidity\n\nAll commands are case insensitive.')
			else:
				reply('Unrecognized command.\nFor more information please send /help or ?\nAll commands are case-insensitive.')

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
