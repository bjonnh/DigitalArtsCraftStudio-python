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




# TODO Add panic
# Set continuous to current/last channel
# 

import mido
import time
import mattel

rtmidi = mido.Backend('mido.backends.portmidi')
print(mido.get_input_names())
out = rtmidi.open_output("input")

mattel = mattel.Mattel()
mattel.open()

CHANNELS = 4

notes_playing = []

class Channel:
    def __init__(self, number, continuous=False, repeater=False):
        self.continuous = continuous
        self.number = number
        self.repeater = repeater
        self.notes_playing = []
        self.last_time = time.time()
        self.delay = 0.4
        self.duration = 0.1 # Only used for repeater
        self.last_note = None
    def stop(self, excepted = None, force = False):
        if self.repeater is True and time.time()<self.last_time+self.duration:
            return
        # The continuous continues to play
        if self.continuous is True and len(self.notes_playing)==1 and not force:
            return
        to_skip = 0
        if excepted is not None:
            to_skip = 1
        while(len(self.notes_playing)>to_skip):
            note = self.notes_playing[0]
            if note.note != excepted:
                msg = mido.Message('note_off', note=note.note, velocity=100,
                                   channel=note.channel)
                out.send(msg)
                self.notes_playing.remove(note)
    def play(self, new_note, internal=False, pen_was_on=False):
        if self.repeater is True and internal is False:
            self.last_note = new_note
            return

        self.last_note = new_note
        if self.continuous and pen_was_on is False:
            print("Force stop")
            self.stop(force=True)
        else:
            for note in self.notes_playing:
                if note.note == new_note:
                    print("We already play that")
                    return
        msg = mido.Message('note_on', note=new_note, velocity=100, channel=self.number)
        self.notes_playing.append(msg)
        out.send(msg)
        # If continuous, we stop all others
        if self.continuous is True:
            self.stop(excepted=new_note)

    def play_repeater(self):
        if self.repeater is False:
            return
        if (self.last_time+self.delay) <= time.time() and self.last_note is not None:
            self.last_time = time.time()
            self.play(self.last_note, True)
        elif self.last_note is not None:
            self.stop()

channels = []
for i in range(0, CHANNELS):
    channels.append(Channel(i))

# make Channel 1 continuous
channels[1].continuous = True

# make Channel 0 repeater
channels[0].repeater = True

pen_was_on = False
while True:
    mattel.read()
    for channel in channels:
        channel.play_repeater()
    
    if mattel.data.pen.click is True:
        note = int(mattel.data.pen.x*100.0/1024)
        channel = int(mattel.data.pen.y*CHANNELS/768)
        channels[channel].play(note, pen_was_on=pen_was_on)
        pen_was_on = True
    if mattel.data.pen.click is False:
        for channel in channels:
            channel.stop()
        pen_was_on = False
