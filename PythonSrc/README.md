# PicoPendant

## Overview
PicoPendant is a very simple product. It contains a Raspberry Pi Pico W, a [optional touchscreen] display, and a board that provides support for a LiPo alternate power source with charger from the USB. The board also has output pins providing raw access to most of the unused Pico I/O pins in a form for easy attachment to rotary encoders, ladder switches and other simple I/O devices.

The micropython source workspace (this) uses the __pymakr__ Visual Studio Code extension to communicate with the Pico W. It can synchronize files between the Pico W and PC and is generally very convenient but a bit awkward.

## Source
The source is all standard __MicroPython__. It is divided into functional groups. I attempted to use asynchronous I/O and a thread and both attempts failed miserably. Either it was running out of memory or too slow or ... anyway I pulled that stuff all out and it's just all blocking I/O for now. Maybe over time the threading will improve because network threaded is so obvious.

## Known Concerns
* Touchscreen<br>
Currently the touchscreen location can not be read because this requires a much slower SPI speed and trying to temporarily switch the SPI speed to accomodate the touch location reader causes WiFi, which also uses SPI, to start failing permanently. So for now the touch location is not used.
* Performance<br>
Due to the unwillingness to keep trying to use thread or asynch there are some performance concerns where WiFi waiting for responses causes GUI lags. This is solvable but not yet worth the trouble until other things are solid.
* Rotary Encoders<br>
The current switch-based encoders are pretty weak (coarse and occasional step-loss) but very cheap - the usual tradeoff. Using a real optical encoder for the movement rotary would help a lot and I may switch to that at some point since I have one lying around.
* MicroPython<br>
Both MicroPython and CircuitPython are still in beta for the Raspberry Pi Pico W and it shows. CircuitPython is unstable, has no thread support, and the wifi support is very bad so imho unsuitable.  MicroPython has been stable and usable but I haven't yet gotten thread to work well - which is pretty necessary.

## Folders

### display

Support code for drawing on the LCD along with app color theme and a simple text box. There's text support for loaded proportional fonts that can easily be created from TrueType.

* lcdDriver is mainly hardware dependent stuff
* dispUtil is only for test/demo stuff
* ioBox is a text box
* colorSet is a few color dictionaries incuding a primitive theme

### fonts

The fonts are stored as importable .py files that produce b/w font masks - but that is incredibly memory inefficient so instead the fontReader code manually reads the files, skips some steps, and produces the allocated bytearrays efficiently. For the really large digits, which change a lot, the fontDrawer draws them in a framebuffer and the fontCache dumbly blits predrawn characters for more speed. In my experience the pymakr extensions fail miserably without about 64K of free memory.

### screens

A really bad early gui. I want to see what gui things will be in use before spending time writing a more general probably xml-like generator.
* screens is the base class. 
* jog is the first 'screen' and currently it uses the text boxes as ways to draw but that'll switch to one textbox per field.

### util

One file per utility type. 
* two network connection modules (AP and STA)
* standard 'arduino' rotary encoder module
* ladder switch module<br> a switch where the pins are connected by roughly equal resistor values and two wires go to an A/D with known resistive divider. 
* picoPendant has the global data storage dictionary sets
  * one serialized
  * one full of created objects
 
The board has 3 encoder ports, 3 ladder sw or general A/D ports with 10K divider, and one digital switch input.

### web

* wifiConnect is the wifi connection method
* webQueue is a serial Wifi queue but currently unused. It was desiged for threading or async.
* ureq is async urequests (for debug)
* ureqorig is urequests with additional diagnostics (for debug)

### root files

* boot.py - pretty slim but does the global initialization
* main.py - allocates the font bytearrays, the display buffer and the caches and then does network initialization
* secrets_file.py - storage of wifi SSID and password for first runs or if loading GlobalPico's config.json fails
* convertFonts - a standalone CPython module to convert bitmap fonts to .py
