#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests

from tornado.options import define, options
define("port", default=9119, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="run on the given address")
URL = 'https://api.telegram.org/bot'

proxies = {'http': 'socks5h://user:pass@IP:PORT', 'https': 'socks5h://user:pass@IP:PORT'}
TOKEN = '11111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
chat_id = 00000000

class MainHandler(tornado.web.RequestHandler):
	def get(self):self.write("Use POST Luke")

class AlertHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_status(200)
		self.finish("OK")

	def post(self):
		try:
			content = tornado.escape.json_decode(self.request.body)
			#print(content)
			try:
				for alert in content['alerts']:
					message = "Hostname: <b>{}</b>\nStatus: <b>{}</b>\nAlertname: <b>{}</b>\n\n<b>{}</b>\n".format(alert['labels']['instance'], alert['status'], alert['labels']['alertname'], alert['annotations']['summary'])
					#print("Message: ", message)
					data = {'disable_web_page_preview': 1, 'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
					try:
						request = requests.post(URL + TOKEN + '/sendMessage', proxies=proxies, data=data, timeout=3)
						print('TELEGRAM', request.status_code, request.reason, chat_id)
					except Exception as e:
						print('TELEGRAM error getting updates, error: ' + str(e))
						#request = requests.post(URL + TOKEN + '/sendMessage', proxies=proxies, data=data, timeout=6)
			except Exception as e:
				print('TELEGRAM wrong json error: ' + str(e))

			self.set_status(200)
			self.finish("TELEGRAM all messages were send")
		except Exception as e:
			print('TELEGRAM must be json, error: ' + str(e))
			self.set_status(503)
			self.finish("Must be json")


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers=[
		(r"/", MainHandler),
		(r"/alert", AlertHandler)
	], debug=True)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port, options.address)
	tornado.ioloop.IOLoop.instance().start()

