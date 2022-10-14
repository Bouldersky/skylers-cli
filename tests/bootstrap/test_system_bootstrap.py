import pytest
import shutil

from skyler_cli.core.bootstrap.system import SystemBootstrapper, OS, MachineType


@pytest.fixture
def system_bootstrapper(tmp_path):
    system_bootstrapper = SystemBootstrapper(
        OS.OS_X, MachineType.DEV, is_personal=True, home_path=tmp_path
    )
    return system_bootstrapper


class TestBashrcBootstrap:
    def test_bashrc_created(self, tmp_path, system_bootstrapper):
        system_bootstrapper.bootstrap_system()
        assert (tmp_path / ".bashrc").exists(), ".bashrc should be created"

    def test_default_location_for_personal_machines(
        self, tmp_path, system_bootstrapper
    ):
        system_bootstrapper.is_personal = True
        system_bootstrapper.bootstrap_system()
        with (tmp_path / ".bashrc").open() as brc:
            assert "/tmp/defaultTerminalLocation" in brc.read()

    def test_default_location_for_work_machines(self, tmp_path, system_bootstrapper):
        system_bootstrapper.is_personal = False
        system_bootstrapper.bootstrap_system()
        with (tmp_path / ".bashrc").open() as brc:
            expected_path = tmp_path / ".defaultTerminalLocation"
            assert str(expected_path) in brc.read()

    # Test a small subset of aliases here to make sure that the templating code works,
    # but don't test all the aliases to avoid tight coupling to the details of my bashrc
    # which are likely to change often.

    def test_standard_alias_is_configured(self, tmp_path, system_bootstrapper):
        system_bootstrapper.bootstrap_system()
        with (tmp_path / ".bashrc").open() as f:
            brc = f.read()
            assert 'alias ..="cd .."' in brc

    def test_top_alias_if_htop_installed(
        self, tmp_path, system_bootstrapper, monkeypatch
    ):
        monkeypatch.setattr(shutil, "which", lambda x: "/some/path")
        system_bootstrapper.bootstrap_system()
        with (tmp_path / ".bashrc").open() as f:
            brc = f.read()
            assert 'alias top="htop"' in brc

    def test_no_top_alias_if_htop_not_installed(
        self, tmp_path, system_bootstrapper, monkeypatch
    ):
        monkeypatch.setattr(shutil, "which", lambda x: None)
        system_bootstrapper.bootstrap_system()
        with (tmp_path / ".bashrc").open() as f:
            brc = f.read()
            assert 'alias top="htop"' not in brc


class TestStaticFilesBootstrapped:
    def test_inputrc_created(self, tmp_path, system_bootstrapper):
        system_bootstrapper.bootstrap_system()
        assert (tmp_path / ".inputrc").exists(), ".inputrc should be created"
