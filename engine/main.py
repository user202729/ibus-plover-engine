#!/bin/python3
#
# ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2007-2014 Peng Huang <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# for python2
from __future__ import print_function

import gi  # type: ignore
gi.require_version('IBus', '1.0')
from gi.repository import IBus	   # type: ignore
from gi.repository import GLib	   # type: ignore
from gi.repository import GObject  # type: ignore

import os
import sys
import getopt
import gettext
#import locale
#
#try:
#	from . import engine
#	pass
#except (ModuleNotFoundError, ImportError):
#	import engine
#	#pass
import engine
EngineEnchant=engine.EngineEnchant

from plover_ibus.ibus_lib import keysym_to_keycode, keysym_to_name
from plover_ibus.lib import response_path, listen_path_name
from plover_ibus import lib

_ = lambda a: gettext.dgettext('ibus-tmpl', a)

class IMApp:
	def __init__(self, exec_by_ibus: bool)->None:
		long_engine_name = "enchant python" if exec_by_ibus else "enchant python (debug)"
		self.__component = \
				IBus.Component.new("org.freedesktop.IBus.EnchantPython",
								   "Enchant Python Component",
								   "0.1.0",
								   "GPL",
								   "Peng Huang <shawn.p.huang@gmail.com>",
								   "http://example.com",
								   "/usr/bin/exec",
								   "ibus-enchant")
		engine_name="enchant-python"
		engine = IBus.EngineDesc.new(engine_name,
									 long_engine_name,
									 "English Enchant",
									 "en",
									 "GPL",
									 "Peng Huang <shawn.p.huang@gmail.com>",
									 "",
									 "us")
		self.__component.add_engine(engine)
		self.__mainloop = GLib.MainLoop()
		self.__bus = IBus.Bus()
		self.__bus.connect("disconnected", self.__bus_disconnected_cb)
		self.__factory = IBus.Factory.new(self.__bus.get_connection())
		self.__factory.add_engine(engine_name,
				GObject.type_from_name("EngineEnchant"))
		if exec_by_ibus:
			self.__bus.request_name("org.freedesktop.IBus.EnchantPython", 0)
		else:
			print('ok')
			self.__bus.register_component(self.__component)
			self.__bus.set_global_engine_async(
					engine_name, -1, None, None, None)

	def run(self):
		print('ok')
		self.__mainloop.run()

	def stop(self):
		print("**stop manual**")
		self.__mainloop.quit()

	def __bus_disconnected_cb(self, bus):
		print("**quit**")
		self.__mainloop.quit()


import threading
import typing

from pathlib import Path
import tempfile

def handle_message(message: typing.Any)->None:
	type_, content=message
	engine_=engine.instance()

	def send_key(keysym: int, keycode: int=None)->None:
		if keycode is None:
			keycode=keysym_to_keycode.get(keysym, 0)
		engine_.forward_key_event(keysym, keycode, 0)
		engine_.forward_key_event(keysym, keycode, IBus.ModifierType.RELEASE_MASK)


	if type_==lib.BACKSPACE:
		text, cursor_pos, anchor_pos=engine_.get_surrounding_text()
		print("**", text, cursor_pos, anchor_pos)
		to_delete: int=min(cursor_pos, content)
		if to_delete:
			engine_.delete_surrounding_text(-to_delete, to_delete)
			content-=to_delete
		for _ in range(content):
			send_key(IBus.BackSpace)

	elif type_==lib.RAW_STRING:
		engine_._commit_string(content)

	elif type_==lib.SMART_STRING:
		print('send str', content)
		import re

		for part in re.split(r"([\t\n])", content):
			if not part: continue
			if part=="\t": send_key(IBus.Tab)
			elif part=="\n": send_key(IBus.Return)
			else: engine_._commit_string(part)

	elif type_==lib.COMBINATION:
		for keysym, mods in content:
			print("send combo", keysym_to_name[keysym], keysym, keysym_to_keycode.get(keysym, 0))
			engine_.forward_key_event(
					keysym,
					keysym_to_keycode.get(keysym, 0),
					mods
					)

	else:
		print("unrecognized", message)

	client=connection.Client(
			str(response_path),
			"AF_UNIX",
			authkey=None
			)
	#client.send(None)

from multiprocessing import connection
#
#def accept_connection(connection: connection.Connection)->None:
#	while True:
#		message=connection.recv()
#
#
#def listen_run()->None:
#	from pathlib import Path
#	import tempfile
#	path=Path(tempfile.gettempdir())/".ibus-listen"
#	print("path=", path)
#	try:
#		path.unlink()
#	except FileNotFoundError:
#		pass
#	listen=connection.Listener(
#			str(path),
#			"AF_UNIX",
#			authkey=None
#			)
#	while True:
#		connection_=listen.accept()
#		threading.Thread(target=accept_connection, args=(connection_,)).start()

#def listen_start()->None:
#	listen_thread=threading.Thread(target=listen_run)
#	listen_thread.start()


#from plover.oslayer.controller import Controller  # type: ignore
from plover_auto_identifier.controller import Controller  # type: ignore
# https://plover.readthedocs.io/en/latest/api/oslayer_controller.html
# https://plover2.readthedocs.io/en/latest/api/oslayer_controller.html


controller_=None

def listen_start(retry: bool=True)->None:
	print("listen_start")
	controller=Controller(listen_path_name)
	controller.__enter__()

	assert controller._thread is None
	print(controller._address)
	if not controller.is_owner:
		assert retry
		controller.force_cleanup()
		return listen_start(retry=False)

	global controller_
	controller_=controller
	print("before start")
	assert controller._thread is None
	controller.start(handle_message)
	print("after start (???? must have finally-executing???)")

def main():
	try:
		locale.setlocale(locale.LC_ALL, "")
	except:
		pass

	exec_by_ibus = False
	daemonize = False

	shortopt = "id"
	longopt = ["ibus", "daemonize"]

	try:
		opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
	except getopt.GetoptError as err:
		sys.exit(1)

	for o, a in opts:
		if o in ("-i", "--ibus"):
			exec_by_ibus = True
		else:
			sys.stderr.write("Unknown argument: %s\n" % o)
			print_help(1)

	IBus.init()

	listen_start()

	try:
		IMApp(exec_by_ibus).run()
	finally:
		print("finally executing")
		controller_.stop()
		#listen_thread.join()
		controller_.__exit__(None, None, None)
		print("finally done")

if __name__ == "__main__":
	if 1:
		main()
	else:
		threading.Thread(target=main).start()
