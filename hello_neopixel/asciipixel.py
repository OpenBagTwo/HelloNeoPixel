"""Virtual terminal-based NeoPixel implementation"""
RESET_SEQUENCE = "\033[0m"
PIXEL_CHARACTER = "\u2b24"  # https://www.compart.com/en/unicode/U+2B24


def convert_rgb_to_ansi_escape(color: tuple, which_color: str) -> str:
    """Create an ANSI escape sequence to color the text and background as
    specified

    Args:
        color : tuple of three ints
            The RGB value for the color.
        which_color : str
            Which color you're looking to set. Must either be one of:
                - "background"
                - "text" / "foreground"

    Returns:
        str : the ANSI escape sequence for coloring the background and text
              as specified

    Notes:
        Never forget to end your text sequence with the RESET_SEQUENCE!
    """
    if which_color == "background":
        selector_code = "48"
    elif which_color in ("text", "foreground"):
        selector_code = "38"
    else:
        message = (
            "This method only supports setting background and"
            " foreground / text colors"
        )
        raise ValueError(message)

    return "\033[{};2;{};{};{}m".format(selector_code, *color)


class AsciiPixel:
    """Virtual light strip where the colors of each pixel get rendered as a
    character in the terminal.

    Attributes:
        n (int) : the number of pixels
        animate_mode (bool) : when True, the "strip" will be printed with a
                              carriage return, but no newline, so as to
                              animate in place

    Notes:
        Requires your terminal to support TrueColor
    """

    def __init__(
        self,
        n_pixels: int,
        strip_color: tuple = (0, 0, 0),
        pixel_spacing: int = 1,
        animate: bool = False,
    ) -> None:
        """Initialize the virtual light strip

        Args:
            n_pixels (int) : the number of pixels in your virtual strip
            strip_color (tuple of three ints, optional) :
                the "background" RGB color (color between pixels) of your
                virtual light strip. Default is black (0, 0, 0).
            pixel_spacing (int, optional): the number of characters between each
                                           pixel. Default is 1.
            animate (bool, optional): whether to initialize the strip in
                                      "animate mode" (print without newline).
                                      Default is False, and this can always
                                      be changed later.

        """
        self.animate_mode = animate
        self._background_color = strip_color
        self._pixel_spacing = pixel_spacing
        self._pixels = [(0, 0, 0) for _ in range(n_pixels)]

    def __iter__(self):
        for pixel in self._pixels:
            yield pixel

    def __getitem__(self, index: int) -> tuple:
        return self._pixels[index]

    def __setitem__(self, index: int, value: tuple) -> None:
        # TODO: is typing available for uPython?
        #       alternatively, is there a more primitive way to hint at
        #       "tuple of three ints"?
        self._pixels[index] = value  # type: ignore[assignment]

    def __len__(self) -> int:
        return len(self._pixels)

    @property
    def n(self) -> int:
        return len(self)

    def write(self, output_to=None):  # TODO: type hint?
        """Emulation of the NeoPixel write function which, in this case,
        renders the virtual strip to stdout

        Args:
            output_to (stream, optional):  If you'd like to display the virtual
                                           pixel to somewhere else besides
                                           stdout, provide your desired
                                           output stream to this argument.

        Returns:
            None
        """
        spacer = " " * self._pixel_spacing
        print_kwargs = {}
        if self.animate_mode:
            print_kwargs["end"] = "\r"
        if output_to is not None:
            print_kwargs["file"] = output_to

        header = convert_rgb_to_ansi_escape(
            self._background_color, "background"
        )

        text_pixels = [
            convert_rgb_to_ansi_escape(pixel_rgb, "text") + PIXEL_CHARACTER
            for pixel_rgb in self
        ]

        print(
            header
            + spacer
            + spacer.join(text_pixels)
            + spacer
            + RESET_SEQUENCE,
            **print_kwargs
        )
