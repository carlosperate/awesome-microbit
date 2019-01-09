# Awesome micro:bit [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[![micro:bit logo](https://user-images.githubusercontent.com/4189262/45967806-fcf4ec00-c026-11e8-90a7-be2ecac881d5.png)](https://www.microbit.org)

A curated list of resources for the BBC micro:bit, a tiny programmable computer designed to make learning and teaching easy and fun!
This embedded board has a Bluetooth capable microcontroller, USB interface, accelerometer, magnetometer, light and temperature sensors, 5x5 LED matrix, buttons, and GPIO accessible via the edge connector.

[![watch badge](https://img.shields.io/github/watchers/carlosperate/awesome-microbit.svg?label=Watch&style=social)](https://github.com/carlosperate/awesome-microbit/watchers) You can "Watch" this repository if you'd like to get notfications when a new entry is added to the list.

Inspired by the [Awesome lists](https://github.com/sindresorhus/awesome).

Contributions are welcome!

## Contents

- [Programming](#programming)
	- [Visual](#visual)
	- [Python](#python)
	- [JavaScript / MakeCode](#javascript-and-makecode)
	- [C/C++](#cc)
	- [Other micro:bit Languages](#other-microbit-languages)
	- [Other Interaction Languages](#other-interaction-languages)
- [Programming Tools](#programming-tools)
- [Mobile Apps](#mobile-apps)
- [ChromeOS Apps](#chromeos-apps)
- [Interface Chip](#interface-chip)
- [Hardware](#hardware)
- [3D Printing](#3d-printing)
- [CAD](#cad)
- [2D Design](#2d-design)
- [Projects](#projects)
- [Articles](#articles)
- [Videos](#videos)
- [Books](#books)
- [Teaching Resources](#teaching-resources)
- [Community](#community)
- [Miscellaneous](#miscellaneous)


## Programming

### Visual

- [MakeCode](https://makecode.microbit.org) - Provides an in-browser emulator and a Blocks interface that generates JavaScript (TypeScript) code (part of Microsoft's PXT).
	- [MakeCode Windows 10 App](https://www.microsoft.com/store/apps/9pjc7sv48lcx) - Windows 10 application for micro:bit MakeCode.
- [Open Roberta Lab](http://lab.open-roberta.org) - Block programming environment design for programming robots, it also supports the micro:bit by generating MicroPython.
- [EduBlocks](https://microbit.edublocks.org) - Blocks interface that provides a transitioning experience from Scratch to Python.
- [MicroBlocks](http://microblocks.fun) - A visual programming language inspired by Scratch that runs right inside microcontroller boards such as the micro:bit.
- [Scratch 3.0](https://scratch.mit.edu/microbit) - The new version of Scratch is officially compatible with the micro:bit via their Scratch Link plug-in.
- [Workbench](https://edu.workbencheducation.com/partners/microbit) - A multi-device coding canvas for block-based programming that connects with BLE devices via Chrome Web Bluetooth.

The following editors are no longer maintained:
- [Microsoft Blocks](https://www.microbit.co.uk/app/#create:xczaux) - Block interface that produces Touch Develop code. No longer in development and it's recommended to use MakeCode instead.
- [Code Kingdoms](https://www.microbit.co.uk/app/#create:tomwku) - Graphical interface that provides a transitioning experience from 'drag and drop' to text-based programming (JavaScript). This editor is no longer maintained.

##### Scratch 2 Extensions

- [Scratch for BBC micro:bit](http://www.picaxe.com/BBC-microbit) - Using micro:bit with Scratch / S2Bot as a Bluetooth 'games controller' (needs specific BLED112 Bluetooth dongle).
- [ScratchX micro:bit extension](https://llk.github.io/microbit-extension/) - Lets you control your micro:bit wirelessly using Scratch programming blocks.
- [s2m](https://github.com/MrYsLab/s2m) - A Python program that acts as a bridge between the Scratch 2 off-line editor and the micro:bit via USB.
- [s2microbit BLE](https://github.com/memakura/s2microbit-ble#English) - Scratch 2 (offline) extension for BBC micro:bit bluetooth connection with a Windows PC.

### Python

- [MicroPython](http://microbit-micropython.readthedocs.io) - Port of MicroPython, a Python 3 implementation for microcontrollers and constrained environments.

##### MicroPython Editors

- [microbit.org Python editor](https://python.microbit.org) - The official online Python editor from the micro:bit foundation website.
- [microbit.co.uk Python editor](http://microbit.co.uk/app/#create:xyelfe) - Original Python editor from microbit.co.uk, contains an older version of MicroPython.
- [Mu](http://codewith.mu) - "Micro" editor for MicroPython and the BBC micro:bit.
- [create.withcode.uk](https://create.withcode.uk) - Python online editor and simulator that supports the micro:bit MicroPython ([instructions](http://community.computingatschool.org.uk/resources/4479)).
- [Atom micro:bit MicroPython package](https://github.com/wendlers/atom-microbit-micropython) - BBC micro:bit MicroPython support package for the Atom editor.
- [Thonny micro:bit](https://bitbucket.org/KauriRaba/thonny-microbit/wiki/installation-guide) - Plug-in for [Thonny](http://thonny.org), a Python IDE for beginners.
- [JetBrains IDEA/PyCharm IDE plugin](https://plugins.jetbrains.com/plugin/9777-micropython-support) - Support for MicroPython devices in IntelliJ IDEA and PyCharm.
- [uPyCraft](https://www.gitbook.com/book/dfrobot/upycraft/details) - A micro:bit compatible MicroPython IDE for Windows/Mac, designed with a simple and convenient interface.
- [CodeSpace](https://make.firialabs.com) - An online MicroPython IDE for micro:bits, with bundled learning resources.

##### MicroPython Libraries

- [Servo](https://github.com/microbit-playground/microbit-servo-class) - Class for controlling servos on the micro:bit via PWM.
- [PCA9685](https://github.com/gingemonster/PCA9685-Python-Microbit) - Class for using the PCA9685 16-Channel 12-bit PWM/Servo Driver via I2C.
- [MAX7219 7-segment](https://github.com/microbit-playground/matrix7seg) - Module for using a 7-segment display driven by a MAX7219 chip via SPI.
- [MAX7219 matrix](https://github.com/titimoby/microbit4all/blob/master/libraries/matrix7219.py) - Module for using a 8x8 Leds Matrix driven by a MAX7219 chip via SPI.
- [SSD1306](https://github.com/fizban99/microbit_ssd1306) - Library to control the OLED SSD1306 128x64 I2C with a micro:bit.
- [SSD1306 7seg](https://github.com/fizban99/microbit_ssd1306_7seg) - Library to use an SSD1306 OLED display as a 7 segment display.
- [SSD1306 SPI](https://github.com/fizban99/microbit_ssd1306spi) - Library to control the OLED SSD1306 128x64 display with a micro:bit via SPI.
- [SSD1306](https://github.com/Afantor/Microbit_SSD1306_OLED) - Library to control the SSD1306 display via I2C.
- [HT16K33](https://bitbucket.org/thesheep/microbit-ht16k33) - Library for the HT16K33 LED matrix driver in multiple configurations (16x8, 8x8 or 8x8x2).
- [HC-SR04](https://github.com/fizban99/microbit_hcsr04) - Library to read the distance from a HC-SR04 ultrasonic sensor using the SPI peripheral.
- [US-100](https://github.com/fizban99/microbit_us100) - Library to read the distance from a US-100 ultrasonic sensor via UART.
- [KY038](https://github.com/fizban99/microbit_ky038) - Library to calibrate and use a sound sensor KY038, including clap counter functionality.
- [Nokia 5110 PCD8544 LCD](https://github.com/matneee/microbit-nokia5110-PCD8544-lcd) - Fast controller for Nokia 5110 LCDs.
- [MPL115A1](https://github.com/hackscribble/microbit-MPL115A1-barometer) - Class to read the pressure and temperature readings from the NXP MPL115A1 SPI sensor.
- [24LCxxx EEPROM](https://github.com/matneee/microbit-I2C-EEPROM-24LCxxx-Read-Write) - Example micro:bit functions to read and write to a Microchip I2C EEPROM.
- [ULN2003](https://github.com/IDWizard/uln2003) - Module to drive stepper motors via ULN2003 darlington transistors.
- [Bosch BME280](https://github.com/jemerlia/microbit-BoschBME280-P-T-and-H-Sensor) - Module for Bosch BME280 Pressure, Temperature and Humidity Sensor via I2C.
- [Pixy](https://github.com/liamkinne/microbit-pixy) - Interface module for using the Pixy cam with the BBC micro:bit.
- [MB1013](https://github.com/liamkinne/microbit-mb1013) - Module for the MB1013 ultrasonic sensor controlled via UART.
- [MY9221](https://github.com/mcauser/microbit-my9221) - Library for 10 segment LED bar graph modules using the MY9221 LED driver.
- [AM2320](https://github.com/mcauser/microbit-am2320) - Library for interfacing with an Aosong AM2320 temperature and humidity sensor over I2C.
- [DHT12](https://github.com/mcauser/microbit-dht12) - Library for interfacing with an Aosong DHT12 temperature and humidity sensor over I2C.
- [TM1637](https://github.com/mcauser/microbit-tm1637) - Library for quad 7-segment LED display modules using the TM1637 LED driver.
- [micro:bit MIDI](https://github.com/liamkinne/microbit-midi) - Module to enable talking to MIDI devices on the BBC micro:bit.
- [Kitronik Motor Driver Board](https://github.com/MrYsLab/kitronik_motor_board) - Class to control the Kitronik motor driver board.
- [microbit python libs](https://github.com/shaoziyang/microbit-lib) - Growing collection of modules, including TM1637/TM1650 7-seg LEDs, OLED 128x64, LCD1602, AT24XX EEPROM, DS1302/DS1307/DS3231 RTC, NeoPixel drivers, APDS9930 Digital Proximity and Ambient Light Sensor, BME280 humidity and pressure sensor, BMP280/BMP180 pressure sensors.

##### Python Libraries

- [MicroPeri](https://github.com/c0d3st0rm/microperi) - Run Python programs on your computer with the same micro:bit MicroPython API and connecting a micro:bit as an external peripheral device or sensor.
- [microbit_stub](https://github.com/casnortheast/microbit_stub) - Python package that emulates the micro:bit as defined by the micro:bit MicroPython API.
- [bluezero](https://github.com/ukBaz/python-bluezero) - Python package to interface with Bluetooth devices, with examples for the micro:bit.
- [bitio](https://github.com/whaleygeek/bitio) - BBC micro:bit I/O library for Python. It allows you to run code in Python on a PC/Mac/Linux/Raspberry Pi and interact directly with the micro:bit.

##### Python Programming Tools

- [uFlash](https://github.com/ntoll/uflash/) - Utility for flashing the micro:bit with Python scripts and the MicroPython runtime.
- [MicroREPL](https://github.com/ntoll/microrepl) - A REPL client for MicroPython running on the BBC micro:bit.
- [MicroFs](https://github.com/ntoll/microfs) - Simple command line tool and module for interacting with the limited file system provided by MicroPython on the micro:bit.
- [Jupyter kernel for the micro:bit](https://github.com/takluyver/ubit_kernel) - Package that allows Jupyter interfaces to run MicroPython code directly on the micro:bit.

### JavaScript and MakeCode

- [MakeCode](https://makecode.microbit.org) - This block and text editor for the micro:bit provides an in-browser emulator, a Blocks interface, and JavaScript (TypeScript) editor.
	- [MakeCode Windows 10 App](https://www.microsoft.com/store/apps/9pjc7sv48lcx) - Windows 10 application for micro:bit MakeCode.
- [Espruino JavaScript](http://www.espruino.com/MicroBit) - JavaScript interpreter for microcontrollers. It also offers a WebIDE for written code and blocks.

##### MakeCode Extensions

To add an extension find the "Extensions" option in the Settings menu or the "Advance" toolbox category.

The extensions included in the official list below can be found by searching for their name in the "Extensions" screen.

- [MakeCode Extensions Gallery](https://makecode.microbit.org/extensions) - Official list of extensions available directly within MakeCode.

The following extensions can be added into MakeCode by copying the GitHub URL and pasting it into the search box of the "Extensions" screen.

- [BlueDot](https://github.com/Microsoft/pxt-bluedot) - PXT package to support the BlueDot app - beta.
- [Kitronik Servo Lite](https://github.com/KitronikLtd/pxt-kitronik-servo-lite) - Blocks that support Kitronik Servo:Lite board for the micro:bit.
- [Kitronik I2C 16 Servo](https://github.com/KitronikLtd/pxt-kitronik-I2C-16-servo) - Blocks for driving the Kitronik I2C 16 servo expansion board.
- [Kitronik motor driver](https://github.com/KitronikLtd/pxt-kitronik-motor-driver) - Blocks for driving the Kitronik micro:bit motor driver board.
- [Lego Power Functions](https://github.com/philipphenkel/pxt-powerfunctions) - Control your LEGO® Power Functions motors using your micro:bit with an infrared LED.
- [Invent robot](https://github.com/techcampuk/pxt-invent) - This library provides a Microsoft PXT package for Invent robot.
- [ubirch NB-IoT](https://github.com/ubirch/pxt-ubirch) - Package for sending signed data messages to the ubirch backend.
- [CCS811](https://github.com/ADataDate/pxt-airQuality) - Makecode Package for the CCS811 Air Quality Sensor.
- [DS1307](https://github.com/Tinkertanker/pxt-ds1307-microbit) - Tinkercademy MakeCode package for using the DS1307 RTC (Real-Time Clock).
- [HT16K33](https://github.com/Tinkertanker/pxt-ht16k33-alnum4) - Tinkercademy MakeCode Package for the HT16K33 I2C Alphanumeric Display (beta).
- [HoneyBit](https://github.com/HoneycombKits/pxt-HoneyBit) - A Honeycomb kits package for micro:bit MakeCode.
- [Bluetooth beacons](https://github.com/kshoji/pxt-bluetooth-beacons) - Allows the micro:bit to act as iBeacon / AltBeacon advertiser.
- [LumexOLED](https://github.com/lioujj/pxt-oled) - Package designed for Lumex OLED display.
- [MakerBit](https://github.com/1010Technologies/pxt-makerbit) - Blocks that support Roger Wagner's MakerBit board including Serial MP3, I2C LCD 1602, and ultrasonic.
- [MakeCode Extensions](https://github.com/makecode-extensions) - Growing collection of packages, including TM1637/TM1650 7-seg LEDs, OLED 128x64, LCD1602, AT24XX EEPROM, DS1302/DS1307 RTC, APDS9930 Digital Proximity and Ambient Light Sensor, BH1750 digital ambient light sensor, BME280 humidity and pressure sensor, BMP280/BMP180 pressure sensors.
- [BMP085](https://github.com/sabas1080/uBit_BMP085) - Package to control the BMP085 or BMP180 pressure and altitude sensors.
- [SHT2X](https://github.com/Tinkertanker/microDriver_SHT2x) - Driver for SHT20, SHT21, SHT25 digital sensor, enabling the the micro:bit to obtain temperature and relative humidity from these sensors.
- [VL53L0X](https://github.com/Tinkertanker/pxt-range-vl53l0x) - Package to calculate distances using a VL53L0X Time-of-Flight ranging sensor.
- [KY-040](https://github.com/Tinkertanker/pxt-rotary-encoder-ky040) - Package for using the KY-040 rotary encoder.
- [PCA9685](https://github.com/Tinkertanker/uDriver_PCA9585) - Package to control the PCA9685, a 16-channel PWM controller, with included servo support.
- [MakerBit-Touch](https://github.com/1010Technologies/pxt-makerbit-touch) - Touch sensing package for the capacitive touch sensor controller MPR121.
- [MAX7219 8x8](https://github.com/alankrantas/pxt-MAX7219_8x8) - Control the MAX7219 LED matrix display module with an 8x8 LED matrix.

##### Node.js Libraries

- [node-bbc-microbit](https://github.com/sandeepmistry/node-bbc-microbit) - Control a micro:bit from Node.js using BLE.
- [node-bbc-microbit-io](https://github.com/sandeepmistry/node-bbc-microbit-io) - Johnny-Five (JavaScript Robotics and IoT programming framework) micro:bit IO Plugin.

##### JavaScript Browser Libraries

- [microBit.js](https://github.com/antefact/microBit.js) - JavaScript library to interact with BBC micro:bit using web bluetooth API.

##### JavaScript Programming Tools

- [PXT Command Line Tool](https://makecode.com/cli) - Use the command line to program the micro:bit with MakeCode JavaScript. You can also run a local version of the MakeCode online editor (part of Microsoft's PXT).

### C/C++

- [C/C++ runtime](https://lancaster-university.github.io/microbit-docs/) - Guidance on how to start using the runtime in C/C++ including full documentation of the APIs, drivers, and types that make up the micro:bit runtime. Bluetooth documentation includes a link to the original `*.hex` file that ships on the micro:bit devices.
- [Arduino nRF5](https://github.com/sandeepmistry/arduino-nRF5/) - Arduino Core for Nordic Semiconductor nRF5 based boards, including the micro:bit.

##### C/C++ Editors

- [Micro:Pi](https://github.com/Bottersnike/Micro-Pi) - C/C++ editor for the micro:bit with serial monitor and deploy functionality. Written in Python with an installer (ATM Linux only, but could be manually installed in any OS) that includes all dependencies.
- [PlatformIO](https://docs.platformio.org/en/latest/boards/nordicnrf51/bbcmicrobit.html) - Embedded IDE with support for the micro:bit using the Arduino or Mbed software stack.

##### C/C++ Libraries

- [OneWire](https://github.com/adamboardman/microbit-onewire) - BBC micro:bit OneWire Library, based upon Erik Olieman's Mbed DS1820 lib.
- [neopixel](https://github.com/elmorg/uBit_neopixel) - Library for using NeoPixels with the BBC micro:bit.
- [micro:bit Screen](https://github.com/ht-deko/microbit_Screen) - Arduino LED Screen library for micro:bit.
- [Adafruit Arduino micro:bit library](https://github.com/adafruit/Adafruit_Microbit) - Wrapper code and examples for using micro:bit with Arduino IDE.
- [RTCC MCP7941X](https://os.mbed.com/users/euxton/code/microbit-RTCC-MCP7941X/) - Program to interface BBC micro:bit to a MCP79410 RTCC (Real Time Clock Calendar) module.
- [AS-289R2](https://os.mbed.com/users/MACRUM/code/microbit_AS-289R2/) - AS-289R2 thermal printer Mbed library for micro:bit.
- [SHT2X](https://github.com/Tinkertanker/microDriver_SHT2x) - Driver for SHT20, SHT21, SHT25 digital sensor, enabling the the micro:bit to obtain temperature and relative humidity from these sensors.
- [VL53L0X](https://github.com/Tinkertanker/pxt-range-vl53l0x) - Driver for the VL53L0X Time-of-Flight ranging sensor.
- [KY-040](https://github.com/Tinkertanker/pxt-rotary-encoder-ky040) - Library for using the KY-040 rotary encoder.
- [PCA9685](https://github.com/Tinkertanker/uDriver_PCA9585) - Driver for the PCA9685, a 16-channel PWM controller, with included servo support.

### Other micro:bit Languages

Other programming languages capable to program the micro:bit.

- [Touch Develop](https://www.microbit.co.uk/create-code#touchdevelopEditor) - Flexible, text-based programming language with an interactive visual component.
- [Rust](https://github.com/SimonSapin/rust-on-bbc-microbit) - Article describing the experience and steps of compiling Rust code for the micro:bit with and without interaction with the runtime DAL.
- [Forth](https://wiki.forth-ev.de/doku.php/en:projects:microbit:start) - Forth, a stack-based language, for the BBC micro:bit.
- [Pascal](http://wiki.freepascal.org/micro:bit) - Free Pascal compiler that can target the ARM embedded platform, including the micro:bit.
- [Ada](https://github.com/AdaCore/Ada_Drivers_Library/tree/master/examples/MicroBit) - Instruction on how to setup the Ada development environment for the micro:bit.
- [Sniff](http://www.sniff.org.uk/p/bbc-microbit.html) - Sniff is a "Scratch-like" programming language that's designed to help Scratchers move gently from Scratch to more conventional languages.
- [Lisp](http://www.ulisp.com/show?2672) - An interpreter for the classic AI programming language for the BBC micro:bit.
- [C# / F#](https://github.com/kekyo/IL2C) - IL2C is a translator implementation of .NET intermediate language to C language, with C# and F# examples for the micro:bit.
- [TinyGo](https://github.com/aykevl/tinygo) - ([examples](https://github.com/hybridgroup/tinygo-zoo)) Project to bring Go to microcontrollers and small systems, with out-of-box support for the BBC micro:bit. 

### Other Interaction Languages

These languages do not program the micro:bit directly, but can be used to create programs that interface with a micro:bit.

- [Kodu Controller](http://www.kodugamelab.com/bbc-microbit/) - Enables interacting with the micro:bit from Kodu Game Lab.
- [Simulink Coder Support Package](http://www.mathworks.com/help/supportpkg/microbit/) - Package that enables you to create Simulink models and automatically generate and deploy code on the micro:bit.
- [micro:bit for Dyalog APL on the Pi](https://github.com/APLPi/microbit) - Tools for using the micro:bit (via MicroPython serial connection) with the Dyalog APL programming language on the Raspberry Pi.
- [Gobot](https://gobot.io/documentation/platforms/microbit/) - Framework for the Go programming language to program devices in the real world. It can access the micro:bit via Bluetooth LE.
- [Microbit-Unity](https://github.com/bLiGM/Microbit-Unity) - Unity scripts to allow the BBC Microbit to be used as a Unity Controller.
- [Haxe node BBC micro:bit](https://github.com/MatthijsKamstra/hx-node-bbc-microbit) - Control a BBC micro:bit from Node.js using BLE and the Haxe programming language.
- [App Inventor + IoT](http://iot.appinventor.mit.edu/#/microbit/microbitintro) - Control a micro:bit via Bluetooth with App Inventor, a visual programming environment for Android applications.
- [BlockyTalkyBLE](http://www.playfulcomputation.group/blockytalkyble.html) - MakeCode and App Inventor extension that makes it easy to connect AppInventor mobile phone apps with the BBC micro:bit wirelessly over Bluetooth.
- [DroidScript micro:bit Plugin](https://play.google.com/store/apps/details?id=org.droidscript.microbit) - Allows you you to control the BBC micro:bit remotely from your own DroidScript apps (Android apps written in JavaScript).
- [CBMicroBit](https://github.com/Louismac/CBMicroBit) - CoreBluetooth wrapper in C++ that connects a micro:bit to a computer running macOS using BLE and outputs over OSC (can be used standalone, or as a C++ or Objective C library).
- [Swift](https://github.com/phwallen/microbit-swift) - An application programming interface written in Swift for use with the micro:bit. It allows programs written for Apple devices to communicate with the micro:bit using BLE.
- [Node-RED](https://github.com/seanmtracey/node-red-contrib-bitio-wrapper) - A node-red (flow-based visual programming) module that wraps some of the functionality of the Python/MicroPython Bitio Library.


## Programming Tools

- [Vagrant Development Environment for C/C++, MicroPython and Makecode](https://github.com/carlosperate/microbit-dev-env) - Creates a virtual machine with the toolchain required to create C/C++ programs, develop/compile MicroPython, and create packages for MakeCode.
- [micro:bit uploader](https://www.touchdevelop.com/microbituploader) - Windows application that monitors your Downloads folder and flashes any new programs to the micro:bit.


## Mobile Apps

- [Official Android App](https://play.google.com/store/apps/details?id=com.samsung.microbit) - ([Source Code](https://github.com/Samsung/microbit)) Pair, program and flash programs to the micro:bit via Bluetooth.
- [Official iOS App](https://itunes.apple.com/gb/app/micro-bit/id1092687276) - Pair, program and flash programs to the micro:bit via Bluetooth.
- [Official Swift playgrounds](https://microbit.org/guide/swift-playgrounds/) - Swift Playgrounds is an app for the iPad that helps teach people to code in the Swift language using interactive 'books'.
- [micro:bit Blue](https://play.google.com/store/apps/details?id=com.bluetooth.mwoolley.microbitbledemo) -  ([Source Code](https://github.com/microbit-foundation/microbit-blue)) Android app that contains a series demos for interacting with the micro:bit using Bluetooth.
- [Bitty Software Apps](http://www.bittysoftware.com/apps.html) - Diverse collection of Android and iOS apps, going from data logging to audio pranks, you'll certainly find something of interest.
- [Insight Mr Bit](http://www.insightresources.co.uk/microbit/page63.html) - ([iOS](https://itunes.apple.com/gb/app/insight-mr-bit/id1175915875)) Create simple programs in plain English to control the BBC micro:bit to do lots of useful things.
- [micro:bit Xamarin](https://github.com/sumitgouthaman/microbit-ble-mobile) - Open source Android app that communicates with the micro:bit over BLE and gets sensor data. A good example of using Xamarin (a cross platform mobile framework) with the micro:bit.
- [bitty blue](http://www.bittysoftware.com/apps/bitty_blue.html) - iOS and Android app that provides a collection of fun things to do with a BBC micro:bit (or compatible device) and Bluetooth.
- [micro:bit logger](https://play.google.com/store/apps/details?id=nl.defbu.mblogger) - Android app that enables users to log data from the BLE services and export it to a file.
- [Kitronik Move](https://play.google.com/store/apps/details?id=com.kitronik.blemove) - Android app that presents a D-Pad interface to control a micro:bit over Bluetooth LE.
- [nRF Connect](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp) - A generic tool for Android that allows you to scan, advertise and explore BLE devices. It supports the micro:bit by including information on the micro:bit services, custom macros and more.
- [Tickle](https://tickleapp.com) - iOS app to program a large selection of devices, including the micro:bit, connecting them all together, so that they can interact with each other.
- [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal) - Android app capable to send and receive micro:bit Bluetooth UART data.
- [micro:bit Slither](https://github.com/novucs/microbit-slither) - Multiplayer snake game on Android, controlled with micro:bits via Bluetooth.
- [Micro:bit Explorer](https://phwallen.github.io/microbit-explorer/) - A Swift Playground Book that introduces computer fundamentals in a visual way, it allows you to enter machine code or assembly and see how it executes and how the micro:bit registers are affected.



## ChromeOS Apps

- [Quiz:bit](https://chrome.google.com/webstore/detail/quizbit/hfnanbphehfnlcpkelfnkmfdljphlmna) - ([Source Code](https://github.com/lancaster-university/quiz-bit)) BBC micro:bit programs and a matching application for providing a quiz-voter-style service using micro:bits as the controls.
- [bitty blue](http://www.bittysoftware.com/apps/bitty_blue.html) - Play with 3D "PolySquiggles", use as a compass, have fun with the buttons, send images or text to the LED display, connect and control electronic circuits, and all via Bluetooth.
- [bitty data logger](http://www.bittysoftware.com/apps/bitty_data_logger.html) - Capture and chart accelerometer, magnetometer and temperature data from your micro:bit's internal sensors over Bluetooth.
- [microbit-chrome](https://github.com/Microsoft/microbit-chrome) - Prototype chrome addon that exposes the micro:bit's serial output to web pages like the MakeCode editor.


## Interface Chip

The USB Interface Chip is the microcontroller placed close to the battery connector. It provides the USB mass storage capability to load the micro:bit firmware using the Operating System file explorer.

- [microbit.org Developer Community Info](http://tech.microbit.org/software/daplink-interface/) - This micro:bit Developer Community page contains information about the Interface Chip DAPlink and the USB interface.
- [DAPLink on micro:bit](https://www.mbed.com/en/development/hardware/prototyping-production/daplink/daplink-on-kl26z/) - The DAPLink is the default software running on the Interface Chip, this page contains information, update instructions, and the latest firmware.
- [DAPLink source code](https://github.com/ARMmbed/DAPLink) - Source code for the Mbed DAPLink, contains the build configuration for the micro:bit.
- [J-Link OB Firmware](https://www.segger.com/bbc-micro-bit.html) - Offers the same flashing functionality than the DAPLink and expands it to include J-Link debugging.
- [pyOCD](https://github.com/mbedmicro/pyOCD) - Python library for programming and debugging ARM Cortex-M microcontrollers, like the one included in the micro:bit, using the CMSIS-DAP provided by the Interface Chip.
- [DAP.js](https://github.com/ARMmbed/dapjs) - JavaScript (Node.js and WebUSB) interface to DAP-CMSIS over USB/HID, meant to provide a subset of functionality of pyOCD.


## Hardware

- [Hardware Design](https://github.com/bbcmicrobit/hardware) - Schematics and bill of materials for the BBC micro:bit.
- [micro:bit Reference Design](https://github.com/microbit-foundation/microbit-reference-design) - Hardware design files for a board 100% binary compatible with the micro:bit. Created to help make your own micro:bit derived designs.
- [micro:bit Badge](https://github.com/make-zurich/micro-bit-badge) - Open Source PCB for the micro:bit with a battery holder, buzzer, extension edge connector and pins breaks out.
- [Eagle micro:bit Edge Part](https://github.com/proto-pic/micro-bit-eagle-libraries) - Eagle library from Proto-Pic for the micro:bit edge connectors.
- [Kicad micro:bit Connector](https://github.com/anthonykirby/kicad_microbit_connector) - KiCad component library and footprint library for a micro:bit edge-connector socket.
- [SparkFun Breakout Board](https://github.com/sparkfun/Micro_Bit_Breakout) - Open source files for the SparkFun micro:bit Breakout Board.
- [SparkFun moto:bit](https://github.com/sparkfun/Micro_Bit_Moto_Bit) - Open source files for the SparkFun moto:bit, a board to provide a robotics platform.
- [SparkFun weather:bit](https://github.com/sparkfun/Micro_Bit_Weather_Bit) - Open source files for the SparkFun weather:bit, a board to provide a weather station.
- [SparkFun gamer:bit](https://github.com/sparkfun/Micro_Bit_Gamer_Bit) - Open source files for the SparkFun gamer:bit, a board to provide a game system.
- [NeoBit](https://github.com/ppelleti/NeoBit) - Open source board that lets you hook up NeoPixel and DotStar LEDs to a BBC micro:bit, also contains a headphone jack and a couple of slide potentiometers for input. 


## 3D Printing

- [Microbot Case](http://www.thingiverse.com/thing:1434797) - Case for the micro:bit in the shape of a robot.
- [micro:bit Stand](http://www.thingiverse.com/thing:2144500) - Stand for the micro:bit.
- [micro:bit Rover](https://www.myminifactory.com/object/microbit-rover-27013) - Multiple 3D printable parts to build a micro:bit robot rover.
- [micro:Racing](https://www.myminifactory.com/object/micro-racing-18280) - Driving wheel case for the micro:bit.
- [Binary Watch](https://www.myminifactory.com/object/binary-watch-15257) - Watch case and strap for the micro:bit.
- [micro:bit Compass](https://www.myminifactory.com/object/micro-bit-compass-18994) - Compass case for the micro:bit.
- [A4 folder holder](https://www.myminifactory.com/object/micro-bit-a4-folder-holder-22039) - Device holder to store your micro:bit in a A4 school folder.
- [mibot drawing robot](https://www.myminifactory.com/object/mibot-drawing-robot-36030) - Chassis for a painting robot powered by a BBC micro:bit and its motor driver board.
- [Robottillo:bit](https://www.myminifactory.com/object/robottillo-bit-46478) - Case which looks like a small robot. Two versions available, with a rear protective cover or with a perforated cover for the pins.
- [Battery pack holder](https://www.thingiverse.com/thing:2666671) - Simple battery clip for the BBC micro:bit.
- [micro:bit holder](https://www.thingiverse.com/thing:2750805) - Stand that holds 20 micro:bit boards vertically, useful in a classroom setting.
- [BBC micro:bit Case V2](https://www.thingiverse.com/thing:3028078) - A slim, nice looking, and functional snap-together case that protects all sides and corners.
- [Otto Robot](https://www.thingiverse.com/thing:2786066) - Otto chassis for the microbit to make a bidepad robot with a robitbit accessory.
- [micro:bit Tracking Car](https://www.thingiverse.com/thing:3270962) - A line follower chassis for the micro:bit.
- [Walking Robot V1](https://www.thingiverse.com/thing:3300339) - Add-on to the bit:booster that makes a simple walking robot using two continuous servos.


## CAD

- [Kitronik CAD Resources](https://www.kitronik.co.uk/blog/bbc-microbit-cad-resources/) - BBC micro:bit CAD model from Kitronik.
- [Proto-PIC CAD Resources](https://www.proto-pic.co.uk/micro-bit-resources.html) - Proto-PIC products CAD resources.


## 2D Design

- [micro:bit Fritzing Part](https://github.com/topshed/FritzingParts) - Richard Hayler collection of Fritzing parts contains a model for the micro:bit.
- [micro:bit-o-matic](https://pycomic.github.io/microbit.html) - Easily create micro:bit illustrations with custom LED matrix messages.
- [micro:bit SVG](https://github.com/microbit-foundation/microbit-svg) - A detailed SVG (Scalable Vector Graphics) drawing of the BBC micro:bit.
- [MonkMakes micro:bit Diagramming Kit](https://github.com/simonmonk/mm_mb_diagramming_kit) - An SVG file template for drawing BBC micro:bit wiring diagrams using alligator clips.
- [Pixel Art](http://www.steamlearninglabs.com/blog/2018/2/26/microbit-inspired-pixel-art-download-use) - micro:bit-inspired fan art made with "Make 8 Bit Art".


## Projects

All these projects contain steps and resources required for reproduction.

- [JUST DO IoT](https://hackaday.io/project/12164-just-do-iot) - Connect the micro:bit to the LoRaWAN network, includes an open source hardware micro:bit connector board.
- [Micro:Bob](https://hackaday.io/project/8643-microbob) - Simple bipedal robot controlled by a micro:bit.
- [Coffee Timer](https://www.norwegiancreations.com/2016/09/coffee-timer-part-1-the-first-prototype-based-on-the-bbc-microbit/) - ([Part 2](https://www.norwegiancreations.com/2016/10/coffee-timer-part-2-low-power-wireless-on-the-bbc-microbit/), [Part 3](https://www.norwegiancreations.com/2016/11/coffee-timer-part-3-enclosures/)) Three part article describing how to augment a coffee maker with an micro:bit indicator, options for low power communication, and creating a custom enclosure.
- [Thermal Printer](http://www.suppertime.co.uk/blogmywiki/2016/12/microbit-thermal/) - Connecting and using a Sparkfun thermal till-roll printer.
- [Telescopic Light Sword](https://www.myminifactory.com/object/telescopic-lightsword-with-micro-bit-14598) - Project shows how to make your own Light Sword with the micro:bit, electronics, and 3D printed parts.
- [Micro Simon](http://mrtomsworld.blogspot.co.uk/2017/01/micro-simon.html) - Programming and connecting a micro:bit to a vintage MB Simon game.
- [Alexa Weather On micro:bit](https://www.hackster.io/chen-tiebiao/weather-on-micro-bit-c79c19) - Creating an Amazon Alexa skill where the current weather can be asked and the result displayed on the micro:bit.
- [BBC Microbit Balloon Tracker](http://www.daveakerman.com/?p=2019) - Making a ballon tracker with a micro:bit connected to GPS and a LoRa transceiver to track and transmit its position.
- [SonicPixels](https://github.com/jrmedd/SonicPixels) - BBC micro:bit and Max frameworks for triggering multiple speakers in a grid arrangement.
- [Little Bug Bit](http://goo.gl/eEFhcy) - Low cost micro:bit buggy.
- [HandShake](https://sites.google.com/site/hardwaremonkey/home/handshake) - Project designed to enable unique gesture recognition for people with limited control of their motion.
- [Mega:Bit](http://www.makerspace-uk.co.uk/megabit/) - Scaled up micro:bit with the 5x5 LED matrix and buttons, connected to a real micro:bit.
- [Scrolling display](https://meanderingpi.wordpress.com/2017/09/16/bbc-microbit-scrolling-display/) - Create a display screen using a number of micro:bits communicating via radio.
- [Ironman Arc Reactor](https://www.kitronik.co.uk/blog/halo-ween-ironman-arc-reactor) - Choose between two different versions (Mk I and Mk II) ready to 3D print and build.
- [microbit-beacon-finder](https://github.com/kshoji/microbit-beacon-finder) - The micro:bit finds various types of BLE Beacons, and displays their ID to the LEDs.
- [Build A Klawsome micro:bit Controlled Tank](https://www.kitronik.co.uk/blog/klawsome-microbit-controlled-tank/) - Tutorial on how to design a build a perspex micro:bit tank.
- [micro:bit Hovercraft](http://www.instructables.com/id/Make-a-Cool-Microbit-Hovercraft-Together/) - A hovercraft, which runs both in the water and on the ground. Uses 2 motors to blow air underneath to support the hovercraft body and 2 motors in the end to control its direction.
- [ZIP Halo Compass](https://www.kitronik.co.uk/blog/bbc-microbit-zip-halo-compass) - A Christmas themed micro:bit ZIP Halo Compass, with a 3D printed and laser cut case.
- [Micro:Boy](https://hackaday.io/project/27757-microboy) - Hardware project to code and play arcade games on the micro:bit.
- [Alexa, Ask micro:bit to Turn LED Light](https://medium.com/@ferrygunawan/alexa-ask-microbit-to-turn-led-light-61ed668a0321) - Project walk through to control with Alexa an RGB LED connected to a micro:bit.
- [OpenGestureControl](https://opengesturecontrol.github.io) - A Linux application which interacts with the BBC micro:bit to give hand prothesis users the ability to control their desktop computer using gestures.
- [micro:bit spectrum](https://github.com/linker3000/micro-bit_spectrum) - Circuit and code to display an audio spectrum bar chart on the BBC micro:bit.
- [micro:bit TVPong](https://github.com/linker3000/Microbit-TVPong) - Play the classic Pong game on a TV - using BBC Microbits as paddles, Bluetooth also supported.
- [Bluetooth Low Energy Remote Control for Spotify](https://www.hackster.io/josejuansanchez/bluetooth-low-energy-remote-control-for-spotify-3438d1) - This project allows you to configure your micro:bit to work as a Bluetooth Low Energy remote control for Spotify on macOS.
- [Stirling Blue](https://www.element14.com/community/community/design-challenges/bluetoothunleashed/blog/2018/05/07/stirling-blue-project-description-blog-1) - An extensive project to examine Stirling engine operation and performance. A micro:bit is used to create a custom keyboard and LCD interface that communicates with other parts of the project.
- [Micro:Gamer](https://hackaday.io/project/47760-microgamer) - A portable game console based on the micro:bit board. It features a 128x64 monochrome OLED screen, six buttons, a buzzer for sound, and a 2xAAA battery holder.
- [µBOSS](https://www.element14.com/community/community/project14/test-instrumentation/blog/2018/10/12/%C2%B5boss-test-instrumentation-microbit) - Turning a BBC micro:bit into a test instrument by displaying all the sensor readings on an LCD and packaging it into a 3D printed box.
- [DIY 3D Virtual Reality System](https://sites.google.com/site/colinord/Home/3d-virtual-reality-hmd-and-controller-project) - Using two micro:bits for head and hand orientation tracking.
- [Robot Arm Rover](https://github.com/AMoazeni/Robot-Arm-Rover) - A gesture controlled Robot Arm Buggy using the micro:bit accelerometer and radio.

### Project Collections

- [microbit.co.uk Site Index](https://www.microbit.co.uk/index) - The microbit.co.uk website contains an extensive list with all their projects and tutorials.
- [hackster micro:bit community](https://microbit.hackster.io) - This hackster community contains user submitted projects for the micro:bit.
- [MakeCode Projects](https://makecode.microbit.org/projects/) - List of micro:bit projects you can do with the MakeCode editor.
- [Tinkercademy Projects](https://tinkercademy.com/microbit/) - Collection of projects using the micro:bit and Tinkercademy Tinker Kit.
- [Raspberry Pi micro:bit Projects](https://projects.raspberrypi.org/en/projects?technologies%5B%5D=microbit) - Collection of Raspberry Pi and micro:bit projects from the Raspberry Pi Foundation.
- [Hackaday.io micro:bit Projects](https://hackaday.io/projects?tag=micro%3Abit) - Projects using the micro:bit tag in Hackaday.io, a collaborative hardware development community.
- [Maker.io micro:bit projects](https://www.digikey.com.au/en/maker/search-results?y=13825c8674444e22884d8d26197819d1&t=54c4be4fbd2f4f748d1eacf05fd3b5b0&g=newest&page=1) - All the micro:bit projects posted to Maker.io, a playground for makers.
- [Electromaker micro:bit projects](https://www.electromaker.io/projects?platform=microbit) - All the micro:bit projects posted to Electromaker, a platform for makers to showcase their projects.


## Articles

Useful Articles for developing on the micro:bit.

- [Offline C/C++ Development With The micro:bit](http://www.i-programmer.info/programming/hardware/9654-offline-cc-development-with-the-microbit-.html)
- [Sending 'commands' from a micro:bit over Bluetooth](http://bluetooth-mdw.blogspot.co.uk/2016/07/sending-commands-from-microbit-over.html)
- [Modelling micro:bit data with the Bitty Data Logger App](https://www.stem.org.uk/elibrary/community-resource/289686/modelling-microbit-data-bitty-data-logger-app)
- [Getting Started with the micro:bit Bluetooth IO Pin Service](https://ukbaz.github.io/howto/ubit_ble_profile.html)
- [Using MQTT-SN over BLE with the BBC micro:bit](https://blog.benjamin-cabe.com/2017/01/16/using-mqtt-sn-over-ble-with-the-bbc-microbit)
- [The First Video Game on the BBC micro:bit [probably]](https://hackernoon.com/the-first-video-game-on-the-bbc-micro-bit-probably-4175fab44da8) - Creating a game for the micro:bit, the MicroPython changes needed to increase performance and a general profile of its resources.
- [Custom BLE services with micro:bit](https://www.hackster.io/pelikhan/custom-ble-services-with-micro-bit-6c9879) - Build your own Bluetooth low energy services and bundle them as PXT/MakeCode blocks that beginners can use.
- [Excel and micro:Bit - Hacking for fun and creativity!](https://techcommunity.microsoft.com/t5/Excel-Blog/Excel-and-Micro-Bit-Hacking-for-fun-and-creativity/ba-p/63603) - Experiment to have some basic sensor data collected using the micro controller and then visualized in Excel.
- [Writing the second video game for the micro:bit in Rust](https://hackernoon.com/writing-the-second-video-game-for-the-micro-bit-in-rust-3cd8b5ab22d3) - Updating a micro:bit game and porting it to the Rust language.
- [Adding a new module to MicroPython](http://cigdemsengul.blogspot.co.uk/2017/04/offline-development-in-microbit-adding.html) - Article describing an experiment to add a new module into MicroPython for the micro:bit.
- [Become a Time Lord with the BBC micro:bit](https://blog.groklearning.com/become-a-time-lord-with-the-bbc-micro-bit-c4b8b4e2d747) - Using different timing mechanisms to run multiple things in MicroPython.
- [Debugging the micro:bit with pyOCD and GDB](https://docs.mbed.com/docs/mbed-os-handbook/en/5.4/debugging/debugging_microbit/) - Shows how to debug a micro:bit program using PyOCD and GDB.
- [Exploring the BBC micro:bit Software Stack](http://mattwarren.org/2017/11/28/Exploring-the-BBC-microbit-Software-Stack/) - What’s in it, what it does and how it all fits together.
- [Building the 1,000 BBC micro:bit Display](https://www.kitronik.co.uk/blog/building-the-bbc-microbit-matrix-display/) - Building a screen to show images from a thousand BBC micro:bits.
- [micro:bit Radio Packets](https://ukbaz.github.io/howto/ubit_radio.html) - Explanation of the MakeCode radio packet specification (built on top of the micro:bit runtime specification) and how to communicate between MakeCode and MicroPython programs via radio.
- [Synchronized Music on micro:bits](https://blog.flowblok.id.au/2018-02/synchronized-music-on-microbits.html) - Building a micro:bit mesh network so they can play music synchronized across a large area.
- [Using the Built-in Sensors](https://learn.adafruit.com/micro-bit-lesson-1-using-the-built-in-sensors) - Learn how to use the micro:bit's built-in accelerometer and magnetometer.
- [Read micro:bit data from Linux via Bluetooth (BLE)](https://github.com/alcir/microbit-ble) - Random notes and examples about micro:bit BLE and Linux.
- [Measure pressure with your micro:bit](https://www.instructables.com/id/Measure-Pressure-With-Your-Microbit/) - An inexpensive and easy to build device to perform pressure measurements and demonstrate Boyle's law with the micro:bit and BMP280 pressure/temperature sensor. 
- [IoT Cloud Access with Micro:bit over BLE for Remote Sensing](https://www.hackster.io/PSoC_Rocks/iot-cloud-access-with-micro-bit-over-ble-for-remote-sensing-351938) - Program BBC Micro:bit with mbed OS and remotely send data to cloud by utilizing BLE to smartphone/PC IoT cloud gateway.

### Article Collections

- [MultiWingSpan](http://www.multiwingspan.co.uk/micro.php) - Large collection of examples, instructions, and direction on how to use electronic components.
- [SparkFun micro:bit tutorials](https://learn.sparkfun.com/tutorials/tags/microbit) - Collection of tutorials from SparkFun, including comprehensive experiment guides for their kits.
- [BitIO blogs](http://warksjammy.blogspot.co.uk/2017/07/bitio-blogs-in-one-place.html) - Collection of blogs written about using the BitIO Python module to control the micro:bit.
- [micro:bit learning](http://www.microbitlearning.com/tag/microbit) - Blog with a section for articles showing how to use a wide selection of sensors with the micro:bit and the Arduino software.
- [Adafruit Learn micro:bit section](https://learn.adafruit.com/category/micro-bit) - Adafruit Learning System section for the BBC micro:bit.
- [BBC micro:bit - Kitronik University](https://www.kitronik.co.uk/blog/bbc-microbit-kitronik-university/) - A varied collection of micro:bit resources by Kitronik.
- [Maker.io micro:bit blog posts](https://www.digikey.com.au/en/maker/search-results?y=cb5252a72f0549558ffaaa2a80d3a1ed&t=54c4be4fbd2f4f748d1eacf05fd3b5b0&g=newest&page=1) - All the micro:bit articles posted in Maker.io, a playground for makers.
- [Physical computing with the BBC micro:bit](http://www.teachwithict.com/physical-computing.html) - How to use different electronic components with the micro:bit.
- [DF Robot micro:bit blog section](http://www.dfrobot.com/category-microbit.html) - Blog posts and articles about micro:bit from DF Robot.
- [ElecFreaks Learn](https://www.elecfreaks.com/learn-en/) - ElecFreaks collection of experiments, tutorials and material for the micro:bit.


## Videos

- [MicroMonsters](https://www.youtube.com/channel/UCK2DviDexh_Er2QYZerZyZQ) - YouTube channel with tutorials to learn to code with your family.
- [micro:bit and Bluetooth](https://www.youtube.com/playlist?list=PLYOCnwH2UtBzhJ2nvn_DM3itz6GNVwrDu) - YouTube playlist with Martin Woolley's Bluetooth videos.
- [Video Series from The Maker Movies](https://www.youtube.com/playlist?list=PLD0HD_3AJljXDWoasq2x5gHmkKeV7cc-P) - List of short, introductory videos for anyone wanting to get started with the micro:bit.
- [SparkFun video resources](http://sparkfuneducation.com/video-resources/microbit.html) - Growing list of video resources for the micro:bit.
- [SamCodes YouTube Playlist](https://www.youtube.com/playlist?list=PLumNlyd5JxxegaAVScP7Qm1AXPtJdGBCq) - Video tutorials showing how to  use different electronic components and features of the micro:bit.
- [Fun with Zephyr Project and BBC micro:bit](https://www.youtube.com/watch?v=ZZRbIpVJGns) - This presentation shows how Zephyr empowers the BBC micro:bit devices and its Bluetooth chip to do fun things.


## Books

- [micro:bit IoT In C](http://www.iot-programmer.com/index.php/books/micro-bit-iot-in-c)
- [Programming with MicroPython](http://shop.oreilly.com/product/0636920056515.do)
- [Getting Started with the micro:bit](http://shop.oreilly.com/product/0636920115267.do)
- [The Official BBC micro:bit User Guide](https://www.wiley.com/en-gb/The+Official+BBC+micro:bit+User+Guide+-p-9781119386735)
- [Programming the BBC micro:bit](http://simonmonk.org/prog-mb/)
- [Networking with the micro:bit (ebook)](https://microbit.nominetresearch.uk/networking-book/)
- [micro:bit in Wonderland](http://www.techagekids.com/2017/11/our-beginner-bbc-microbit-coding-craft-project-book-microbit-in-wonderland.html)
- [Beginning BBC micro:bit](https://www.apress.com/gb/book/9781484233597)


## Teaching Resources

- [microbit.org Teaching Resources](https://www.microbit.org/teach/)
- [Code Club micro:bit projects](https://www.codeclubprojects.org/en-GB/microbit/)
- [Make with the micro:bit by Technology Will Save Us](https://make.techwillsaveus.com/microbit)
- [IET micro:bit Teaching Resources](http://microbit.org/teach/iet/) - A series of resources created by the IET (Institution of Engineering and Technology) as part of their highly successful IET Faraday brand.
- [IET micro:bit case studies](https://faraday-secondary.theiet.org/stem-activities/microbit/microbit-case-studies/) - Booklets and video content to bring a variety of real-life applications of the micro:bit to life in your classroom.
- [Grok Learning](https://groklearning.com/microbit/) - Provides an online MicroPython code editor, Blockly visual programming, full micro:bit simulator, curriculum-aligned teaching material and auto-marked problems.
- [micro:bit For Primary Schools](http://mb4ps.co.uk) - Fully-customisable scheme of work and resources for use in the primary classroom.
- [101 Computing BBC micro:bit category](http://www.101computing.net/category/bbc-microbit/) - Computing challenges with the micro:bit to boost your programming skills or spice up your teaching of computer science.
- [micro:bit of Things](https://sites.google.com/view/microbitofthings/) - Notes on micro:bit project ideas for Key Stage 2 and 3.
- [The Brooke Primary School Space Programme](http://www.brooke.norfolk.sch.uk/brooke-space-programme/) - Project page documenting Brooke Primary School pupil's upcoming journey for launching a BBC micro:bit (on its own) into near-space, with experiments and sensor measurements.
- [FunWithMicrobit](https://github.com/MicrobitPolska/FunWithMicrobit) - FunWithMicrobit is a 6 hours workshop made by kids for the kids.
- [Year 7 micro:bit lessons](http://www.jonwitts.co.uk/year-7-microbit) - Lessons used to introduce students to the micro:bit and Python.
- [UCL’s BBC micro:bit Tutorials](http://microbit-challenges.readthedocs.io/en/latest/) - Tutorial sheets that introduce micro:bit features with practical examples provided to invite students to design solutions to problems.
- [BBC micro:bit and Kodu Interact](http://www.kodugamelab.com/resources/#microbit) - Kodu is a visual programming language made specifically for creating games and allow interaction with the micro:bit.
- [Build A Robot Wars Buggy](https://www.kitronik.co.uk/blog/robot-buggy-part-1-build-robot-wars-buggy-introduction/) - This fun learning resource has been put together to provide teachers with an all in one design and technology challenge that you can set for your students over the course of a term or a year.
- [CPC UCreate micro:bit resources](http://warksjammy.blogspot.co.uk/2017/04/cpc-ucreate-microbit-resources-all-in.html) - Collection of micro:bit resources made for CPC.
- [Year 7 BBC micro:bit topic](https://bournetocode.com/projects/7-CS-micro/) - BBC micro:bit lessons from Bourne Grammar school.
- [Microsoft 14 Week Curriculum](https://makecode.microbit.org/courses/csintro) - Targeted to middle school grades 6-8 (ages 11-14 years). It is also written for teachers who may not have a Computer Science background, or may be teaching an "Intro to CS" for the first time.
- [micro:bit in science teaching - How clean is my pond](https://community.computingatschool.org.uk/resources/5204) - Using a micro:bit to monitor the level of algal growth in a pond and to control a filter pump.
- [Kitronik Inventors Kit Resources](https://www.kitronik.co.uk/blog/kitronik-inventors-kit-resources) - A a great way to get started with programming and hardware interaction with the micro:bit. Includes 12 experiments using LEDs, motors, LDRs and capacitors.
- [CLOQQ Activities](https://cloqq.com/newtomorrowtogether2017) - ([more](https://cloqq.com/tecnologia?id=14777677)) Activities with different difficulty levels, target age, and duration.
- [Learn micro:bit](https://github.com/LearnToProgramRoanoke/Learn-microbit) - Code and materials for learning to program with the BBC micro:bit.
- [Lessons Aligned to Code.org's CS Fundamentals](http://microbit.org/teach/code-org-fundamentals/) - Lesson plans aligned to Code.org's Computer Science Fundamentals curriculum for primary and elementary school students.
- [First steps in using micro:bits with PCs](http://community.computingatschool.org.uk/resources/5437/single) - This very comprehensive article explores ways in which the micro:bit can send data via USB cable or wirelessly to PC applications.
- [Starting Computer Science with the BBC micro:bit](http://microbit.org/en/2018-01-19-train_the_trainer/) - From Getting Started to Games. Computer Science teaching resources designed for use with students aged 10-14 years.
- [Science Experiment Lessons](https://makecode.microbit.org/courses/ucp-science) - Geared for students in middle and early high school, these Science Experiment lessons are designed help gain a greater understanding of the forces and behaviour of the physical world.
- [micro:bit Basics for Teachers](https://microbit.hackster.io/kkristoff/micro-bit-basics-for-teachers-part-1-the-hardware-768229) - ([Part 2](https://microbit.hackster.io/monica/micro-bit-basics-for-teachers-part-2-javascript-blocks-6eaed5), [Part 3](https://microbit.hackster.io/monica/micro-bit-basics-for-teachers-part-3-micropython-c3fde0)) - Are you a teacher who wants to use micro:bit in your classroom, but doesn't know where to start? We'll show you how!

### BBC Teaching Resources

- [Welcome to the micro:bit - Live Lesson](http://www.bbc.co.uk/programmes/articles/2M3H2YpKLsw2W8fC2ycHYSR/welcome-to-the-micro-bit-live-lesson) - Learn how to create games, animations and robots using simple code.
- [Doctor Who and the micro:bit - Live Lesson](http://www.bbc.co.uk/programmes/articles/3ydvd6mvhl89cHVJ7F2nmzf/doctor-who-and-the-micro-bit-live-lesson) - The BBC micro:bit will be put to the test at the controls of the TARDIS in this special BBC Live Lesson in collaboration with the team behind Doctor Who.
- [Strictly micro:bit - Live Lessons](http://www.bbc.co.uk/programmes/articles/49tjW0qR05wXrdpK7ZbGTbs/strictly-micro-bit-live-lesson) - The full BBC Live Lesson exploring the basics of coding, with help from the stars of Strictly Come Dancing and the BBC micro:bit.
- [micro:bit: Mission to Mars - Live Lesson](http://www.bbc.co.uk/programmes/articles/3d5Chvn8QBgdP1Z1d9GN9gx/micro-bit-mission-to-mars-live-lesson) - Reach for the stars with our latest Live Lesson on the BBC micro:bit, which investigates how computer science can be used to aid man's exploration of space.
- [Tackle time and space with Doctor Who and the BBC micro:bit](http://www.bbc.co.uk/programmes/articles/GDNGTpkHJrDJSYMQJbH9f1/tackle-time-and-space-with-doctor-who-and-the-bbc-micro-bit) - Join The Doctor on an adventure of courage, cunning and coding!
	- [Part 1: Mission Sonic](http://www.bbc.co.uk/programmes/articles/52yF6JCCn1X2L4HKBQtgWlP/doctor-who-and-the-micro-bit-mission-sonic) - What plan does the Doctor have in mind to save the Universe from the Reality Bomb?
	- [Part 2: Mission Decode](http://www.bbc.co.uk/programmes/articles/1tbvkWxx5vqQDmGnWMSLBJg/doctor-who-and-the-micro-bit-mission-decode) - The Doctor has intercepted some seriously strange data from the Daleks; it's up to you to help decode it.
	- [Part 3: Mission Hack](http://www.bbc.co.uk/programmes/articles/1ZD3hYYBZVM5SDCVKH6vGfm/doctor-who-and-the-micro-bit-mission-hack) - It's the final mission! Click here to get hacking and infiltrate the Dalek spaceship.


## Community

- [Official Slack Channel](http://tech.microbit.org/get-involved/where-to-find/) - Online form to join this chat group, a great place to discuss and meet more people from the micro:bit community.
- [`@microbit_edu` on twitter](https://twitter.com/microbit_edu)
- [`microbitfoundation` on Facebook](https://www.facebook.com/microbitfoundation)
- [micro:bit Python mailing list (archived)](https://github.com/ntoll/microbit_mailman_archive)
- [micro:bit Sri Lanka User Group](http://microbitslug.org)
- [Croatian Makers](http://izradi.croatianmakers.hr/bbc-microbit-uvodna-stranica/)
- [MakeCode Gitter](https://gitter.im/makecode-community/Lobby)


## Miscellaneous

- [micro:bit broadcast](https://microbit-broadcast.embeddedlog.com) - (Discontinued, archived) newsletter to stay up-to-date with the latest micro:bit news, articles, projects, and resources.
- [microbit.org Support](https://support.microbit.org) - The support pages from the micro:bit Foundation is a great source of information, containing an extensive collection of FAQs, articles, and guides.
- [Radiobit, a BBC micro:Bit RF firmware](https://github.com/virtualabs/radiobit) - Radiobit is composed of a dedicated Micropython-based firmware and a set of tools allowing security researchers to sniff, receive and send data over Nordic's ShockBurst protocol, Enhanced ShockBurst protocol, Bluetooth Smart Link Layer and sniff raw 2.4GHz GFSK demodulated data.
- [micro:bit Poster](https://www.element14.com/community/servlet/JiveServlet/downloadBody/87638-102-3-368412/microbit24x15.pdf) - Element14 has put together this detailed, beautifully rendered, cross-section micro:bit poster highlighting all of the device's key functions and components.
- [Bluetooth troubleshooting guide](http://www.bittysoftware.com/troubleshooting.html) - Tips on how to solve common and not so common micro:bit Bluetooth problems.
- [Micro World Tour](https://microworldtour.github.io) - Before the micro:bit was released a few went on a tour to the world-wide Python community. A lot of interesting content and ideas on these micro:bit adventures.
- [Parent's Complete Guide To The BBC micro:bit](https://www.kitronik.co.uk/blog/parents-complete-guide-bbc-microbit/) - Free resource to help parent's get actively involved in helping their children learn how to code, even with no prior coding experience. 
- [BBC micro:bit composer](https://scratch.mit.edu/projects/201592887/) - Write music and get the corresponding micro:bit micropython code, a tool made with Scratch.
- [micro:mag](http://micromag.cc) - The Unofficial micro:bit Community Magazine.
- [micro:bit Out Of Box Experience](https://support.microbit.org/support/solutions/articles/19000021613-reset-the-micro-bit-to-factory-defaults) - ([Source Code](https://github.com/lancaster-university/microbit-samples/tree/master/source/examples/out-of-box-experience)) The default program running on a brand new micro:bit.


## License

[![CC0](https://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the authors have waived all copyright and related or neighbouring rights to this work.

---

This projects is not endorsed, sponsored or associated with the BBC. "BBC", "micro:bit", and their logos are trademarks of the BBC.
