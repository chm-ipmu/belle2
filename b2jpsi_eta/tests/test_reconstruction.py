from unittest import TestCase

import basf2 as b2
import pytest

from constants.mode_info import mode2decay_string
from my_reconstruction.perform_reconstruction import Reconstruction


@pytest.fixture()
def my_path():
    return b2.create_path()


class TestReconstruction(TestCase):

    def test_jpsi2ee_eta2pipipi0(self):
        reco = Reconstruction("jpsi2ee_eta2pipipi0", path=my_path)
        assert reco.is_jpsi2ee_eta2pipipi0
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2pipipi0(self):
        reco = Reconstruction("jpsi2mumu_eta2pipipi0", path=my_path)
        assert reco.is_jpsi2mumu_eta2pipipi0
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2ee_eta2pipigamma(self):
        reco = Reconstruction("jpsi2ee_eta2pipigamma", path=my_path)
        assert reco.is_jpsi2ee_eta2pipigamma
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2pipigamma(self):
        reco = Reconstruction("jpsi2mumu_eta2pipigamma", path=my_path)
        assert reco.is_jpsi2mumu_eta2pipigamma
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert reco.has_eta2pipigamma

    def test_jpsi2ee_eta2gammagamma(self):
        reco = Reconstruction("jpsi2ee_eta2gammagamma", path=my_path)
        assert reco.is_jpsi2ee_eta2gammagamma
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2gammagamma(self):
        reco = Reconstruction("jpsi2mumu_eta2gammagamma", path=my_path)
        assert reco.is_jpsi2mumu_eta2gammagamma
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2ee_eta23pi0(self):
        reco = Reconstruction("jpsi2ee_eta23pi0", path=my_path)
        assert reco.is_jpsi2ee_eta23pi0
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta23pi0(self):
        reco = Reconstruction("jpsi2mumu_eta23pi0", path=my_path)
        assert reco.is_jpsi2mumu_eta23pi0
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_fill_particle_lists(self):
        pass

    def test_reconstruct_jpsi_decay(self):
        pass

    def test_reconstruct_eta_decay(self):
        pass

    def test_truth_match_all(self):
        pass

    def test_reconstruction(self):
        pass


@pytest.mark.parametrize("decay,expected", tuple(mode2decay_string.items()))
def test_decay_string(decay, expected):
    reco = Reconstruction(decay, path=my_path)
    assert reco.decay_string == expected
