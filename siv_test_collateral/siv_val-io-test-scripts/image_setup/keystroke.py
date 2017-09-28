import os, argparse, sys
from keyActions import *

def init():
	try:
		return_code = os.system("stty -F /dev/ttyUSB0 9600 -crtscts")
		if return_code:	raise KeyStrokeError("Failed to setup /dev/ttyUSB0")
	except KeyStrokeError as e:
		print e.message
		print "Exception caught while sending keystroke"
def change_efi_shell_first(auto_keyboard):
	auto_keyboard.sendKey("KEY_F2", num=200)
	auto_keyboard.sendKey("KEY_UP")
	auto_keyboard.sendKey("KEY_ENTER", num=2)
	auto_keyboard.sendKey("KEY_UP")
	auto_keyboard.sendKey("KEY_ENTER", num=2)
	auto_keyboard.sendKey("KEY_DOWN", num=10)
	auto_keyboard.sendKey("KEY_EQUAL", num=10, shift=True)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN")
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_ESC", num=2)
	auto_keyboard.sendKey("KEY_ENTER", num=5)
	
def fast_boot_in(auto_keyboard):
	auto_keyboard.sendKey("KEY_ENTER", num=10)

# from fast mode to standard mode
def i2c_standard_mode(auto_keyboard):
	auto_keyboard.sendKey("KEY_F2", num=30)
	auto_keyboard.sendKey("KEY_UP", num=2)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN")
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=3)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=3)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=7)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_UP")
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_F4")
	auto_keyboard.sendKey("KEY_ESC", num=4)
	auto_keyboard.sendKey("KEY_ENTER", num=20)

# from standard mode to fast mode
def i2c_fast_mode(auto_keyboard):
	auto_keyboard.sendKey("KEY_F2", num=30)
	auto_keyboard.sendKey("KEY_UP", num=2)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN")
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=3)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=3)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN", num=7)
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_DOWN")
	auto_keyboard.sendKey("KEY_ENTER")
	auto_keyboard.sendKey("KEY_F4")
	auto_keyboard.sendKey("KEY_ESC", num=4)
	auto_keyboard.sendKey("KEY_ENTER", num=20)
	
def main():
	script_name = str(sys.argv[0])
	usage = "Teensy Function"
	parser = argparse.ArgumentParser(prog=script_name, description=usage)
	parser.add_argument('-media', help='Media', default="usb")
	parser.add_argument('-setting', help='Settings [after_flash_bios, load_image, i2c_fast_mode, i2c_standard_mode]')
	args = parser.parse_args()
	
	media = args.media if (args.media is not None and args.media == "usb") else exit("Invalid media")
	settings = args.setting if args.setting is not None else exit("Invalid settings")

	init()
	auto_keyboard = keyActions(media)
	if settings == "after_flash_bios":
		change_efi_shell_first(auto_keyboard)
	if settings == "load_image":
		fast_boot_in(auto_keyboard)
	if settings == "i2c_fast_mode":
		i2c_fast_mode(auto_keyboard)
	if settings == "i2c_standard_mode":
		i2c_standard_mode(auto_keyboard)
		
main()
