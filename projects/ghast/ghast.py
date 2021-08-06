"""Logic for controlling the ghast.

Code for interacting with the DFPlayer DFMini SD MP3 player module is baed on
specs and protocol information found here:
https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299"""
import blynklib_mp as blynklib
import machine
import urandom
import utime

from hello_neopixel.animations import Fireball
from hello_neopixel.base import Pixel
from hello_neopixel.manager import run_animations

# these are the track numbers (explicitly "00x.mp3" / "0xx.mp3") as they exist
# on my SD card. Adjust if your numberings differ.
ANGRY_TRACK = 15  # charge.ogg
FIRE_TRACK = 13  # fireball4.ogg
PASSIVE_TRACKS = (6, 7, 8, 9, 10, 11, 12)  # moan1.ogg - moan7.ogg


def _compile_command(
    command_code: int, parameter_1: int = 0, parameter_2: int = 0
) -> bytes:
    """Generate the byte string to send to the DFPlayer

    Args:
        command_code (byte in hex): The command value
        parameter_1 (byte in hex, default = 0x00): The "high data byte"
        parameter_2 (byte in hex, default = 0x00): The "low data byte"

    Returns:
        bytes
            The byte sequence to transmit the specified command

    Notes:
        This omits the checksum and feedback bytes, as they're not needed
    """
    return bytes(
        [0x7E, 0xFF, 6, command_code, 0, parameter_1, parameter_2, 0xEF]
    )


def _play_track(uart: machine.UART, track_number: int) -> None:
    """Send the command to play a specific track

    Args:
        uart (machine.UART):
            the UART object configured to communicate with the DFPlayer
        track_number (int):
            The track to play

    Returns:
        None
    """
    uart.write(_compile_command(3, 0, track_number))


def play_passive(uart: machine.UART) -> None:
    """Tell the DFPlayer to play one of the "passive" ghast sounds at random

    Args:
        uart (machine.UART):
            the UART object configured to communicate with the DFPlayer

    Returns:
        None
    """
    _play_track(uart, urandom.choice(PASSIVE_TRACKS))


def play_angry(uart: machine.UART) -> None:
    """Tell the DFPlayer to play the angry ghast sound

    Args:
        uart (machine.UART):
            the UART object configured to communicate with the DFPlayer

    Returns:
        None
    """
    _play_track(uart, ANGRY_TRACK)


def play_fireball(uart: machine.UART) -> None:
    """Tell the DFPlayer to play the fireball sound

    Args:
        uart (machine.UART):
            the UART object configured to communicate with the DFPlayer

    Returns:
        None
    """
    _play_track(uart, FIRE_TRACK)


class Ghast:
    """Runner for the ghast animation, sound effects and app communication.

    The ghast has two modes: passive (is_angry = False) and angry
    (is_angry = True).

    While passive, its eyes and mouth will not be illuminated upon calling
    update_leds() and play_sound() will choose from one of the passive
    ghast "moans."

    In angry mode, its eyes and mouth will illuminate red upon calling
    update_leds(), and play_sound() will play its shriek ("charge").

    If launch_fireball() is called, the "fireball" launch sound will play,
    and the fireball animation will run to completion.

    While this all can be orchestrated via console, the intent is to
    connect the ghast to Blynk via register_app() and then execute run(), which
    will allow the connected Blynk app to control the ghast over wifi.

    The app-controlled behavior is for:
      - switching the ghast from passive to angry to immediately trigger a
        shriek
      - the ghast to "calm down" (switch from angry to passive) after the
        fireball is launched
      - the ghast to be able to launch fireballs in passive mode, which is,
        admittedly, not true to the game.

    Attributes:
        eyes (list-like of Pixels):
            The pixel or pixels that control the eyes of the ghast
        mouth (Pixel):
            The pixel for the ghast's mouth
        uart (machine.UART):
            The UART controller for communicating with the sound board
        is_angry (bool):
            True = ghast is angry
            False = ghast is passive
        current_time (float): time (in seconds) since starting run()
        calm_after (bool): set to True after a fireball launch to tell
                           the program to set the ghast back to passive
                           after the fireball animation completes
        calm_ui (bool): flag to update the blynk app's UI to passive (and
                        ignore it if the toggle in the UI is still set to
                        angry)
        next_sound_at (float): time (in seconds) when the ghast will next
                               play a sound
        fireball (ani.Animation): the fireball animation
        blynk_app (Blynk): the Blynk object for communicating with the app UI
    """

    def __init__(self, eyes, mouth: Pixel, uart: machine.UART):
        """Initialize a ghast

        Args:
            eyes (Pixel or list of Pixels):
                The pixel(s) for the eyes
            mouth (Pixel):
                The pixel for the mouth
            uart (machine.UART):
                The UART controller for interacting with the sound card
        """
        if isinstance(eyes, Pixel):
            self.eyes = (eyes,)
        self.mouth = mouth
        self.uart = uart
        self.is_angry = False
        self.current_time = 0.0
        self.calm_after = False
        self.calm_ui = False
        self.next_sound_at = 0.0

        self.fireball = Fireball(self.mouth)

    def register_app(self, blynk_app: blynklib.Blynk):
        """Connect the ghast to Blynk

        Args:
            blynk_app (Blynk):
                the Blynk object for communicating with the app UI

        Returns:
            None

        Notes:
            The Blynk app should consist of:
            - a switch button for toggling between passive (0) and active (1)
              connected to virtual pin V0
            - a push button (0/1) for triggering a fireball launch connected
              to virtual pin V1
            - a Level V indicator for displaying the fireball cooldown time,
              with values ranging from 0 to 1023, connected to virtual pin V2
        """

        @blynk_app.handle_event("write V0")
        def update_ghast_mood(pin, value):
            if int(value[0]) == 1:
                if not self.is_angry:
                    play_angry(self.uart)
                if not self.calm_ui:
                    self.is_angry = True
            else:
                self.is_angry = False

        @blynk_app.handle_event("read V0")
        def calm_ghast(pin):
            if self.calm_ui:
                blynk_app.virtual_write(pin, 0)
                self.calm_ui = False

        @blynk_app.handle_event("write V1")
        def launch_fireball(pin, value):
            if int(value[0]) == 1:
                self.fireball.trigger_time = self.current_time
                play_fireball(self.uart)
                self.calm_after = True

        @blynk_app.handle_event("read V2")
        def render_cooldown(pin):
            progress = (self.current_time - self.fireball.trigger_time) / 2000
            if 0 < progress < 1:
                progress = int(1024 * (1.0 - progress))
                blynk_app.virtual_write(pin, progress)
            else:
                if self.calm_after and self.is_angry:
                    self.is_angry = False
                    self.calm_ui = True
                    self.calm_after = False

        self.blynk_app = blynk_app

    def update_leds(self):
        """Update and display the new colors values for the LEDs based on the
        ghast's mood and where we are in the fireball animation

        Returns:
            None
        """
        pixels = set(self.eyes)
        pixels.add(self.mouth)

        light_strips = {pixel.light_strip for pixel in pixels}
        if self.is_angry:
            for pixel in pixels:
                pixel.set((128, 0, 0))
        if 0 <= self.current_time - self.fireball.trigger_time < 2.0:
            self.fireball.render(self.current_time)
        for light_strip in light_strips:
            light_strip.write()

    def play_sound(self):
        """Play a ghast sound depending on its mood

        Returns:
            None
        """
        if self.is_angry:
            play_angry(self.uart)
        else:
            play_passive(self.uart)

    def launch_fireball(self, frame_rate: float = 60.0):
        """Run through the fireball animation

        Args:
           frame_rate (float, optional):
                how many times per second to render the animations.
                Default is 60 fps.

        Returns:
            None
        """
        self.fireball.trigger_time = 0.0  # runner will use its own clock
        play_fireball(self.uart)
        run_animations([self.fireball], 2.0, frame_rate=frame_rate)

    def run(
        self,
        runtime: float = None,
        frame_rate: float = 15.0,
        sound_interval: float = 5.0,
        clear_after: bool = False,
    ):
        """Connect the ghast to Blynk so it can be controlled via app

        Args:
            runtime (float, optional):
                how long to stay connected. Default is forever (or until
                the microcontroller is interrupted or restarted).
            frame_rate (float, optional):
                how many times per second to render the animations and
                communicate with Blynk. Default is 15 fps, which may or may
                not be feasible based on Blynk, your internet connection or
                the microcontroller's hardware.
            sound_interval (float, optional):
                how many seconds should elapse between the ghast playing a
                sound (in the absence of external triggers). Default is 5.0.
            clear_after (bool, optional):
                whether to turn off all the LED lights once the run ends.
                Default is True.

        Returns:
            None
        """
        try:
            self.blynk_app.connect()
        except AttributeError:
            message = "Must .register() a blynk app before running."
            raise RuntimeError(message)

        step_time_us = int(1e6 / frame_rate)  # microseconds between steps
        start_time = utime.ticks_ms()

        try:
            while True:
                step_start_tick_us = utime.ticks_us()
                self.current_time = (
                    utime.ticks_diff(utime.ticks_ms(), start_time) / 1000
                )
                if runtime is not None and self.current_time > runtime:
                    break

                self.blynk_app.run()

                self.update_leds()

                if self.current_time > self.next_sound_at:
                    self.play_sound()
                    self.next_sound_at = self.current_time + sound_interval

                compute_time_us = utime.ticks_us() - step_start_tick_us
                if compute_time_us < step_time_us:
                    utime.sleep_us(step_time_us - compute_time_us)

        finally:
            self.current_time = 0  # reset for the next run
            if clear_after:
                self.is_angry = False
                self.fireball.trigger_time = 1e99
                self.update_leds()
            self.blynk_app.disconnect()
