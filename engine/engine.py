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

from plover_ibus.ibus_lib import keysym_to_name
from typing import Dict


class EngineEnchant(IBus.Engine):
	__gtype_name__ = 'EngineEnchant'
	#__dict = enchant.Dict("en")

	def __init__(self)->None:
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

	# inconsistently "keysym" parameter is called keyval in some places
	def do_process_key_event(self, keysym: int, keycode: int, state: int)->bool:
		print(keysym_to_name.get(keysym, f"?{keysym}"), keycode, IBus.ModifierType(state))
		return False

	def _commit_string(self, text: str)->None:
		print("**")
		self.commit_text(IBus.Text.new_from_string(text))

	def do_focus_in(self):
		print("focus_in")
		self.register_properties(self.__prop_list)

	def do_focus_out(self):
		print("focus_out")

	def do_reset(self):
		print("reset")

