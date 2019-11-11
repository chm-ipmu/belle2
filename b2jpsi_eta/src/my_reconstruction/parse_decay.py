import enum


def parse_decay(decay_string: str) -> enum.Enum:
    class DecayModeInfo(enum.Enum):
        # J/psi decays
        has_jpsi2ee = "jpsi2ee" in decay_string
        has_jpsi2mumu = "jpsi2mumu" in decay_string

        # eta decays
        has_eta2gammagamma = "eta2gammagamma" in decay_string
        has_eta2pipipi0 = "eta2pipipi0" in decay_string
        has_eta2pipigamma = "eta2pipigamma" in decay_string
        has_eta23pi0 = "eta23pi0" in decay_string

    cls = DecayModeInfo

    return cls
