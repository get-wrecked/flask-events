from ipaddress import ip_address


class Anonymizer:
    def __init__(self,
            ipv4_mask='255.255.255.0',
            ipv6_mask='ffff:ffff:ffff:0000:0000:0000:0000:0000',
    ):
        '''
        Null out the last octet in IPv4, and everything after the NLA in IPv6
        by default. See rfc 2374, section 3.1 for the unicast structure of IPv6
        addresses.
        '''
        self.ipv4_mask = ip_address(ipv4_mask)
        self.ipv6_mask = ip_address(ipv6_mask)


    def anonymize(self, original_ip):
        address = ip_address(original_ip)

        if address.version == 6:
            if address.ipv4_mapped:
                return self._anonymize_mapped(address)
            return _anonymize_address(address, self.ipv6_mask)

        return _anonymize_address(address, self.ipv4_mask)


    def _anonymize_mapped(self, address):
        masked_ip = ['::ffff:']
        for original_byte, mask_byte in zip(address.ipv4_mapped.packed, self.ipv4_mask.packed):
            if len(masked_ip) != 1:
                masked_ip.append('.')
            masked_ip.append('%d' % (original_byte & mask_byte))
        return ''.join(masked_ip)


def _anonymize_address(address, mask):
    masked_ip = bytearray()
    for original_byte, mask_byte in zip(address.packed, mask.packed):
        masked_ip.append(original_byte & mask_byte)
    return ip_address(bytes(masked_ip)).compressed
