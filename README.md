## Plover remote control engine for IBus

### System requirements

IBus have to be installed and enabled. Refer to your distribution documentation for more details.

If there's any missing dependency, refer to [IBus system requirements](https://github.com/ibus/ibus/wiki/DevGuide#system-requirements).

### Build & Install

Adapted from [IBus wiki](https://github.com/ibus/ibus/wiki/DevGuide).

	git clone https://github.com/user202729/ibus-tmpl
	cd ibus-tmpl
	./autogen.sh --prefix /usr
	make
	sudo make install

### Uninstall

	sudo make uninstall

### Usage

Enable the extension plugin in Plover.
(you also need to install a Plover extension plugin [`plover-ibus`](https://github.com/user202729/plover-ibus))

Go to IBus Preferences -> Input method, add and select engine "Enchant (English)".

Additionally, it's recommended to configure IBus to use same input method for all applications
(Preferences -> Advanced -> Share the same input method among all applications)

