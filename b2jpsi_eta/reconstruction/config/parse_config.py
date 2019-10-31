class Track:
    def __init__(self, track):
        self.track = track.strip()
        self.is_charged = "+" in self.track or "-" in self.track
        self.q_agnostic = self.track.replace("+", "").replace("-", "")
        self.for_fitting = f"^{self.track}" if self.is_charged else self.track

    def __repr__(self):
        return f"Track({self.track})"


class ParseDecay:
    def __init__(self, string):
        self.string = string
        mother, daughters = self.string.split("->")
        self.mother = mother.strip()
        self.daughters = [x.strip() for x in daughters.split()]

    def __str__(self):
        fit_daughters = ' '.join([Track(x).for_fitting for x in self.daughters])
        string = f"[{self.mother!s} -> {fit_daughters!s}] "
        return string

    def __repr__(self):
        string = f"ParseDecay({self.string!r}) [m={self.mother!r}, d={self.daughters!r}]"
        return string


class DecayList(list):

    def __init__(self, a_list=None):
        if a_list is not None:
            super(DecayList, self).__init__(
                ParseDecay(x) for x in a_list
            )
        else:
            super(DecayList, self).__init__()

    @property
    def mothers(self):
        return [item.mother for item in self]

    @property
    def daughters(self):
        # Flatten singly nested list
        from itertools import chain
        return list(chain(*[item.daughters for item in self]))

    # Get list of final state particles
    def get_fsps(self, unique_only=True):
        ret = []
        for d in self.daughters:
            is_fsp = d not in self.mothers
            if is_fsp:
                ret.append(d)

        # Clean-up charge conjugates
        def rm_charge(x):
            if "-" in x:
                x = x.replace("-", "+")
            return x

        ret = [rm_charge(x) for x in ret]

        if unique_only:
            ret = set(ret)

        return ret

    # Return head particle of decay chain
    def get_head(self):
        for m in self.mothers:
            if m not in self.daughters:
                return m

    def decay_dict(self):
        return {x.mother: x for x in self}

    def get_chain(self):
        decay_dict = dict(self.decay_dict())
        head = self.get_head()
        chain = str(decay_dict.pop(head))
        print(decay_dict)

        def check(string, particle):
            return particle in string and f"[{particle} ->" not in string

        while any(check(chain, x) for x in self.mothers):
            for m, sub_decay in decay_dict.items():
                while m in chain and f"{m} ->" not in chain:
                    chain = chain.replace(m, str(sub_decay))

        # Trim initial '[' and final '] ', which are not needed
        chain = chain[1:-2]

        return chain
