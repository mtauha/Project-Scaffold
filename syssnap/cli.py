#!/usr/bin/env python3

import argparse
import os
from collectors import ALL_COLLECTORS
from utils.output import write_output
from utils.redact import redact_snapshot
from utils.diff import diff_snapshots
from utils.plugin import load_plugins
from utils.upload import upload_snapshot
from utils.crypto import compress_snapshot, encrypt_snapshot


def main():
    parser = argparse.ArgumentParser(
        description="SysSnap: Linux System Configuration Snapshot Tool"
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "txt"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--include", type=str, help="Comma-separated modules to include (default: all)"
    )
    parser.add_argument("--exclude", type=str, help="Comma-separated modules to skip")
    parser.add_argument(
        "--out", type=str, help="Write output to file (default: stdout)"
    )
    parser.add_argument("--redact", action="store_true", help="Redact sensitive fields")
    parser.add_argument(
        "--anonymize", action="store_true", help="Anonymize host/user/network fields"
    )
    parser.add_argument(
        "--compress", action="store_true", help="Compress output as ZIP"
    )
    parser.add_argument(
        "--encrypt", action="store_true", help="Encrypt output (prompt for passphrase)"
    )
    parser.add_argument(
        "--plugin-dir", type=str, default="plugins", help="Directory for user plugins"
    )
    parser.add_argument(
        "--upload-url", type=str, help="HTTP(S) endpoint to upload snapshot"
    )
    parser.add_argument("--diff", nargs=2, help="Compare two snapshots")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    # Load plugins
    user_plugins = load_plugins(args.plugin_dir)
    modules = set(ALL_COLLECTORS.keys()).union(user_plugins.keys())

    # Diff mode
    if args.diff:
        diff_result = diff_snapshots(args.diff[0], args.diff[1], fmt=args.format)
        print(diff_result)
        return

    # Filter modules
    include = set(args.include.split(",")) if args.include else modules
    exclude = set(args.exclude.split(",")) if args.exclude else set()
    final_modules = include - exclude

    # Collect system data
    snapshot = {}
    for module in final_modules:
        if module in ALL_COLLECTORS:
            if not args.quiet:
                print(f"Collecting: {module}...")
            snapshot[module] = ALL_COLLECTORS[module].collect()
        elif module in user_plugins:
            if not args.quiet:
                print(f"Collecting (plugin): {module}...")
            snapshot[module] = user_plugins[module].collect()
        else:
            print(f"Unknown module: {module}")

    # Redact/anonymize if requested
    if args.redact or args.anonymize:
        snapshot = redact_snapshot(
            snapshot, redact=args.redact, anonymize=args.anonymize
        )

    # Output formatting/writing
    output_path = args.out
    result_bytes = write_output(
        snapshot, fmt=args.format, out=output_path, as_bytes=True
    )

    # Compress/encrypt
    if args.compress:
        result_bytes = compress_snapshot(result_bytes, output_path)
    if args.encrypt:
        result_bytes = encrypt_snapshot(result_bytes, output_path)

    # Upload if needed
    if args.upload_url:
        upload_snapshot(result_bytes, args.upload_url, args.format)


if __name__ == "__main__":
    main()
