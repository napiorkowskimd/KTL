import sys
import os
import re
from random import randint
from itertools import zip_longest
from shutil import get_terminal_size
from operator import itemgetter

def clear_screen():
    platform = sys.platform
    if platform in (u"linux", "unix", "darwin", "cygwin"):
        os.system(u"clear")
    if platform in (u"win32"):
        os.system(u"cls")

def get_LLAP(numbers):
    n = len(numbers)
    if n <= 2:
        return n

    llap = 2
    L = [x[:] for x in [[0]*n]*n]
    for i in range(n):
        L[i][-1] = 2

    for j in range(n-2, 0, -1):
        i, k = j-1, j+1
        while i >= 0 and k <= n-1:
            if numbers[i] + numbers[k] < 2*numbers[j]:
                k = k+1
            elif numbers[i] + numbers[k] > 2*numbers[j]:
                L[i][j] = 2
                i = i - 1
            else:
                L[i][j] = L[j][k] + 1
                llap = max(llap, L[i][j])
                i = i - 1
                k = k + 1

        while i >= 0:
            L[i][j] = 2
            i = i - 1

    return llap

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
        print(u"Witamy w grze Szemeredi online")
        print(u"Mamy nadzieję, że będzie się podobać!!!")

    def run(self, *args, **kwargs):
        clear_screen()
        self.draw()
        input(u"Wciśnij <enter> aby kontynuować ")
        return ""


class Level(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print(u"Wybierz strategie komputera")
        print(u"Wybieranie liczb po kolei (1)")
        print(u"Strategia losowa (2)")
        print(u"Strategia trudniejsza (3)")

    def run(self, *args, **kwargs):
        cmd = ""
        while cmd not in ["1", "2", "3"]:
            clear_screen()
            self.draw()
            cmd = input(u"Wybierz 1, 2 lub 3: ")
        self.config["Strategia"] = cmd
        return cmd


class Colors(Stage):
    def __init__(self):
        super().__init__()
        self.prompt = ">> "
    def draw(self):
        print(u"Wybierz liczbe dostępnych kolorów")

    def run(self, *args):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input(u"Wpisz liczbę z przedziału [1, ..., inf]: ")
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
        print(u"Wybierz długość gry")

    def run(self, *args):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input(u"Wpisz liczbę z przedziału [1, ..., 500]: ")
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
        print(u"Wybierz długość ciągu")

    def run(self, *args, **kwargs):
        cmd = ""
        while True:
            clear_screen()
            self.draw()
            cmd = input(u"Wpisz liczbę z przedziału [1, ..., inf]: ")
            try:
                cmd = int(cmd)
                break
            except:
                pass

        self.config["K"] = cmd
        return cmd


class PSize(Stage):
    def __init__(self):
        super().__init__()

    def draw(self):
        print(u"Wybierz wielkość planszy")

    def run(self, *args, **kwargs):
        if self.config["Strategia"] != "3":
            return 0
        cmd = ""
        game_length = self.config["L"]
        while True:
            clear_screen()
            self.draw()
            cmd = input(u"Wpisz liczbę z przedziału [{}, ..., 500]: ".format(game_length))
            try:
                cmd = int(cmd)
                assert game_length <= cmd <= 500
                break
            except:
                pass

        self.config["Size"] = cmd
        return cmd

class Game(Stage):
    def __init__(self):
        super().__init__()
        self.plansza = dict()
        self.strategie = (self.strategia_po_kolei, self.strategia_losowa, self.strategia_sprytna)
        self.naj_ciag = 0
        self.game_time = 0
        self.N = 10
        self.k = 1

    def get_color(self, color):
        return sorted(list(map(itemgetter(0), filter(lambda kc: kc[1]==color, self.plansza.items()))))

    def color_iter(self):
        return iter(range(1, self.config["C"] + 1))

    def draw(self):
        plansza = sorted(self.plansza.items())
        _, rows = get_terminal_size()
        height = int(rows/2) - 2
        batches = [plansza[i*height:(i+1)*height] for i in range(0, int(len(plansza)/height))]
        rest = len(plansza) % height
        if rest > 0:
            batches.append(plansza[-rest:])

        lines = list(zip_longest(*batches))

        print("Najdłuższy ciąg ma długość {} / {}, ruchy do wykorzystania: {}"
                .format(self.naj_ciag,
                        self.config["K"],
                        self.config["L"] - self.game_time))
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
            print(u"    ....  "*len(l))



    def strategia_po_kolei(self):
        if len(self.plansza) == 0:
            return 1
        max_t = max(self.plansza)
        return max_t + 1

    def strategia_losowa(self):
        t = randint(1, 2*self.config["L"] + 1)
        while t in self.plansza:
            t = randint(1, 2*self.config["L"] + 1)
        return t

    def strategia_sprytna(self):
        MAX_KROK = 6
        ans = -1
        max_score = 0
        goal = self.config["K"]
        max_size = self.config["Size"]
        if len(self.plansza) == 0:
            return randint(1, max_size)

        for p in range(1, max_size):
            if p in self.plansza:
                continue
            score = 0
            for c in self.color_iter():
                ciag = self.get_color(c)
                new_ciag = sorted(ciag + [p])
                dlugosc_ciagu = get_LLAP(new_ciag)
                if dlugosc_ciagu >= goal:
                    score = score + 2*dlugosc_ciagu
                else:
                    score = score + dlugosc_ciagu
                # import pdb; pdb.set_trace()
            if score > max_score:
                max_score = score
                ans = p

        if ans == -1:
            return max(self.plansza, default=0)+1

        return ans

    def ai_win(self):
        naj_ciag = 0
        for c in self.color_iter():
            naj_ciag_c = get_LLAP(self.get_color(c))
            if naj_ciag_c > naj_ciag:
                naj_ciag = naj_ciag_c

        self.naj_ciag = naj_ciag
        if self.naj_ciag >= self.config["K"]:
            return True

        return False

    def run(self, *args):
        strategia = self.strategie[int(self.config["Strategia"]) - 1]
        self.plansza = {}
        self.game_time = 0
        self.naj_ciag = 0
        end_game = False
        win = False
        while True:
            if self.ai_win():
                win = False
                end_game = True
            elif self.game_time >= self.config["L"]:
                win = True
                end_game = True

            if end_game:
                clear_screen()
                self.draw()
                if win:
                    cmd = input(u"Gratulacje!! Wygrałeś. Naciśnij dowolny przycisk, aby kontynuować")
                    return True
                else:
                    cmd = input(u"Niestety przegrałeś. Naciśnij dowolny przycisk, aby kontynuować")
                    return False

            t = strategia()
            self.plansza[t] = None

            clear_screen()
            self.draw()

            try:
                while True:
                    try:
                        cmd = input(u"Podaj kolor z przedziału [1, ..., {}] ".format(self.config["C"]))
                        cmd = int(cmd)
                        assert 1 <= cmd <= self.config["C"]
                        break
                    except (ValueError, AssertionError):
                        clear_screen()
                        self.draw()
                self.plansza[t] = cmd
            except KeyboardInterrupt:
                win = False
                end_game = True
                continue

            self.game_time = self.game_time + 1

class Retry(Stage):
    def draw(self, win):
        print(u"Dziękujemy za grę!!")

    def run(self, *args):
        clear_screen()
        self.draw(args[0])
        cmd = input(u"Czy chcesz kontynuować?? [T]ak, [N]ie, [Z]mień parametry ")
        return cmd

class GameLogic(object):
    def __init__(self):
        self.stages = dict()
        self._plan = list()
        self.config = dict(K=5, C=3, L=10, Strategia="3", Size=100)
        self.name_counter = 1

    def add_screens(self, *args):
        if len(args) % 2 == 1:
            raise ValueError(u"number of args must be event")
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
                raise ValueError(u"Stage not found!!")
            self._plan.append(idx)
        else:
            raise ValueError(u"stage must be int or str")

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
                           'psize', PSize(),
                           'level', Level(), 'game', Game(),
                            'retry', Retry(), 'exit', Exit())

    (game_logic.start('welcome')
               .then('colors')
               .then('length')
               .then('klength')
               .then('level')
               .then('psize')
               .then('game')
               .then('retry')
               .choice(u"Z|z|zmien|Zmien|Zmień|zmień", 1,
                       "N|n|No|no|nie|Nie", "exit",
                       "Y|y|Yes|yes|t|T|Tak|tak", 6))

    game_logic.run()
