import pytest

from flask_events.anonymizer import Anonymizer


@pytest.mark.parametrize('original_ip,expected', [
    ('127.0.0.1', '127.0.0.0'),
    ('1.2.3.4', '1.2.3.0'),
    ('2001:1db8:85a3:3a4b:1a2a:8a2e:0370:7334', '2001:1db8:85a3::'),
    ('::ffff:129.144.52.38', '::ffff:129.144.52.0'),
])
def test_default_anonymizer(original_ip, expected):
    anonymizer = Anonymizer()
    ip = anonymizer.anonymize(original_ip)
    assert ip == expected


@pytest.mark.parametrize('ipv4_mask,ipv6_mask,original_ip,expected', [
    ('255.255.0.0', 'ffff::', '127.1.1.1', '127.1.0.0'),
    ('255.255.255.0', 'ffff:ffff::', '2001:1db8:85a3:3a4b:1a2a:8a2e:0370:7334', '2001:1db8::'),
])
def test_anonymizer_custom_mask(ipv4_mask, ipv6_mask, original_ip, expected):
    anonymizer = Anonymizer(ipv4_mask, ipv6_mask)
    ip = anonymizer.anonymize(original_ip)
    assert ip == expected
