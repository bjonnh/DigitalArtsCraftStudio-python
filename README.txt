Playing with a Mattel Fischer-Price Digital Arts & Crafts Studio (DACS) that I found for $1.50 in a thrift store.
(http://service.mattel.com/us/TechnicalProductDetail.aspx?prodno=L1152&siteid=27&catid1=511)

This is a USB device that declares itself as a HID device (great, so no proprietary stuff involved, no IP and so on).

Made a python-based "driver" so this device can be used in GNU/Linux. This is not a Pointing device or keyboard driver, it is just a way for python programs to use the pen area (1024x768), the 25 buttons and the 4 leds.

I think I found all the possible interacting thingies on the DACS, but the lsusb -v output is attached just in case.

mattel.py the main class, requires:
- hidapi

mattelidi.py is just a demo of what can be done by using the DACS as a midi controller.

It is working with mido (a great midi library) with the portmidi backend, just connect that to a synth such as yoshimi.

By the way, this is a quick and dirty hack, don't expect too much from it (well the mattel.py is not that bad and mostly just lacks documentation, but there is a demo at the end of it that shows everything it can do).
