from collections import defaultdict


class Cut:

    def __init__(self, name, cut_string, category):
        self.name = name
        self.cut_string = cut_string
        self.category = category

    def __repr__(self):
        return f"Cut({self.name!r}, {self.cut_string!r}, {self.category!r})"


class Particle:

    def __init__(self, particle):
        self.particle = particle
        charge = particle[-1]
        self.charge = charge if charge in "+-0" else None
        self.cuts = defaultdict(list)

    def add_cut(self, name=None, cut_string=None, category=None, cut=None):
        if cut is None:
            cut = Cut(name, cut_string, category)

        self.cuts[cut.category].append(cut)


def test_cuts():
    my_electron = Particle("e+")
    good_electrons = Cut(name="good", cut_string="electronID > 0.5 and abs(d0) < 1 and abs(z0) < 4",
                         category="default")
    my_electron.add_cut(good_electrons)
    print("done")
