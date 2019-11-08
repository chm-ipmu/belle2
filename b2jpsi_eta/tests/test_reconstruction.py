from unittest import TestCase

import basf2 as b2
import pytest

from b2jpsi_eta.my_reconstruction.perform_reconstruction import Reconstruction


@pytest.fixture()
def my_path():
    return b2.create_path()


class TestReconstruction(TestCase):

    def test_jpsi2ee_eta2pipipi0(self):
        reco = Reconstruction("jpsi2ee_eta2pipipi0", path=my_path)
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2pipipi0(self):
        reco = Reconstruction("jpsi2mumu_eta2pipipi0", path=my_path)
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2ee_eta2pipigamma(self):
        reco = Reconstruction("jpsi2ee_eta2pipigamma", path=my_path)
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2pipigamma(self):
        reco = Reconstruction("jpsi2mumu_eta2pipigamma", path=my_path)
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert reco.has_eta2pipigamma

    def test_jpsi2ee_eta2gammagamma(self):
        reco = Reconstruction("jpsi2ee_eta2gammagamma", path=my_path)
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta2gammagamma(self):
        reco = Reconstruction("jpsi2mumu_eta2gammagamma", path=my_path)
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert reco.has_eta2gammagamma
        assert not reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2ee_eta23pi0(self):
        reco = Reconstruction("jpsi2ee_eta23pi0", path=my_path)
        assert reco.has_jpsi2ee
        assert not reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_jpsi2mumu_eta23pi0(self):
        reco = Reconstruction("jpsi2mumu_eta23pi0", path=my_path)
        assert not reco.has_jpsi2ee
        assert reco.has_jpsi2mumu
        assert not reco.has_eta2pipipi0
        assert not reco.has_eta2gammagamma
        assert reco.has_eta23pi0
        assert not reco.has_eta2pipigamma

    def test_fill_particle_lists(self):
        self.fail()

    def test_reconstruct_jpsi_decay(self):
        self.fail()

    def test_reconstruct_eta_decay(self):
        self.fail()

    def test_truth_match_all(self):
        self.fail()

    def test_rave_vertex_reconstruction(self):
        self.fail()

    def test_reconstruction(self):
        self.fail()
