import unittest
import struct
import tempfile
from pathlib import Path

from import_adapter import canonical_name, adapt_image


class ImportIdentityTests(unittest.TestCase):
    def setUp(self):
        self.libs = {'s': ('libkernel', 1), 'q': ('libSceSharePlay', 1)}
        self.mods = {'J': ('libkernel', 257), 'q': ('libSceSharePlay', 257)}
        self.reference_libs = {'p': ('libkernel', 1), 'q': ('libc', 1)}
        self.reference_mods = {'J': ('libkernel', 257), 'q': ('libc', 257)}

    def translate(self, name):
        return canonical_name(name, self.libs, self.mods,
                              self.reference_libs, self.reference_mods)

    def test_ds3_procparam_resolves_to_existing_kernel_contract(self):
        self.assertEqual(self.translate('959qrazPIrg#s#J'), '959qrazPIrg#p#J')

    def test_unrelated_library_cannot_collide_with_bloodborne_libc(self):
        self.assertEqual(self.translate('abc#q#q'),
                         'abc#libSceSharePlay:1#libSceSharePlay:257')

    def test_version_mismatch_does_not_bind_to_old_contract(self):
        self.libs['s'] = ('libkernel', 2)
        self.assertEqual(self.translate('abc#s#J'), 'abc#libkernel:2#libkernel:257')

    def test_named_linker_import_is_preserved(self):
        self.assertEqual(self.translate('abc#libSceLibcInternal'), 'abc#libSceLibcInternal')

    def test_missing_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            self.translate('abc#missing#J')

    def test_only_import_names_change_in_linked_image(self):
        prefix = (struct.pack('<8s6Q', b'BBPROBE5', 4, 0, 1, 1, 1, 1)
                  + struct.pack('<6Q', 0, 0, 0, 0, 0, 1)
                  + bytes(56) + struct.pack('<Q', 1) + bytes(24)
                  + struct.pack('<3Q', 0, 4, 5))
        old_name = b'959qrazPIrg#s#J'.ljust(128, b'\0')
        suffix = bytes(32) + b'CODE'
        original = prefix + old_name + suffix
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder) / 'input', Path(folder) / 'output'
            source.write_bytes(original)
            changes = adapt_image(source, target,
                                  {'libraries': self.libs, 'modules': self.mods},
                                  {'libraries': self.reference_libs, 'modules': self.reference_mods})
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(target.read_bytes(), prefix + b'959qrazPIrg#p#J'.ljust(128, b'\0') + suffix)
            self.assertEqual(len(changes), 1)
            source.write_bytes(original[:-1])
            with self.assertRaisesRegex(ValueError, 'layout'):
                adapt_image(source, target, {}, {})


if __name__ == '__main__':
    unittest.main()
