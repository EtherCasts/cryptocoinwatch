from bitcoin import b58check_to_hex, hex_to_b58check, get_version_byte

def hex_pad(x):
    return "{0:#0{1}x}".format(x, 66)

def xhex(x):
    value = "{0:#x}".format(x)
    if len(value) % 2 != 0:
        value = "0x0" + value[2:]
    return value

def xint(x):
    if x == '0x':
        return 0
    return int(x, 16)

def address_to_hex(address):
    version = get_version_byte(address)
    hex_value = b58check_to_hex(address)
    return "0x%02x%s" % (version, hex_value)

def hex_to_address(value):
    if len(value) == 42:
        version = 0
        value = value[2:]
    elif len(value) == 44:
        version = int(value[:4], 16)
        value = value[4:]
    else:
        raise ValueError("Invalid length")

    return hex_to_b58check(value, magicbyte=version)

# TESTS

def test_address_to_hex_bitcoin():
    assert address_to_hex("1CQLd3bhw4EzaURHbKCwM5YZbUQfA4ReY6") == "0x007d13547544ecc1f28eda0c0766ef4eb214de1045"

def test_address_to_hex_bitcoin_script_hash():
    assert address_to_hex("36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2") == "0x053399bc19f2b20473d417e31472c92947b59f95f8"

def test_address_to_hex_dogecoin():
    assert address_to_hex("DHia1kvDH3Bz73cA1KXzHtjSF4cZC5njNC") == "0x1e89f62b9eeada09ae6d250f1c4d987abc3562c743"

def test_address_to_hex_litecoin():
    assert address_to_hex("Lbnu1x4UfToiiFGU8MvPrLpj2GSrtUrxFH") == "0x30b5bd079c4d57cc7fc28ecf8213a6b791625b8183"

def test_hex_to_address_bitcoin():
    assert hex_to_address("0x007d13547544ecc1f28eda0c0766ef4eb214de1045") == "1CQLd3bhw4EzaURHbKCwM5YZbUQfA4ReY6"

def test_hex_to_address_bitcoin_script_hash():
    assert hex_to_address("0x053399bc19f2b20473d417e31472c92947b59f95f8") == "36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2"

def test_hex_to_address_dogecoin():
    assert hex_to_address("0x1e89f62b9eeada09ae6d250f1c4d987abc3562c743") == "DHia1kvDH3Bz73cA1KXzHtjSF4cZC5njNC"

def test_hex_to_address_litecoin():
    assert hex_to_address("0x30b5bd079c4d57cc7fc28ecf8213a6b791625b8183") == "Lbnu1x4UfToiiFGU8MvPrLpj2GSrtUrxFH"
