import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import time
from dataclasses import dataclass, field

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU") # Ignoring warnings from whisper

@dataclass
class Recording:
    duration:int = 10
    fs:int = 16000

    def record_audio(self) -> np.array:
        print()
        print("Hi, I am listening. What command would you like to execute?")
        recording = sd.rec(
            int(self.duration * self.fs),
            samplerate=self.fs,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        print("Ok, your command has been successfully recorded!")
        print()
        recording_int16 = (recording * 32767).astype(np.int16)

        return recording_int16

    def speech_to_text(self, write:bool=False) -> str:

        audio = self.record_audio()

        # Writing audio to a temporary file so whisper can read it (whisper needs a file)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            wav.write(tmp_file.name, self.fs, audio)
            tmp_path = tmp_file.name

        model = whisper.load_model("base")
        result = model.transcribe(tmp_path)

        if write:
            with open("transcribed.txt", "w", encoding="utf-8") as f:
                f.write(result["text"])

        os.unlink(tmp_path)

        return result["text"]

@dataclass
class Parse:
    stt: str
    foods:tuple[str, str] = ("apple", "pepper")
    colors:tuple[str, str] = ("red", "green")
    dumps:tuple[str, str] = ("box", "cup")
    words: list[str] = field(init = False)

    def __post_init__(self):
        ws = self.stt.split(" ")
        self.words = [w.strip().rstrip(".,!?").lower() for w in ws]

    def read_stt(self) -> tuple[int | None, int | None]:

        pick_indx, drop_indx = None, None

        for i in range(len(self.words)):
            curr_word = self.words[i]
            if pick_indx is None and curr_word == "pick":
                pick_indx = i
            if drop_indx is None and curr_word == "drop":
                drop_indx = i

        return pick_indx, drop_indx

    def picking(self, indx1:int, indx2:int) -> tuple[str | None, str | None]:

        food, color = None, None
        search = self.words[indx1:indx2]

        for i in range(len(search)):
            if search[i] in self.foods:
                food = search[i]
                color = search[i - 1] # Fruits to pick up are given in shape "color fruit"

        try:
            color_ok = False if color not in self.colors else True
            food_ok = False if food not in self.foods else True

            if not color_ok or not food_ok:
                raise ValueError(f"Something is wrong with the parsed PICKING instruction: {color_ok=}, {food_ok=}!")

        except ValueError:

            print()
            print("Something went wrong, please speak again when prompted.")
            time.sleep(1)

            while True:
                stt = Recording(duration=5).speech_to_text()
                parsed1 = Parse(stt)
                color, food = parsed1.picking(0, -1)
                return color, food

        return color, food

    def dropping(self, indx:int) -> str:

        dump = None
        search = self.words[indx:]

        for w in search:
            if w in self.dumps:
                dump = w

        if dump is None:

            print()
            print("Release object is not recognized!")
            
            while True:
                stt = Recording(duration=5).speech_to_text()
                parsed1 = Parse(stt)
                for word in parsed1.words:
                    if word in self.dumps:
                        return word
        return dump

    def extract(self) -> None | dict[str]:

        try:
            pick_idx, drop_idx = self.read_stt()
            if pick_idx is None or drop_idx is None:
                raise ValueError("Action of picking or dropping was not recognized!")

        except ValueError as err:
            print()
            print(f"The following error occured: {err}. You will be prompted to re-enter the instruction now.")
            print("For moving the object use \"pick\" and for releasing the object use \"drop\".")
            time.sleep(5)
            stt1 = Recording().speech_to_text()
            return Parse(stt1).extract()

        color, food = self.picking(pick_idx, drop_idx)
        dump = self.dropping(drop_idx)

        return {"pick": color + " " + food, "drop": dump}

if __name__ == "__main__":

    # Use example:
    stt = Recording().speech_to_text()
    whattodo = Parse(stt)
    print(whattodo.words)
    print(whattodo.extract())

