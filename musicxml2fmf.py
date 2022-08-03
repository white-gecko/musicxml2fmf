#!/usr/bin/env python3

import click
from lxml import etree

downsteps = {
    "C": ("B", -1),
    "D": ("C", 0),
    "E": ("D", 0),
    "F": ("E", 0),
    "G": ("F", 0),
    "A": ("G", 0),
    "B": ("A", 0),
}

# mapping:
# duration: (noteValue, dot, correction: (duration))
durations = {
    1: (8, "", None),
    2: (4, "", None),
    3: (4, ".", None),
    4: (2, "", None),
    5: (2, "", 1),  # rounded
    6: (2, ".", None),
    7: (2, ".", 1),  # rounded
    8: (1, "", None),
}

filetypeHeader = """Filetype: Flipper Music Format
Version: 0
BPM: {bpm}
Duration: {duration}
Octave: {octave}
Notes: """


class Note:
    def __init__(self, duration=1, step="C", sharp="", octave=5):
        self.duration = int(duration)
        self.step = step
        self.sharp = sharp
        self.octave = int(octave)

    def __str__(self):
        noteValue, dot, correction = durations[self.duration]
        correctionStr = ""
        if correction:
            correctionStr = ", " + str(Rest(correction))
        return f"{noteValue}{self.step}{self.sharp}{self.octave}{dot}" + correctionStr

    def __repr__(self):
        return f"<{self.duration}, {self.step}, {self.sharp}, {self.octave}>"

    def __add__(self, other):
        if (
            isinstance(other, Note)
            and self.step == other.step
            and self.octave == other.octave
            and self.sharp == other.sharp
        ):

            return [
                Note(self.duration + other.duration, self.step, self.sharp, self.octave)
            ]
        return [self, other]


class Rest:
    def __init__(self, duration=1):
        self.duration = int(duration)

    def __str__(self):
        noteValue, dot, correction = durations[self.duration]
        correctionStr = ""
        if correction:
            correctionStr = ", " + str(Rest(correction))
        return f"{noteValue}P{dot}" + correctionStr


@click.command()
@click.option("--input", help="File to read the MusicXML from (suffix: '.musicxml').")
@click.option("--output", help="File to write the Flipper Music to (suffix: '.fmf').")
@click.option(
    "--bpm", default=120, help="Beats per minute for the piece (default: 120)."
)
@click.option("--duration", default=8, help="Default duration of a tone (default: 8).")
@click.option("--octave", default=5, help="Default octave of a note (default: 5).")
def convert(input, output, bpm, duration, octave):
    defaultDuration = duration
    defaultOctave = octave
    flipperNotes = []
    overTie = False
    tree = etree.parse(input)
    musicXmlNotes = tree.xpath("//score-partwise/part/measure/note")
    for noteTag in musicXmlNotes:
        duration = noteTag.xpath("duration")[0].text
        if noteTag.xpath("rest"):
            flipperNotes.append(Rest(duration))
            continue
        alter = False
        if noteTag.xpath("pitch/alter"):
            alter = int(noteTag.xpath("pitch/alter")[0].text)
        step = noteTag.xpath("pitch/step")[0].text
        octave = int(noteTag.xpath("pitch/octave")[0].text)
        sharp = ""
        if alter:
            if alter < 0:
                step, octaveShift = downsteps[step]
                octave = octave + octaveShift
            sharp = "#"
        note = Note(duration, step, sharp, octave)
        if overTie:
            tiedNotes = flipperNotes[-1] + note
            flipperNotes = flipperNotes[:-1] + tiedNotes
        else:
            flipperNotes.append(note)
        if noteTag.xpath("notations/tied") or noteTag.xpath("notations/slur"):
            tieStart = False
            tieStop = False
            for tied in noteTag.xpath("notations/tied") + noteTag.xpath("notations/slur"):
                tieStart = tied.attrib["type"] in "start"
                tieStop = tied.attrib["type"] in "stop"
            if tieStart:
                overTie = True
            elif tieStop:
                overTie = False

    with open(output, "w") as o:
        o.write(
            filetypeHeader.format(
                bpm=bpm, duration=defaultDuration, octave=defaultOctave
            )
        )
        o.write(", ".join(str(n) for n in flipperNotes))
