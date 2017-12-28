import sys
import os
import re
from random import randint
from itertools import zip_longest
from shutil import get_terminal_size

def clear_screen():
    platform = sys.platform
    if platform in ("linux", "unix", "darwin", "cygwin"):
        os.system("clear")
    if platform in ("win32"):
        os.system("cls")


class Stage(object):
    def __init__(self):
        self.game_config = None
        self.game_logic = None

    def run(self, *args):
        return ""

class Exit(Stage):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        return None

class Welcome(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print("Witamy w grze Szemeredi online")
        print("Mamy nadzieję, że będzie się podobać!!!")

    def run(self, *args, **kwargs):
        clear_screen()
        self.draw()
        input("Wciśnij <enter> aby kontynuować ")
        return ""


class Level(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print("Wybierz strategie komputera")
        print("Wybieranie liczb po kolei (1)")
        print("Strategia losowa (2)")
        print("Strategia trudniejsza (3)")

    def run(self, *args, **kwargs):
        cmd = ""
        while cmd not in ["1", "2", "3"]:
            clear_screen()
            self.draw()
            cmd = input("Wybierz 1, 2 lub 3: ")
        self.config["Strategia"] = cmd
        return cmd


class Colors(Stage):
    def __init__(self):
        super().__init__()
        self.prompt = ">> "
    def draw(self):
        print("Wybierz Liczbe kolorów komputera")

    def run(self, *args):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input("Wpisz liczbę z przedziału [1, ..., inf]: ")
            try:
                cmd = int(cmd)
                break
            except:
                pass

        self.config["C"] = cmd
        return cmd

class Length(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print("Wybierz Długość Gry")

    def run(self, *args):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input("Wpisz liczbę z przedziału [1, ..., inf]: ")
            try:
                cmd = int(cmd)
                break
            except:
                pass

        self.config["L"] = cmd
        return cmd

class KLength(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print("Wybierz Długość Ciągu")

    def run(self, *args, **kwargs):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input("Wpisz liczbę z przedziału [1, ..., inf]: ")
            try:
                cmd = int(cmd)
                break
            except:
                pass

        self.config["K"] = cmd
        return cmd

class Game(Stage):
    def __init__(self):
        super().__init__()
        self.plansza = dict()
        self.strategie = (self.stategia_po_kolei, self.stategia_losowa, self.stategia_losowa)

    def draw(self):
        plansza = sorted(self.plansza.items())
        _, rows = get_terminal_size()
        height = int(rows/2) - 2
        batches = [plansza[i*height:(i+1)*height] for i in range(0, int(len(plansza)/height))]
        rest = len(plansza) % height
        if rest > 0:
            batches.append(plansza[-rest:])

        lines = list(zip_longest(*batches))

        for l in lines:
            s = ""
            for p in l:
                if p is None:
                    break
                num_str = str(p[0])
                num_str = " " * (3-len(num_str)) + num_str
                if p[1] is None:
                    s = s + "   {}:<--".format(num_str)
                else:
                    col_str = str(p[1])
                    col_str = col_str + " " * (2-len(col_str))
                    s = s + "   {}: {}".format(num_str, col_str)
            print(s)
            print("    ....  "*len(l))



    def stategia_po_kolei(self):
        if len(self.plansza) == 0:
            return 0
        max_t = max(self.plansza)
        return max_t + 1

    def stategia_losowa(self):
        t = randint(0, 500)
        while t in self.plansza:
            t = randint(0, 500)
        return t

    def win(self):
        return False

    def run(self, *args):
        strategia = self.strategie[int(self.config["Strategia"]) - 1]
        self.plansza = {}
        game_time = 0
        while True:
            if(self.win()):
                return True
            if(game_time > self.config["L"]):
                return False
            t = strategia()
            self.plansza[t] = None

            clear_screen()
            self.draw()
            try:
                while True:
                    try:
                        cmd = input("Podaj kolor z przedziału [1, ..., {}] ".format(self.config["C"]))
                        cmd = int(cmd)
                        assert 1 <= cmd <= self.config["C"]
                        break
                    except (ValueError, AssertionError):
                        clear_screen()
                        self.draw()
                self.plansza[t] = cmd
            except KeyboardInterrupt:
                return False
            game_time = game_time + 1

class Retry(Stage):
    def draw(self, win):
        if win:
            print("Gratulacje!! Wygrałeś")
        else:
            print("Niestety przegrałeś")
        print("Dziękujemy za grę!!")

    def run(self, *args):
        clear_screen()
        self.draw(args[0])
        cmd = input("Czy chcesz kontynuować?? [T]ak, [N]ie, [Z]mień parametry ")
        return cmd

class GameLogic(object):
    def __init__(self):
        self.stages = dict()
        self._plan = list()
        self.config = dict(K=5, C=3, L=100, Strategia="1")
        self.name_counter = 1

    def add_screens(self, *args):
        if len(args) % 2 == 1:
            raise ValueError("number of args must be event")
        for name, stage in zip(args[::2], args[1::2]):
            stage.config = self.config
            stage.game_logic = self
            self.stages[name] = stage
        return self

    def start(self, stage_name):
        assert stage_name in self.stages
        self._plan = []
        self._plan.append(stage_name)
        return self

    def then(self, stage_name):
        assert len(self._plan) > 0
        assert stage_name in self.stages or 0 <= stage_name < len(self._plan)
        self._plan.append(stage_name)
        return self

    def choice(self, *args):
        assert len(args) % 2 == 0
        self._plan.append(tuple(args))
        return self

    def jump(self, stage):
        if isinstance(stage, int):
            assert 0 <= stage < len(self._plan)
            self._plan.append(stage)
        elif isinstance(stage, str):
            s = self._plan[-1]
            idx = len(self._plan)
            while idx > 0 and s != stage:
                idx = idx - 1
                s = self._plan[idx]
            else:
                raise ValueError("Stage not found!!")
            self._plan.append(idx)
        else:
            raise ValueError("stage must be int or str")

        return self

    def resolve_choice(self, choices, result):
        pairs = zip(choices[::2], choices[1::2])
        return next(filter(lambda x: re.match(x[0], result), pairs))[1]

    def run(self):
        idx = 0
        result = ""
        while result is not None and idx < len(self._plan):
            stage_tag = self._plan[idx]
            if isinstance(stage_tag, int):
                idx = stage_tag
                stage_tag = self._plan[stage_tag]

            if isinstance(stage_tag, tuple):
                stage_tag = self.resolve_choice(stage_tag, result)
                if isinstance(stage_tag, int):
                    idx = stage_tag
                    stage_tag = self._plan[stage_tag]

            stage = self.stages[stage_tag]
            result = stage.run(result)
            idx = idx + 1


if __name__ == "__main__":
    game_logic = GameLogic()
    game_logic.add_screens('welcome', Welcome(), 'colors', Colors(),
                           'length', Length(), 'klength', KLength(),
                           'level', Level(), 'game', Game(),
                            'retry', Retry(), 'exit', Exit())

    (game_logic.start('welcome')
               .then('colors')
               .then('length')
               .then('klength')
               .then('level')
               .then('game')
               .then('retry')
               .choice("Z|z|zmien|Zmien|Zmień|zmień", 1,
                       "N|n|No|no|nie|Nie", "exit",
                       "Y|y|Yes|yes|t|T|Tak|tak", 5))

    game_logic.run()
