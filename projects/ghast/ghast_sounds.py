"""Code for interacting with the DFPlayer DFMini SD MP3 player module. Specs
and protocol information are here:
https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299"""
import machine
import urandom

# these are the track numbers (explicitly "00x.mp3" / "0xx.mp3") as they exist
# on my SD card. Adjust if your numberings differ.
ANGRY_TRACK = 3  # charge.ogg
FIRE_TRACK = 5  # fireball4.ogg
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
        track_number: int
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
