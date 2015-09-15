from pypuppetdb.package import (
    __title__, __author__, __license__,
    __year__, __copyright__)


def test_package():
    assert __title__ == 'pypuppetdb'
    assert __author__ == 'Daniele Sluijters'
    assert __license__ == 'Apache License 2.0'
    assert __year__ == '2013, 2014, 2015'
    assert __copyright__ == 'Copyright {0} {1}'.format(__year__, __author__)
