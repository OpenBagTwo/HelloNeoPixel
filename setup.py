from setuptools import setup

import versioneer

setup(
    name="HelloNeoPixel",
    description=(
        "Sandbox for learning to use"
        " individually-addressible LEDs using MicroPython"
    ),
    author='Gili "OpenBagTwo" Barlev',
    url="https://github.com/OpenBagTwo/HelloNeoPixel",
    packages=["hello_neopixel"],
    license="GPL v3",
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
