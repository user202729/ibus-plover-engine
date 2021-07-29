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

#import enchant

from gi.repository import GLib	  # type: ignore
from gi.repository import IBus	  # type: ignore
from gi.repository import Pango   # type: ignore

keysyms = IBus

import weakref
import typing
instances: typing.List[weakref.ReferenceType["EngineEnchant"]]=[]

def filter_instances():
	global instances
	instances=[x for x in instances if x() is not None]

def instance()->"EngineEnchant":
	filter_instances()
	if len(instances)!=1:
		import time
		time.sleep(0.3)
		filter_instances()
	assert len(instances)==1, instances

	result=instances[0]()
	assert result is not None
	return result

print('start00')


class EngineEnchant(IBus.Engine):
	__gtype_name__ = 'EngineEnchant'
	#__dict = enchant.Dict("en")

	def __init__(self):
		super(EngineEnchant, self).__init__()
		self.__is_invalidate = False
		self.__preedit_string = ""
		self.__lookup_table = IBus.LookupTable.new(10, 0, True, True)
		self.__prop_list = IBus.PropList()
		self.__prop_list.append(IBus.Property(key="test", icon="ibus-local"))
		filter_instances()
		instances.append(weakref.ref(self))
		print("Create EngineEnchant OK", len(instances))

		print("**")
		#GLib.timeout_add(1000, lambda: [self._commit_string("a"), True][-1]) # loop indefinitely

	def do_process_key_event(self, keyval, keycode, state):
		print(keyval, keycode, state)
		return False

		#print("process_key_event(%04x, %04x, %04x)" % (keyval, keycode, state))
		# ignore key release events
		is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
		if not is_press:
			return False

		if keyval==ord("a") and (
				state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) == 0):
			self._commit_string("b")
			return True

		return False
		# ========


		if keyval in range(keysyms.a, keysyms.z + 1) or \
			keyval in range(keysyms.A, keysyms.Z + 1):
			if state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) == 0:
				GLib.timeout_add(1000,
						lambda: [self._commit_string(chr(keyval+1)), False][-1]
						)
				#import threading
				#threading.Timer(
				#		1,
				#		lambda: self._commit_string(chr(keyval+1))
				#		).start()
				## (is this safe?...)
				#self.__invalidate()
				return True

		return False

	def __invalidate(self):
		if self.__is_invalidate:
			return
		self.__is_invalidate = True
		GLib.idle_add(self.__update)


	def do_page_up(self):
		if self.__lookup_table.page_up():
			self.page_up_lookup_table()
			return True
		return False

	def do_page_down(self):
		if self.__lookup_table.page_down():
			self.page_down_lookup_table()
			return True
		return False

	def do_cursor_up(self):
		if self.__lookup_table.cursor_up():
			self.cursor_up_lookup_table()
			return True
		return False

	def do_cursor_down(self):
		if self.__lookup_table.cursor_down():
			self.cursor_down_lookup_table()
			return True
		return False

	def _commit_string(self, text):
		print("**")
		self.commit_text(IBus.Text.new_from_string(text))
		#self.__preedit_string = ""
		#self.__update()

	def __update(self):
		preedit_len = len(self.__preedit_string)
		attrs = IBus.AttrList()
		self.__lookup_table.clear()
		if preedit_len > 0:
			if not self.__dict.check(self.__preedit_string):
				attrs.append(IBus.Attribute.new(IBus.AttrType.FOREGROUND,
						0xff0000, 0, preedit_len))
				for text in self.__dict.suggest(self.__preedit_string):
					self.__lookup_table.append_candidate(IBus.Text.new_from_string(text))
		text = IBus.Text.new_from_string(self.__preedit_string)
		text.set_attributes(attrs)
		self.update_auxiliary_text(text, preedit_len > 0)

		attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE,
				IBus.AttrUnderline.SINGLE, 0, preedit_len))
		text = IBus.Text.new_from_string(self.__preedit_string)
		text.set_attributes(attrs)
		self.update_preedit_text(text, preedit_len, preedit_len > 0)
		self.__update_lookup_table()
		self.__is_invalidate = False

	def __update_lookup_table(self):
		visible = self.__lookup_table.get_number_of_candidates() > 0
		self.update_lookup_table(self.__lookup_table, visible)


	def do_focus_in(self):
		print("focus_in")
		self.register_properties(self.__prop_list)

	def do_focus_out(self):
		print("focus_out")

	def do_reset(self):
		print("reset")

	def do_property_activate(self, prop_name):
		print("PropertyActivate(%s)" % prop_name)

