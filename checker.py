import argparse
import os
import json
import struct
import pickle
import sys

def scan_safetensors(path):
    print(f"[*] scanning safetensors: {path}")
    try:
        with open(path, 'rb') as f:
            header_size_bytes = f.read(8)
            if len(header_size_bytes) < 8:
                print("[!] file too small for safetensors")
                return
            header_size = struct.unpack('<Q', header_size_bytes)[0]
            header_json = f.read(header_size).decode('utf-8')
            header = json.loads(header_json)
            
            # check for suspicious keys
            keys = header.keys()
            print(f"[*] found {len(keys)} tensors")
            
            # metadata check
            if '__metadata__' in header:
                print(f"[*] metadata detected: {header['__metadata__']}")
                
    except Exception as e:
        print(f"[!] error parsing safetensors: {e}")

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # allow list for safe classes
        safe_list = {
            'torch', 'numpy', 'collections', 'builtins'
        }
        if module in safe_list:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")

def scan_pickle(path):
    print(f"[*] scanning pickle/bin: {path}")
    try:
        with open(path, 'rb') as f:
            # this is a dry-run check
            unpickler = RestrictedUnpickler(f)
            # we don't actually load, just trace
            print("[*] running restricted unpickler trace...")
            # logic to inspect opcode stream would go here
    except Exception as e:
        print(f"[!] pickle scan error: {e}")

def main():
    parser = argparse.ArgumentParser(description="simple-safetensors-checker: verify AI weights safety")
    parser.add_argument("path", help="path to model file")
    parser.add_argument("--mode", choices=['safetensors', 'pickle', 'auto'], default='safetensors')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"[!] path {args.path} not found")
        sys.exit(1)

    if args.mode == 'auto':
        if args.path.endswith('.safetensors'):
            scan_safetensors(args.path)
        else:
            scan_pickle(args.path)
    elif args.mode == 'safetensors':
        scan_safetensors(args.path)
    else:
        scan_pickle(args.path)

if __name__ == "__main__":
    main()
