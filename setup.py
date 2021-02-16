from setuptools import find_namespace_packages, setup

import versioneer

setup(
    name="HelloNeoPixel",
    description=(
        "Sandbox for learning to use"
        " individually-addressible LEDs using MicroPython"
    ),
    author='Gili "OpenBagTwo" Barlev',
    url="https://github.com/OpenBagTwo/HelloNeoPixel",
    packages=find_namespace_packages(),
    license="GPL v3",
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
