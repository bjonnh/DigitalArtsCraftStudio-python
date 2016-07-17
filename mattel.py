# Mattel Fischer-Price Digital Arts & Crafts Studio (DACS) linux "driver"
# Copyright (C) 2016 Jonathan Bisson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hid
import time


class Pen:
    def __init__(self):
        self.click = False
        self.x = 0
        self.y = 0

    @property
    def click(self):
        return self.__click

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @click.setter
    def click(self, val):
        self.__click = val

    @x.setter
    def x(self, val):
        if val != 0xffff:
            self.__x = val

    @y.setter
    def y(self, val):
        if val != 0xffff:
            self.__y = val


class MattelData:
    def __init__(self, rawdata=None):
        # The four top buttons
        self.buttons = [False]*25
        self.pen = Pen()
        # 0 pen, 1 spray, 2 brush, 3 pencil,
        # 4 back, 5 explosion, 6 wand,
        # 7 letters, 8 picture, 9 stamp,
        # 10 paint can, 11 slider
        # 12 color wheel
        # 13 red, 14 white, 15 black
        # 16 brown, 17 purple, 18 blue
        # 19 green, 20 yellow, 21 orange
        # 22 print, 23 home, 24 power

        if rawdata is not None:
            self.from_raw(rawdata)

    def from_raw(self, rawdata):
        self.buttons[0] = rawdata[5] & 16 > 0
        self.buttons[1] = rawdata[4] & 16 > 0
        self.buttons[2] = rawdata[3] & 16 > 0
        self.buttons[3] = rawdata[2] & 16 > 0
        self.buttons[4] = rawdata[1] & 4 > 0
        self.buttons[5] = rawdata[5] & 8 > 0
        self.buttons[6] = rawdata[4] & 8 > 0
        self.buttons[7] = rawdata[3] & 8 > 0
        self.buttons[8] = rawdata[2] & 8 > 0
        self.buttons[9] = rawdata[1] & 8 > 0
        self.buttons[10] = rawdata[5] & 4 > 0
        self.buttons[11] = rawdata[6] & 1 > 0
        self.buttons[12] = rawdata[3] & 1 > 0
        self.buttons[13] = rawdata[2] & 1 > 0
        self.buttons[14] = rawdata[1] & 1 > 0
        self.buttons[15] = rawdata[5] & 2 > 0
        self.buttons[16] = rawdata[4] & 2 > 0
        self.buttons[17] = rawdata[3] & 2 > 0
        self.buttons[18] = rawdata[2] & 2 > 0
        self.buttons[19] = rawdata[1] & 2 > 0
        self.buttons[20] = rawdata[5] & 1 > 0
        self.buttons[21] = rawdata[4] & 1 > 0
        self.buttons[22] = rawdata[4] & 4 > 0
        self.buttons[23] = rawdata[3] & 4 > 0
        self.buttons[24] = rawdata[1] & 16 > 0
        self.pen.click = rawdata[6] & 2 == 0
        self.pen.x = (rawdata[8] << 8) + rawdata[7]
        self.pen.y = (rawdata[10] << 8) + rawdata[9]


class Mattel:
    def __init__(self):
        self.data = MattelData()
        self.opened = False
        self.leds = [0]*4

    def open(self):
        self.device = hid.device()
        self.device.open(0x813, 0x1006)
        self.opened = True

    def set_led(self, number, status):
        if number >= 0 and number < 4:
            if isinstance(status, bool):
                self.leds[number] = int(status)
                self.update_leds()

    def write(self, value):
        if self.opened:
            self.device.write(value)

    def read(self):
        if self.opened:
            self.data.from_raw(self.device.read(11))
        return None

    def update_leds(self):
        self.write([0, 0, self.leds[0] +
                    (self.leds[1] << 1) +
                    (self.leds[2] << 2) +
                    (self.leds[3] << 3)])


if __name__ == '__main__':
    mattel = Mattel()
    mattel.open()
    for i in range(0, 4):
        mattel.set_led(i, True)
        time.sleep(0.1)
        mattel.set_led(i, False)

    while True:
        mattel.read()
        print(''.join([str(button)[0] for button in mattel.data.buttons]) +
              " {} {} {}".format(mattel.data.pen.click,
                                 mattel.data.pen.x,
                                 mattel.data.pen.y))
