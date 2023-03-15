# PicoPendant
A small wireless CNC Pendant based off the Raspberry Pi Pico W and the Waveshare Pico-ResTouch-LCD-3.5. 

The pendant uses WiFi to communicate with the CNC and can work with any CNC/Mill/3d printer device that is available on a network. The current Micropython source only supports Duet3d-based controllers because that's all I have.

## Folders
* CircuitBoard<br>This contains the circuit board (display hat) files and readme. The circuit board has two LiPo connectors (small and regular), a LiPo charger, three encoder inputs, three A/D dividers for ladder switches and one switch input.
* Enclosure<br>This contains a Fusion360 workspace and result STL files for 3d printing an enclosure and spacers. The spacers are used to support the display hat over the Waveshare LCD. Since the hole locations are not exact and Jlcpcb seems unable to put holes in the right place anyway, the spacers are slightly offset.
* PythonSrc<br>The MicroPython source code

## Getting Started

You may need to install a driver to have the Pico show up as a serial port. See the Raspberry Pi Pico documentation.

### Installing MicroPython
* Plug the Pico into a USB port.
* Boot the Pico W. If it's connected to the display use the display reboot button, otherwise just power up the USB port.
* While booting, hold down the white button on top of the Pico. This will attach a drive to the PC.
* Copy the latest Micropython UF2 file to the attached Pico drive. When the copy is complete the Pico will reboot and Python will be installed.

### Start up Visual Studio Code
* Install Visual Studio Code
* Add these extensions (at least)
  * Python - adds intellisense for python
  * Pymakr - this plugin adds USB serial support for the Pico
* Start up Visual Studio Code and open the source folder. You should be prompted to load the PicoPendant.code-workspace as a Workspace and that links in the Pymakr usb serial extensions.

### Synching and copying files
* In Visual Studio Code switch to the pymakr extension icon in the left toolbar
* You may need to select the Pico COM port (ensure any driver is installed)
* As you mouse over the USB Serial Device line under PROJECTS / PicoPendant you'll see some icons appear (yeah bad UI)
  * Click the lightning bolt icon to connect to the Pico USB Serial
  * Click the box/prompt icon to open a terminal connected to the Pico
* To copy a file to the Pico:
  * Right click the file name and use the pymakr menu to select Upload to device
* To synchronize all files to the pico:
  * Mouse over the USB Serial Device line in the pymakr extension and pick the arrow-to-cloud icon (yeah bad UI)

### config.json
The code sets up default globals then reads config.json to override them. It's simple to manually edit your config.json and set up networking variables. Put config.json in the root with main.py to have it loaded at startup. Interrupt (Ctrl-C) the running jog.py and use

	from util import picoPendant
	picoPendant.GlobalPico().Save()

to save current settings. Clean out the stuff you don't want changed, then edit the stuff you want to override.

## SBC Support
The SBC version of the Duet3d controller takes quite a different WiFi syntax and is not yet supported.
