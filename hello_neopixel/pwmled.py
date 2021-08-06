"""NeoPixel-compatible abstraction for controlling non-addressable LEDs"""
try:
    from machine import PWM, Pin

    def _convert_to_pwm(pin):
        if isinstance(pin, None):
            return None
        if isinstance(pin, int):
            pin = Pin(pin)
        if isinstance(pin, Pin):
            pin = PWM(pin, freq=20000, duty=0)
        if not isinstance(pin, PWM):
            message = "{pin} is not a valid pin".format(pin=repr(pin))
            raise ValueError(message)


except ImportError:

    def _convert_to_pwm(pin):
        """Pass-through for testing on Unix micropython"""
        return pin


from .base import Pixel


def _validate_calibration_matrix(calibration):
    if len(calibration) != 3 or any(len(row) != 3 for row in calibration):
        message = "calibration must be in the form of a 3x3 matrix"
        raise ValueError(message)


class RGBLED:
    """RGB LED controlled with separate GPIO pins controlling each channel,
    wrapped to be NeoPixel interface compatible (treated like a strip of
    length 1)

    Attributes:
        value (tuple of three ints):
            the RGB tuple corresponding to the color that the LED should
            display upon next call to write()
        n (int): the number of pixels. That is to say, 1.
    """

    def __init__(
        self,
        pins,
        calibration=((1.0, 0.0, 0.0), (0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    ):
        """
        Args:
            pins: tuple of three ints, machine.Pins or machine.PWMs
                The pins that will control each channel (in order R-G-B)
            calibration: 3x3 matrix, optional
                Calibration values. The duty cycle written to each channel
                based on the set color value will be:
                    duty[i] = sum(4 * calibration[i][j] * value[j])

        """
        try:
            self._channels = tuple(_convert_to_pwm(pin) for pin in pins)
        except TypeError:
            message = (
                "The main constructor requires you to provide separate"
                " pins for the R, G and B channels."
                "\n    For monochrome LEDs, try the factory methods."
            )
            raise TypeError(message)

        n_channels = len(self._channels)
        if n_channels != 3:
            message = (
                "This class does not support {n_channels}-channel LEDs".format(
                    n_channels=n_channels
                )
            )
            raise NotImplementedError(message)

        _validate_calibration_matrix(calibration)
        self._calibration = calibration

        self.value = (0, 0, 0)

    def write(self) -> None:
        """Update the displayed LED color

        Returns:
            None
        """
        for i in range(3):
            if self._channels[i] is None:
                continue
            channel_value = 4.0 * sum(
                self._calibration[i][j] * self.value[j] for j in range(3)
            )
            channel_value = int(min(max(channel_value, 0), 1023))

            self._channels[i].duty(channel_value)

    @classmethod
    def red(cls, pin, adjust=1.0):
        """Create an RGBLED to represent a red LED

        Args:
            pin (int, machine.Pin or machine.PWM):
                The GPIO pin controlling this pixel
            adjust (float, optional):
                A multiplier between 0 and 1 to use to adjust the LED
                brightness when calibrating colors across a strip of
                potentially very different LEDs

        Returns:
            RGBLED: essentially a NeoPixel-compatible single-pixel light strip
                    where only the red channel works
        """
        return cls((pin, None, None), ((adjust, 0, 0), (0, 0, 0), (0, 0, 0)))

    @classmethod
    def green(cls, pin, adjust=1.0):
        """Create an RGBLED to represent a green LED

        Args:
            pin (int, machine.Pin or machine.PWM):
                The GPIO pin controlling this pixel
            adjust (float, optional):
                A multiplier between 0 and 1 to use to adjust the LED
                brightness when calibrating colors across a strip of
                potentially very different LEDs

        Returns:
            RGBLED: essentially a NeoPixel-compatible single-pixel light strip
                    where only the green channel works
        """
        return cls((None, pin, None), ((0, 0, 0), (0, adjust, 0), (0, 0, 0)))

    @classmethod
    def blue(cls, pin, adjust=1.0):
        """Create an RGBLED to represent a blue LED

        Args:
            pin (int, machine.Pin or machine.PWM):
                The GPIO pin controlling this pixel
            adjust (float, optional):
                A multiplier between 0 and 1 to use to adjust the LED
                brightness when calibrating colors across a strip of
                potentially very different LEDs

        Returns:
            RGBLED: essentially a NeoPixel-compatible single-pixel light strip
                    where only the blue channel works
        """
        return cls((None, None, pin), ((0, 0, 0), (0, 0, 0), (0, 0, adjust)))

    @classmethod
    def white(cls, pin, calibration=(1 / 3, 1 / 3, 1 / 3)):
        """Create an RGBLED to represent a white LED

        Args:
            pin (int, machine.Pin or machine.PWM):
                The GPIO pin controlling this pixel
            calibration (tuple of three floats, optional):
                A vector that weighs how much the LED should brighten based on
                the red, green and blue channels, respectively. The default
                is to give each channel equal weight (so that (255, 255, 255)
                is max brightness and (255, 0, 0) would be 1/3 max brightness).

        Returns:
            RGBLED: essentially a NeoPixel-compatible single-pixel light strip
                    which only displays white light
        """
        return cls((pin, 0, 0), (calibration, (0, 0, 0), (0, 0, 0)))

    @property
    def n(self):
        return 1

    def __iter__(self):
        for pixel in (self.value,):
            yield pixel

    def __getitem__(self, index: int) -> tuple:
        if index != 0:
            raise IndexError("RGBLED is just one pixel")
        return self.value

    def __setitem__(self, index: int, value: tuple) -> None:
        # TODO: is typing available for uPython?
        #       alternatively, is there a more primitive way to hint at
        #       "tuple of three ints"?
        if index != 0:
            raise IndexError("RGBLED is just one pixel")
        self.value = value  # type: ignore[assignment]

    def to_pixel(self) -> Pixel:
        """Return the Pixel representation of this LED

        Returns:
            Pixel: a representation of the LED as a Pixel
        """
        return Pixel(self, 0)
