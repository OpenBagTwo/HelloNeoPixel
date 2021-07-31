# Ghast

This is the code for an app-controlled model Minecraft
[ghast](https://minecraft.fandom.com/wiki/Ghast) which
makes ghast noises, can be toggled between passive and angry modes,
and can be triggered to shoot fireballs.

## Technical Design

### Components (Parts List)

* **Main Controller: ESP32-WROOM-32** development board. For
  once, it actually made sense to use an ESP32 over a cheaper
  82xx, as the non-REPL UART bus on the 8266 is TX only
  (no RX), and the only other WiFi-enabled MicroPython board
  (the PyBoard) is considerably more expensive. Smaller
  form factors exist, but the enclosure was large enough to
  accommodate the full-sized dev board, so why not?
  
* **Audio / SD Card Module: DFRobot DFPlayer Mini** (clone).
  A pretty nifty board that lets you load mp3 files onto
  an SD card and then play them either via buttons or
  UART. The clones are notoriously poor build quality--out
  of five I ordered, only _one_ had functional UART. On
  the plus side, the kit I ordered came with an 8Ω speaker.
  
* **LEDs:**
  * 2x **5mm Red LEDs** for the eyes
  * 1x **single WS2812 NeoPixel** (clone) addressable RGB LED
    for the mouth
    
<!-- AMP? -->
  
### Enclosure

<!-- Link to STL -->

<!-- Yay Toybox! -->

### Assembly

#### Wiring Diagram

### Blynk App

## Installation

<!-- Outline
1. Flash ESP32
1. Follow setup instructions from project root to install
HelloNeoPixel
1. Download ghast sounds from somewhere
1. Convert ghast sounds to mp3 with specified order
1. Download and deploy blynklib_mp.py
1. Create the above blynk app and then get the auth key
1. Create a file called secrets.py and set auth creds for your wifi and blynk
1. Use ampy to put main.py and ghast.py onto microcontroller
-->


