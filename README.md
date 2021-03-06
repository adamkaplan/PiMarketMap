# PiMarketMap

Realtime stock market heat map using Raspberry Pi &amp; Unicorn pHAT

![Market Heat Map](https://github.com/adamkaplan/PiMarketMap/blob/images/6eee7b00-4cc2-11e9-888b-120b57a6fcbf.gif)

## Table of Contents

- [Background](#background)
  - [Shutting Down The Pi](#shutting-down-the-pi)
  - [LED Light Legend](#led-light-legend)
  - [WiFi Setup](#wifi-setup)
- [Instructions for Raspbian Linux](#instructions-for-raspbian-linux)
  - [Requirements](#requirements-raspbian)
  - [Installation](#installation-raspbian)
  - [Usage](#usage-raspbian)
- [Instructions for macOS Mojave](#instructions-for-macos-mojave)
  - [Requirements](#requirements-macos)
  - [Installation](#installation-macos)
  - [Usage](#usage-macos)
- [Contributing](#contributing)
- [Maintainers](#maintainers)
- [License](#license)

## Background

PiMarketMap provides realtime visualization of U.S. market conditions, using a Unicorn pHAT and Raspberry Pi (A/B or Zero). It utilizes Yahoo Finance APIs to get the list of 30 stocks in the Dow Jones Industrial Average. It also fetches the current market values for those stocks, a subscribes to realtime streaming price updates.

The day change of [all 30 DJI stocks](https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI) is displayed using 30 RGB LED lights on the Unicorn pHAT. The last two lights depict the Pound vs the US Dollar, and the Yen vs the US Dollar. Stocks which are up for the current trading day, are green. Stocks that are down are red. Stocks that have not changed value are blue.

When an update comes in, the red/green/blue lights flash to a brighter saturation for a brief period before returning to the base color.

### LED Light Legend

The Dow 30 stocks are sorted by market cap such that the most valuable company occupies the first light, and the lowest value company occupies the last spot. The "first light" is the top-left light if you are holding the Pi such that the word "Unicorn" is on the left side. The lights progress down, and to the left. The 4th largest Dow component is the bottom light of the first/left column, and the 5th largest Dow component is the first light at the top of the second column from the left.

As of March 2019, this is the LED to Stock mapping:
```
 ___________________________________________
|  MSFT XOM  PG   PFE  HD   MCD  MMM  GS    |
|  AAPL V    VZ   CSCO BA   NKE  UTX  BTC*  |
|  FB*  JPM  INTC UNH  KO   IBM  AXP  WBA   |
|  JNJ  WMT  CVX  MRK  DIS  DWDP CAT  TRV   |
|-------------------------------------------|
|o : : : : : : : : : : : : : : : : : : : : o|
'-------------------------------------------'
```

### Shutting Down The Pi
 
It's very easy to properly shut down your PiMarketMap, so do it properly! Simply short the two left most jumpers using a paper clip or the end of a USB cable. It will shut off within 2 seconds.
```
 ___________________________________________
|  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]   |
|  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]   |
|  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]   |
|  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  [ ]   |
|-------------------------------------------|
|o : : : : : : : : : : : : : : : : : : : : o|
'-------------------------------------------'
   /\
 Touch these two together with a paperclip!
```

### WiFi Setup

If you want to set a custom WiFi, shut down the PiMarketMap. Remove the SD card, and insert it into a computer. On the "boot" volume (which on macOS will automatically appear at `/Volumes/boot`), add a new file named `wpa_supplicant.conf` following the [format here](https://www.raspberrypi.org/forums/viewtopic.php?t=203716#p1264992). Or, copy paste this into the Terminal:

```
echo 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
  ssid="YOUR_NETWORK_NAME"
	psk="YOUR_PASSWORD"
	id_str="MY_WIFI_LABEL"
	priority=100
	key_mgmt=WPA-PSK
}

network={
  ssid="YOUR_NETWORK_NAME"
	id_str="MY_WIFI_LABEL_NO_PASSWORD"
	priority=50
	key_mgmt=NONE
}' > /Volumes/boot/wpa_supplicant.conf
```

## Instructions for Raspbian Linux

### Requirements Raspbian

#### Hardware
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero-w/) (Pi A and B should work, but not tested)
- [Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat#description)
- [8 GB MicroSD card](https://www.microcenter.com/product/486146/micro-center-16gb-microsdhc-class-10-flash-memory-card) with Raspbian Stretch image
- [USB cable for power (Micro-B to A)](https://www.microcenter.com/product/485276/usb-20-(type-a)-to-micro-usb-(type-b)-male-cable-3-ft---black)
- _Optional_ [Custom Case](https://www.c4labs.com/product/zebra-zero-heatsink-case-raspberry-pi-zero-zero-w-color-options/)
- _Optional_ [LED Diffuser](https://shop.pimoroni.com/products/phat-diffuser)

#### Software
- Python3 (3.5 and 3.7 tested)

### Installation Raspbian

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

### Usage Raspbian

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

### Requirements macOS

- Python [3.7.0](https://github.com/pygame/pygame/issues/555#issuecomment-471258085) [Download install package](https://www.python.org/ftp/python/3.7.0/python-3.7.0-macosx10.9.pkg). macOS Mojave ship with 3.7.2, which does not work.

### Installation macOS

Clone this project and install *dev* dependencies.
```
git clone git@github.com:adamkaplan/PiMarketMap.git
cd PiMarketMap
pip3 install -r dev_requirements.txt
```
### Usage macOS

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
