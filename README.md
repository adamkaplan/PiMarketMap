# PiMarketMap

Realtime stock market heat map using Raspberry Pi &amp; Unicorn pHAT

![Market Heat Map](https://github.com/storage/user/12445/files/6eee7b00-4cc2-11e9-888b-120b57a6fcbf)

## Table of Contents

- [Background](#background)
- [Instructions for Raspbian Linux](#instructions-for-raspbian-linux)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#Usage)
- [Instructions for macOS Mojave](#instructions-for-macos-mojave)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#Usage)
- [Contributing](#contributing)
- [Maintainers](#maintainers)
- [License](#license)

## Background

PiMarketMap provides realtime visualization of U.S. market conditions, using a Unicorn pHAT and Raspberry Pi (A/B or Zero). It utilizes Yahoo Finance APIs to get the list of 30 stocks in the Dow Jones Industrial Average. It also fetches the current market values for those stocks, a subscribes to realtime streaming price updates.

The day change state of all 30 DJI stocks are displayed using 32 RGB LED lights on the Unicorn pHAT. Stocks which are up for the current trading period, are green, stocks that are down are red, and stocks that have not changed are blue. When an update comes in, the red/green/blue lights flash to a  brighter saturation for a brief period before returning to the base color.

## Instructions for Raspbian Linux

### Requirements

#### Hardware
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero-w/) (Pi A and B should work, but not tested)
- [Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat#description)
- [8 GB MicroSD card](https://www.microcenter.com/product/486146/micro-center-16gb-microsdhc-class-10-flash-memory-card) with Raspbian Stretch image
- [USB cable for power (Micro-B to A)](https://www.microcenter.com/product/485276/usb-20-(type-a)-to-micro-usb-(type-b)-male-cable-3-ft---black)
- _Optional_ [Custom Case](https://www.c4labs.com/product/zebra-zero-heatsink-case-raspberry-pi-zero-zero-w-color-options/)
- _Optional_ [LED Diffuser](https://shop.pimoroni.com/products/phat-diffuser)

#### Software
- Python3 (3.5 and 3.7 tested)

### Installation

### Raspian Stretch

Switch to Python 3
```
sudo apt-get install --yes --force-yes python3-pip
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.5 2
```

Clone this project and install dependencies
```
git clone git@github.com:adamkaplan/PiMarketMap.git
cd PiMarketMap
sudo pip3 install -r requirements.txt
```

### Usage

Run (root is required for GPIO access)
```
sudo ./pimarketmap.py
```

#### Running automatically on boot

```
sudo cp etc/systemd/system/marketmap.service /etc/systemd/system/marketmap.service
sudo systemctl daemon-reload
sudo systemctl enable marketmap
```

Now the service will start whenever the Pi boots up. Control the service manually like this:
```
# Stop
sudo systemctl stop marketmap
# Start
sudo systemctl start marketmap
# output is logged to /var/log/syslog
```

Side note: if you need to make the Pi join wifi networks on boot, [read this](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/setting-up-wifi-with-occidentalis)

## Instructions for MacOS Mojave

### Requirements

- Python [3.7.0](https://github.com/pygame/pygame/issues/555#issuecomment-471258085) [Download install package](https://www.python.org/ftp/python/3.7.0/python-3.7.0-macosx10.9.pkg). macOS Mojave ship with 3.7.2, which does not work.

### Installation

Clone this project and install *dev* dependencies.
```
git clone git@github.com:adamkaplan/PiMarketMap.git
cd PiMarketMap
pip3 install -r dev_requirements.txt
```
### Usage

Run in the pHAT simulator, and enjoy!
```
python3 ./pimarketmap.py
```

Note: if you log messages, but only a gray box, you probably didn't install Python 3.7.0! See above.

## Contributing
Please refer to the contributing.md file for information about how to get involved. We welcome issues, questions, and pull requests. Pull Requests are welcome.

## Maintainers

- [Adam Kaplan](https://github.com/adamkaplan), Twitter: [@adkap](https://twitter.com/adkap)

## License

This project is licensed under the terms of the [MIT](LICENSE-MIT) open source license. Please refer to [LICENSE](LICENSE) for the full terms.