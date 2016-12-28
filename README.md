# Awesome micro:bit [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

[![micro:bit logo](http://i.imgur.com/rYLbkBh.jpg)](https://www.microbit.org)

A curated list of resources for the BBC micro:bit, a pocket-sized programmable board with a Bluetooth capable microcontroller, accelerometer, magnetometer, LED matrix, a couple of buttons, and accessible GPIO.

Inspired by the [Awesome lists](https://github.com/sindresorhus/awesome).

**Table Of Contents:**

- [Visual Programming Languages](#visual-programming-languages)
- [Written programming Languages](#written-programming-languages)
- [Online Code Editors](#online-code-editors)
- [Desktop Code Editors](#desktop-code-editors)
- [Programming Tools](#programming-tools)
- [Apps](#apps)
- [Interface Chip](#interface-chip)
- [Libraries](#libraries)
- [Projects](#projects)
- [Articles](#articles)
- [Videos](#videos)
- [Teaching Resources](#teaching-resources)
- [Miscellaneous](#miscellaneous)


## Visual Programming Languages

- [Microsoft Blocks](https://www.microbit.co.uk/app/#create:xczaux) - A Block interface that produces Touch Develop code.
- [Code Kingdoms](https://www.microbit.co.uk/app/#create:tomwku) - A graphical interface that provides a transitioning experience from 'drag and drop' to text-based programming (JavaScript).
- [PXT](https://codethemicrobit.com) - The Programming eXperience Toolkit for the micro:bit provides a Blocks interface with more capabilities than Microsoft Blocks.
- [Scratch for BBC micro:bit](http://www.picaxe.com/BBC-microbit) - Using micro:bit with Scratch / S2Bot as a bluetooth 'games controller' (needs specific BLED112 Bluetooth dongle).


## Written Programming Languages

- [MicroPython](http://microbit-micropython.readthedocs.io) - Port of MicroPython, a Python 3 implementation for microcontrollers and constrained environments.
- [C/C++ runtime](https://lancaster-university.github.io/microbit-docs/) - Guidance on how to start using the runtime in C/C++ including full documentation of the APIs, drivers, and types that make up the micro:bit runtime. Bluetooth documentation includes a link to the original *.hex file that ships on the micro:bit devices.
- [Touch Develop](https://www.microbit.co.uk/create-code#touchdevelopEditor) - A flexible, text-based programming language with an interactive visual component.
- [PTX TypeScript](https://codethemicrobit.com) - The Programming eXperience Toolkit is based on a subset of TypeScript, which in itself is a superset of JavaScript.
- [Espruino JavaScript](http://www.espruino.com/MicroBit) - A JavaScript interpreter for microcontrollers. It also offers a WebIDE for written code and blocks.
- [Rust on BBC micro:bit](https://github.com/SimonSapin/rust-on-bbc-microbit) - Describes the experience and steps of compiling Rust code for the micro:bit with and without interaction with the runtime DAL.


## Online Code Editors

- [microbit website](https://www.microbit.org/code/) - Includes the Code Kingdoms, PXT, Microsoft Blocks, Touch Develop, and Python editors.
- [create.withcode.uk](https://create.withcode.uk) - A Python online editor and simulator that supports the micro:bit MicroPython ([instructions](http://community.computingatschool.org.uk/resources/4479)).


## Desktop Code Editors

- [Mu](http://codewith.mu) - A "micro" editor for MicroPython and the BBC micro:bit.
- [Atom microbit-python package](https://github.com/Giannie/atom-microbit-python) - Flash Python code to your micro:bit directly from the Atom text editor.
- [Micro:Pi](https://github.com/Bottersnike/Micro-Pi) - A C/C++ editor with serial monitor and deploy functionality. Written in Python with an installer (ATM Linux only, but could be manually installed in any OS) that includes all dependencies.


## Programming Tools

- [Vagrant C/C++ Development Environment](https://github.com/carlosperate/microbit-dev-env) - With a single command it creates a virtual machine with all the toolchain required to compile and flash C/C++ programs to the micro:bit (including  MicroPython).
- [Android App](https://play.google.com/store/apps/details?id=com.samsung.microbit) - Connects and flashes programs to the micro:bit via Bluetooth.
- [iOS App](https://itunes.apple.com/gb/app/micro-bit/id1092687276) - Connects and flashes programs to the micro:bit via Bluetooth.
- [uFlash](https://github.com/ntoll/uflash/) - A utility for flashing the micro:bit with Python scripts and the MicroPython runtime.
- [MicroFs](https://github.com/ntoll/microfs) - A simple command line tool and module for interacting with the limited file system provided by MicroPython on the micro:bit.
- [micro:bit uploader](https://www.touchdevelop.com/microbituploader) - Windows application that monitors your Downloads folder and flashes any new programs to the micro:bit.
- [PXT Command Line Tool](https://www.pxt.io/cli) - Use the command line to program the micro:bit with javascript using PXT.
- [Jupyter kernel for the micro:bit](https://github.com/takluyver/ubit_kernel) - This package allows Jupyter interfaces to run MicroPython code directly on the micro:bit.


## Apps

- [micro:bit Blue](https://github.com/microbit-foundation/microbit-blue) - [Android](https://play.google.com/store/apps/details?id=com.bluetooth.mwoolley.microbitbledemo) Contains a series demos for interacting with the microbit using Bluetooth.
- [Bitty Software Apps](http://www.bittysoftware.com/apps.html) - A diverse collection of Android and iOS apps, going from data logging to audio pranks, you'll certainly find something of interest. 
- [Insight Mr Bit](http://www.insightresources.co.uk/microbit/page63.html) - Create simple programs in plain English to control the BBC micro:bit to do lots of useful things.


## Interface Chip

The Interface Chip is the microcontroller placed close to the battery connector. It provides the USB mass storage capability to load the micro:bit firmware using the Operating System file explorer.

- [DAPLink on micro:bit](https://www.mbed.com/en/development/hardware/prototyping-production/daplink/daplink-on-kl26z/) - The DAPLink is the default software running on the Interface Chip, this page contains information, update instructions, and the latest firmware.
- [DAPLink source code](https://github.com/mbedmicro/DAPLink) - Source code for the mbed DAPLink, contains the build configuration for the micro:bit.
- [J-Link OB Firmware](https://www.segger.com/bbc-micro-bit.html) - Offers the same flashing functionality than the DAPLink and expands it to include J-Link debugging.


## Libraries

### Python

- [MicroPeri](https://github.com/c0d3st0rm/microperi) - Run Python programs on your computer with the same micro:bit MicroPython API and connecting a micro:bit as an external peripheral device or sensor.
- [microbit_stub](https://github.com/casnortheast/microbit_stub) - A Python package that emulates the micro:bit as defined by the micro:bit MicroPython API.
- [bluezero](https://github.com/ukBaz/python-bluezero) - A Python package to interface with Bluetooth devices, with examples for the micro:bit. 


### Node.js

- [node-bbc-microbit](https://github.com/sandeepmistry/node-bbc-microbit) - Control a micro:bit from Node.js using BLE.


## Projects

All these projects contain steps and resources required for reproduction.

- [microbit.co.uk Site Index](https://www.microbit.co.uk/index) - The microbit.co.uk website contains an extensive list with all their projects and tutorials.
- [Quiz:bit](https://github.com/lancaster-university/quiz-bit) - micro:bit programs and a matching application for providing a quiz-voter-style service using micro:bits as the controls.
- [JUST DO IoT](https://hackaday.io/project/12164-just-do-iot) - Connect the micro:Bit to the LoRaWAN network, includes open source hardware microbit connector board.
- [Micro:Bob](https://hackaday.io/project/8643-microbob) - A simple bipedal robot controlled by a micro:bit.
- Coffee Timer ([1](https://www.norwegiancreations.com/2016/09/coffee-timer-part-1-the-first-prototype-based-on-the-bbc-microbit/), [2](https://www.norwegiancreations.com/2016/10/coffee-timer-part-2-low-power-wireless-on-the-bbc-microbit/), [3](https://www.norwegiancreations.com/2016/11/coffee-timer-part-3-enclosures/)) - Three part article describing how to augment a coffee maker with an micro:bit indicator, options for low power communication, and creating a custom enclosure.
- [Thermal Printer](http://www.suppertime.co.uk/blogmywiki/2016/12/microbit-thermal/) - Connecting and using a Sparkfun thermal till-roll printer.
- [Telescopic Light Sword](https://www.myminifactory.com/object/telescopic-lightsword-with-micro-bit-14598) - Project shows how to make your own Light Sword with the micro:bit, electronics, and 3D printed parts.


## Articles

Useful Articles for developing on the micro:bit.

- [Getting Started Microbit & Microsoft’s new www.codethemicrobit.com Environment](https://blogs.msdn.microsoft.com/uk_faculty_connection/2016/08/01/getting-started-microbit-microsofts-new-www-codethemicrobit-com-environment/)
- [Offline C/C++ Development With The Micro:bit](http://www.i-programmer.info/programming/hardware/9654-offline-cc-development-with-the-microbit-.html)
- [Sending 'commands' from a micro:bit over Bluetooth](http://bluetooth-mdw.blogspot.co.uk/2016/07/sending-commands-from-microbit-over.html)
- [MultiWingSpan](http://www.multiwingspan.co.uk/micro.php) - A large collection of examples, instructions, and direction on how to use electronic components.


## Videos

- [MicroMonsters](https://www.youtube.com/channel/UCK2DviDexh_Er2QYZerZyZQ) - A YouTube channel with tutorials to learn to code with your family.
- [micro:bit and Bluetooth](https://www.youtube.com/playlist?list=PLYOCnwH2UtBzhJ2nvn_DM3itz6GNVwrDu) - YouTube playlist with Martin Woolley's Bluetooth videos.


## Teaching Resources

- [microbit.org Teaching Resources](https://www.microbit.org/teach/)
- [IET micro:bit Teaching Resources](http://faraday.theiet.org/stem-activity-days/bbc-microbit/resources/index.cfm)
- [Code Club micro:bit projects](https://www.codeclubprojects.org/en-GB/microbit/)
- [Make with the micro:bit by Technology Will Save Us](http://make.techwillsaveus.com/bbc-microbit)
- [Grok Learning](https://groklearning.com/microbit/) - Provides an online MicroPython code editor, Blockly visual programming, full micro:bit simulator, curriculum-aligned teaching material and auto-marked problems.
- [Microbit For Primary Schools](http://mb4ps.co.uk)
- [101 Computing BBC micro:bit category](http://www.101computing.net/category/bbc-microbit/) - Computing challenges with the micro:bit to boost your programming skills or spice up your teaching of computer science.
- [Micro:bit Maths](https://microbitmathsblog.wordpress.com) - A blog exploring the BBC micro:bit in mathematics education.
- [micro:bit of Things](https://sites.google.com/view/microbitofthings/) - Notes on micro:bit project ideas for Key Stage 2 and 3.


## Miscellaneous

- [Kodu Controller](http://www.kodugamelab.com/bbc-microbit/) - Enables interacting with the microbit from Kodu Game Lab.
- [microbit Fritzing Part](https://github.com/topshed/FritzingParts) - Richard Hayler collection of Fritzing parts contains a model for the micro:bit.
- [Bitty Software](http://www.bittysoftware.com) - Provides phone apps for the micro:bit with hands-on tutorials.
- [micro:bit broadcast](http://eepurl.com/cq4Y6b) - Free newsletter to stay up-to-date with the latest micro:bit news, articles, projects, and resources.
- [CAD Resources](https://www.kitronik.co.uk/blog/bbc-microbit-cad-resources/) - Free micro:bit CAD model from Kitronik.
- [micro:bit-o-matic](https://pycomic.github.io/microbit.html) - Easily create micro:bit illustrations with custom LED matrix messages.


## License & Trademarks

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the authors have waived all copyright and related or neighbouring rights to this work.

This projects is not endorsed, sponsored or associated with the BBC. "BBC”, “micro:bit”, and their logos are trademarks of the BBC.
