# Awesome micro:bit [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

[![BBC micro:bit logo](https://az742082.vo.msecnd.net/pub/juslkhnu)](https://www.microbit.co.uk)

A curated list of resources for the BBC micro:bit.

Inspired by the [Awesome lists](https://github.com/sindresorhus/awesome).

**Table Of Contents:**

- [Visual Programming Languages](#visual-programming-languages)
- [Written programming Languages](#written-programming-languages)
- [Online Code Editors](#online-code-editors)
- [Desktop Code Editors](#desktop-code-editors)
- [Programming Tools](#programming-tools)
- [Interface Chip](#interface-chip)
- [Libraries](#libraries)
- [Projects](#projects)
- [Articles](#articles)
- [Teaching Resources](#teaching-resources)


## Visual Programming Languages

- [Microsoft Blocks](https://www.microbit.co.uk/create-code) - A Block interface that produces Touch Develop code.
- [Code Kingdoms](https://www.microbit.co.uk/create-code) - A graphical interface that provides a transitioning experience from 'drag and drop' to text-based programming (JavaScript).
- [PXT](https://codethemicrobit.com) - The Programming eXperience Toolkit for the micro:bit provides a Blocks interface with more capabilities than Microsoft Blocks.


## Written Programming Languages

- [MicroPython](http://microbit-micropython.readthedocs.io) - Port of MicroPython, a Python 3 implementation for microcontrollers and constrained environments.
- [C/C++ runtime](https://lancaster-university.github.io/microbit-docs) - Guidance on how to start using the runtime in C/C++ including full documentation of the APIs, drivers, and types that make up the micro:bit runtime. Bluetooth documentation includes a link to the original *.hex file that ships on the micro:bit devices.
- [Touch Develop](https://www.microbit.co.uk/create-code) - A flexible, text-based programming language with an interactive visual component.
- [PTX TypeScript](https://codethemicrobit.com) - The Programming eXperience Toolkit is based on a subset of TypeScript, which in itself is a superset of JavaScript.
- [Espruino JavaScript](http://www.espruino.com/MicroBit) - A JavaScript interpreter for microcontrollers. It also offers a WebIDE for written code and blocks.
- [Rust on BBC micro:bit](https://github.com/SimonSapin/rust-on-bbc-microbit) - Describes the experience and steps of compiling Rust code for the micro:bit with and without interaction with the runtime DAL.


## Online Code Editors

- [microbit website](https://www.microbit.co.uk) - Includes the Code Kingdoms, Microsoft Blocks, Touch Develop, and Python editors.
- [PTX](https://codethemicrobit.com) - Includes the Blocks and TypeScript editors for the Programming eXperience Toolkit.
- [create.withcode.uk](https://create.withcode.uk) - A Python online editor and simulator that supports the micro:bit MicroPython ([instructions](http://community.computingatschool.org.uk/resources/4479)).


## Desktop Code Editors

- [Mu](http://codewith.mu) - A "micro" editor for MicroPython and the BBC micro:bit.
- [Atom microbit-python package](https://github.com/Giannie/atom-microbit-python) - Flash Python code to your micro:bit directly from the [Atom text editor](https://atom.io).
- [Micro:Pi](https://github.com/Bottersnike/Micro-Pi) - A C/C++ editor with serial monitor and deploy functionality. Written in Python with an installer (ATM Linux only, but could be manually installed in any OS) that includes all dependencies.


## Programming Tools

- [Vagrant C/C++ Development Environment](https://github.com/carlosperate/microbit-dev-env) - With a single command it creates a virtual machine with all the toolchain required to compile and flash C/C++ programs to the micro:bit (including  MicroPython).
- [Android App](https://play.google.com/store/apps/details?id=com.samsung.microbit) - Connects and flashes programs to the micro:bit via Bluetooth.
- [iOS App](https://itunes.apple.com/gb/app/micro-bit/id1092687276) - Connects and flashes programs to the micro:bit via Bluetooth.
- [uFlash](https://github.com/ntoll/uflash/) - A utility for flashing the BBC micro:bit with Python scripts and the MicroPython runtime.
- [MicroFs](https://github.com/ntoll/microfs) - A simple command line tool and module for interacting with the limited file system provided by MicroPython on the BBC micro:bit.
- [micro:bit uploader](https://www.touchdevelop.com/microbituploader) - Windows application that monitors your Downloads forlder and flashes any new programs to the micro:bit. 
- [Scratch for BBC micro:bit](http://www.picaxe.com/BBC-microbit) - Using BBC micro:bit with Scratch / S2Bot: the [S2Bot](http://www.picaxe.com/s2bot) app allows you to use the BBC micro:bit as a bluetooth 'games controller' for your Scratch project. Needs [BLED112](http://www.picaxe.com/bled112) [Bluetooth dongle](http://www.silabs.com/products/wireless/bluetooth/bluetooth-smart-modules/Pages/bled112-bluetooth-smart-dongle.aspx).


## Interface Chip

The Interface Chip is the microcontroller placed close to the battery connector. It provides the USB mass storage capability to load the micro:bit firmware using the Operating System file explorer.

- [DAPLink on micro:bit](https://www.mbed.com/en/development/hardware/prototyping-production/daplink/daplink-on-kl26z/) - The DAPLink is the default software running on the Interface Chip, this page contains information, update instructions, and the latest firmware.
- [J-Link OB Firmware](https://www.segger.com/bbc-micro-bit.html) - Offers the same flashing functionality than the DAPLink and expands it to include J-Link debugging.


## Libraries

### Python

- [MicroPeri](https://github.com/JoeGlancy/microperi) - Run Python programs on your computer with the same micro:bit MicroPython API and connecting a micro:bit as an external peripheral device or sensor.
- [microbit_stub](https://github.com/casnortheast/microbit_stub) - A Python module that emulates the BBC micro:bit as defined by the micro:bit MicroPython API.


### Node.js

- [node-bbc-microbit](https://github.com/sandeepmistry/node-bbc-microbit) - Control a BBC micro:bit from Node.js using BLE.


## Projects

All these projects contain steps and resources required for reproduction.

- [Quiz:bit](https://github.com/lancaster-university/quiz-bit) - micro:bit programs and a matching application for providing a quiz-voter-style service using micro:bits as the controls.


## Articles

Useful Articles for developing on the BBC micro:bit.

- [Getting Started Microbit & Microsoft’s new www.codethemicrobit.com Environment](https://blogs.msdn.microsoft.com/uk_faculty_connection/2016/08/01/getting-started-microbit-microsofts-new-www-codethemicrobit-com-environment/)
- [Offline C/C++ Development With The Micro:bit](http://www.i-programmer.info/programming/hardware/9654-offline-cc-development-with-the-microbit-.html)
- [Sending 'commands' from a micro:bit over Bluetooth](http://bluetooth-mdw.blogspot.co.uk/2016/07/sending-commands-from-microbit-over.html)


## Teaching Resources

- [microbit.co.uk Teaches and Parents](https://www.microbit.co.uk/teachers-and-parents)
- [IET micro:bit Teaching Resources](http://faraday.theiet.org/stem-activity-days/bbc-microbit/resources/index.cfm)
- [Code Club micro:bit projects](https://www.codeclubprojects.org/en-GB/microbit/)
- [Make with the micro:bit by Technology Will Save Us](http://make.techwillsaveus.com)


## License & Trademarks

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the authors have waived all copyright and related or neighbouring rights to this work.

This projects is not endorsed, sponsored or associated with the BBC. "BBC”, “micro:bit”, and their logos are trade marks of the BBC. [http://microbit.co.uk](http://microbit.co.uk)
