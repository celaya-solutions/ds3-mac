import struct


def canonical_name(name, libraries, modules, reference_libraries, reference_modules):
    parts = name.split('#')
    if len(parts) != 3:
        return name
    nid, library_id, module_id = parts
    try:
        library, module = libraries[library_id], modules[module_id]
    except KeyError as exc:
        raise ValueError(f'Unknown import identity in {name}') from exc
    reference_libs = {identity: key for key, identity in reference_libraries.items()}
    reference_mods = {identity: key for key, identity in reference_modules.items()}
    if library in reference_libs and module in reference_mods:
        return f'{nid}#{reference_libs[library]}#{reference_mods[module]}'
    # Never pass another game's local IDs through to Bloodborne's resolver.
    return f'{nid}#{library[0]}:{library[1]}#{module[0]}:{module[1]}'


def adapt_image(source, destination, game_module, reference_module):
    data = bytearray(source.read_bytes())
    magic, size, entry, segments, relocations, imports, flags = struct.unpack_from('<8s6Q', data)
    if magic != b'BBPROBE5':
        raise ValueError('Expected a freshly linked BBPROBE5 image')
    module_count, = struct.unpack_from('<Q', data, 96)
    pos = 104 + module_count * 56
    binding_count, = struct.unpack_from('<Q', data, pos)
    pos += 8 + binding_count * 24 + segments * 24
    if pos + imports * 128 + relocations * 32 + size != len(data):
        raise ValueError('Invalid linked image layout')
    changes = []
    for index in range(imports):
        start = pos + index * 128
        old = bytes(data[start:start + 128]).split(b'\0', 1)[0].decode('ascii')
        new = canonical_name(old, game_module['libraries'], game_module['modules'],
                             reference_module['libraries'], reference_module['modules'])
        encoded = new.encode('ascii')
        if len(encoded) >= 128:
            raise ValueError(f'Import name too long: {new}')
        if new != old:
            changes.append({'index': index, 'from': old, 'to': new})
            data[start:start + 128] = encoded.ljust(128, b'\0')
    if destination.resolve() == source.resolve():
        raise ValueError('Keep the original linked image for comparison')
    destination.write_bytes(data)
    return changes
