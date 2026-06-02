from __future__ import annotations

import argparse
import json
import sys

from .auth import (
    AuthError,
    get_missing_credentials,
    load_token,
    run_auth_flow,
)
from .config import DEFAULT_REDIRECT_PORT, DEFAULT_SCOPES, token_path
from .server import main as server_main
from .tools import list_activities, summarize_training


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strava-mcp",
        description="MCP server and CLI for Strava.",
    )
    sub = parser.add_subparsers(dest="command")

    auth = sub.add_parser("auth", help="Authorize Strava and save a local token.")
    auth.add_argument("--client-id", default=None, help="Strava API client ID.")
    auth.add_argument("--client-secret", default=None, help="Strava API client secret.")
    auth.add_argument("--port", type=int, default=DEFAULT_REDIRECT_PORT)
    auth.add_argument(
        "--scope",
        action="append",
        dest="scopes",
        help="OAuth scope. Can repeat.",
    )
    auth.add_argument(
        "--no-browser",
        action="store_true",
        help="Print URL instead of opening browser.",
    )

    sub.add_parser("token-path", help="Print local token path.")
    sub.add_parser("doctor", help="Check Strava credential and token setup.")
    sub.add_parser("logout", help="Delete local Strava token.")

    summary = sub.add_parser("summary", help="Print recent training summary as JSON.")
    summary.add_argument("--per-page", type=int, default=20)
    summary.add_argument("--after", default=None, help="ISO datetime lower bound.")
    summary.add_argument("--before", default=None, help="ISO datetime upper bound.")

    activities = sub.add_parser("activities", help="Print recent activities as JSON.")
    activities.add_argument("--per-page", type=int, default=10)
    activities.add_argument("--page", type=int, default=1)
    activities.add_argument("--after", default=None)
    activities.add_argument("--before", default=None)

    serve = sub.add_parser("serve", help="Run MCP stdio server. Same as no subcommand.")
    serve.set_defaults(command="serve")

    return parser


def _run_doctor() -> None:
    missing = get_missing_credentials()

    print("Strava MCP Doctor")
    print()
    if "STRAVA_CLIENT_ID" in missing:
        print("[FAIL] STRAVA_CLIENT_ID tidak ditemukan")
    else:
        print("[OK] STRAVA_CLIENT_ID ditemukan")

    if "STRAVA_CLIENT_SECRET" in missing:
        print("[FAIL] STRAVA_CLIENT_SECRET tidak ditemukan")
    else:
        print("[OK] STRAVA_CLIENT_SECRET ditemukan")

    try:
        token = load_token()
        expires_at = int(token.get("expires_at", 0))
        if expires_at > 0:
            print("[OK] Token ditemukan")
        else:
            print("[WARN] Token ditemukan tapi expires_at tidak valid")
    except AuthError:
        print("[FAIL] Token file belum tersedia atau tidak valid")

    print(f"[INFO] Token path: {token_path()}")
    print()
    if not missing:
        print("[INFO] Credentials siap. Jalankan `strava-mcp auth` kalau token belum ada.")
    else:
        print("[INFO] Setup belum lengkap. Tambahkan credentials lalu jalankan ulang.")


def _run_logout() -> None:
    path = token_path()
    if path.exists():
        path.unlink()
        print("Token Strava lokal sudah dihapus.")
    else:
        print("Token Strava lokal sudah tidak ada.")
    print(f"Token path: {path}")
    print()
    print("Credentials environment tidak dihapus.")
    print("Jalankan auth lagi untuk login ulang.")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "serve"):
        server_main()
        return

    try:
        if args.command == "auth":
            scopes = args.scopes or DEFAULT_SCOPES
            token = run_auth_flow(
                client_id=args.client_id,
                client_secret=args.client_secret,
                port=args.port,
                scopes=scopes,
                open_browser=not args.no_browser,
            )
            athlete = token.get("athlete", {})
            print("Strava MCP authorization successful.")
            if athlete:
                first = athlete.get("firstname", "")
                last = athlete.get("lastname", "")
                print(f"Athlete: {first} {last}".strip())
            print(f"Token saved to: {token_path()}")
        elif args.command == "doctor":
            _run_doctor()
        elif args.command == "logout":
            _run_logout()
        elif args.command == "token-path":
            print(token_path())
        elif args.command == "summary":
            _print_json(
                summarize_training(
                    per_page=args.per_page,
                    after=args.after,
                    before=args.before,
                )
            )
        elif args.command == "activities":
            _print_json(
                list_activities(
                    per_page=args.per_page,
                    page=args.page,
                    after=args.after,
                    before=args.before,
                )
            )
        else:
            parser.error(f"Unknown command: {args.command}")
    except AuthError as exc:
        print(f"Auth error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
