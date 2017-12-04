from setuptools import setup, find_packages

setup(
    name="piledmatrix",
    version="1.0.0",
    url="https://github.com/jonayet/piledmatrix",
    download_url="https://github.com/jonayet/piledmatrix/tarball/1.0.0",
    author="Jonayet Hossain",
    author_email="jonayet.bu@gmail.com",
    description="Python library for RaspberryPi for interfacing LED matrix array with MAX7219 chip.",
    packages=["piledmatrix"],
    zip_safe=False,
    include_package_data=True,
    platforms="raspberry-pi",
    license="MIT",
    install_requires=[

    ]
)