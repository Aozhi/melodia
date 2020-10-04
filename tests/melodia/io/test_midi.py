import pytest

from melodia.io.midi import _format_var_len, _format_chunk


def test_format_var_len():
    assert _format_var_len(0x00000000) == bytes.fromhex('00')
    assert _format_var_len(0x00000040) == bytes.fromhex('40')
    assert _format_var_len(0x0000007F) == bytes.fromhex('7F')
    assert _format_var_len(0x00000080) == bytes.fromhex('8100')
    assert _format_var_len(0x00002000) == bytes.fromhex('C000')
    assert _format_var_len(0x00003FFF) == bytes.fromhex('FF7F')
    assert _format_var_len(0x00004000) == bytes.fromhex('818000')
    assert _format_var_len(0x00100000) == bytes.fromhex('C08000')
    assert _format_var_len(0x001FFFFF) == bytes.fromhex('FFFF7F')
    assert _format_var_len(0x00200000) == bytes.fromhex('81808000')
    assert _format_var_len(0x08000000) == bytes.fromhex('C0808000')
    assert _format_var_len(0x0FFFFFFF) == bytes.fromhex('FFFFFF7F')


def test_format_chunk():
    assert _format_chunk(b'MThd', b'\x00\x7F\x00\x80\x90\xFF\x76') == \
           b'MThd\x00\x00\x00\x07\x00\x7F\x00\x80\x90\xFF\x76'

    assert _format_chunk(b'MThd', b'') == b'MThd\x00\x00\x00\x00'
    assert _format_chunk(b'MThd', b'\x00') == b'MThd\x00\x00\x00\x01\x00'

    with pytest.raises(AssertionError):
        _format_chunk(b'', b'')

    with pytest.raises(AssertionError):
        _format_chunk(b'a', b'')

    with pytest.raises(AssertionError):
        _format_chunk(b'ab', b'')

    with pytest.raises(AssertionError):
        _format_chunk(b'abc', b'')

    assert _format_chunk(b'abcd', b'') == b'abcd\x00\x00\x00\x00'

    with pytest.raises(AssertionError):
        _format_chunk(b'abcde', b'')
