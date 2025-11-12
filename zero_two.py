#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZERO TWO - APKs Toolkit for Termux
Version: 3.0.0
Author: Ghost Developer
GitHub: https://github.com/CHICO-CP
"""

import os
import sys
import zipfile
import shutil
import subprocess
import tempfile
import time
import platform
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------
# ANSI Colors (simple wrapper)
# ---------------------------
class Colors:
    ENABLE = True
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @classmethod
    def colorize(cls, text, color):
        if not cls.ENABLE:
            return text
        return f"{color}{text}{cls.RESET}"

# Detect if terminal likely supports colors
def terminal_supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if sys.platform.startswith("win"):
        # On Windows, newer consoles support ANSI; but keep it enabled and hope user has it.
        return True
    return sys.stdout.isatty()

Colors.ENABLE = terminal_supports_color()

# ---------------------------
# Utility helpers
# ---------------------------
def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def printc(msg, color=None, bold=False):
    out = msg
    if color:
        out = Colors.colorize(out, color)
    if bold:
        out = Colors.BOLD + out + Colors.RESET if Colors.ENABLE else out
    print(out)

# ---------------------------
# Main toolkit class
# ---------------------------
class ZeroTwo:
    def __init__(self, headless=False):
        self.name = "ZERO TWO"
        self.version = "3.0.0"
        self.developer = "Ghost Developer"
        self.github = "https://github.com/CHICO-CP/zero-two-toolkit"
        self.telegram = "@GhostDeve"
        self.logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file = os.path.join(self.logs_dir, "conversion_log.txt")
        self.termux = True if "termux" in os.environ.get('PREFIX', '') else False
        self.apktool_version = self.get_apktool_version()
        self.aapt_available = bool(shutil.which('aapt') or shutil.which('aapt2'))
        self.apksigner_available = bool(shutil.which('apksigner'))
        self.headless = headless
        self.github_api_release = "https://api.github.com/repos/CHICO-CP/zero-two-toolkit/releases/latest"
        self.build_banner()

    # ---------------------------
    # Banner & UI
    # ---------------------------
    def build_banner(self):
        # Single centered title "ZERO TWO"
        line = "═" * 55
        self.banner = f"""
{Colors.colorize('╔' + line + '╗', Colors.CYAN)}
{Colors.colorize('║' + ' ' * 55 + '║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}{Colors.colorize(self.name.center(55), Colors.MAGENTA)}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║' + ' ' * 55 + '║', Colors.CYAN)}
{Colors.colorize('╚' + line + '╝', Colors.CYAN)}
"""

    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def show_banner(self):
        print(self.banner)
        print(f"    {Colors.colorize('Version:', Colors.DIM)} {Colors.colorize(self.version, Colors.GREEN)}    {Colors.colorize('Developer:', Colors.DIM)} {self.developer}")
        print()

    def show_menu(self):
        menu = f"""
{Colors.colorize('╔' + '═'*60 + '╗', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('MAIN MENU'.center(58), Colors.CYAN)}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('╠' + '═'*60 + '╣', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('1.', Colors.CYAN)} Convert single .apks → .apk{' ' * 25}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('2.', Colors.CYAN)} Process directory (batch .apks){' ' * 32}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('3.', Colors.CYAN)} Decompile APK {' ' * 36}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('4.', Colors.CYAN)} Rebuild {' ' * 39}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('5.', Colors.CYAN)} Sign APK {' ' * 31}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('6.', Colors.CYAN)} Show APK info {' ' * 29}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('7.', Colors.CYAN)} Check for updates {' ' * 27}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('8.', Colors.CYAN)} Auto mode {' ' * 33}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('9.', Colors.CYAN)} Install missing dependencies{' ' * 28}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('10.', Colors.CYAN)} Show system info & credits{' ' * 26}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('║', Colors.CYAN)}  {Colors.colorize('11.', Colors.CYAN)} Exit{' ' * 52}{Colors.colorize('║', Colors.CYAN)}
{Colors.colorize('╚' + '═'*60 + '╝', Colors.CYAN)}
"""
        print(menu)
        print(f"    apktool: {Colors.colorize(self.apktool_version, Colors.GREEN if self.apktool_version!='Not installed' else Colors.RED)}    aapt: {Colors.colorize('OK' if self.aapt_available else 'MISSING', Colors.GREEN if self.aapt_available else Colors.RED)}")
        print()

    # ---------------------------
    # Logging
    # ---------------------------
    def save_log(self, action, status, details=""):
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{now_ts()}] ACTION: {action} | STATUS: {status} | DETAILS: {details}\n")
        except Exception:
            pass

    # ---------------------------
    # Shell helpers
    # ---------------------------
    def run_cmd(self, cmd, capture=False, timeout=None):
        try:
            if capture:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                return res.returncode, res.stdout + (res.stderr or "")
            else:
                res = subprocess.run(cmd, text=True, timeout=timeout)
                return res.returncode, ""
        except subprocess.TimeoutExpired:
            return -1, "timeout"
        except Exception as e:
            return -1, str(e)

    # ---------------------------
    # Core: .apks -> .apk
    # ---------------------------
    def list_apks_inside(self, apks_path):
        action = f"list_apks_inside {apks_path}"
        if not os.path.exists(apks_path):
            printc(f"    ❌ Error: {apks_path} not found.", Colors.RED)
            self.save_log(action, "FAIL", "file not found")
            return []

        temp_dir = tempfile.mkdtemp(prefix="zero_two_extract_")
        try:
            with zipfile.ZipFile(apks_path, 'r') as z:
                printc("    ⏳ Extracting .apks (this may take a few seconds)...", Colors.YELLOW)
                z.extractall(temp_dir)

            apk_files = []
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if f.lower().endswith('.apk'):
                        apk_files.append(os.path.join(root, f))
            self.save_log(action, "OK", f"{len(apk_files)} found")
            return apk_files
        except Exception as e:
            printc(f"    ❌ Error extracting: {e}", Colors.RED)
            self.save_log(action, "FAIL", str(e))
            shutil.rmtree(temp_dir, ignore_errors=True)
            return []

    def find_main_apk(self, apk_files):
        # prefer base/master
        for p in apk_files:
            n = os.path.basename(p).lower()
            if 'base.apk' in n or 'master.apk' in n:
                return p
        # exclude splits
        candidates = []
        for p in apk_files:
            n = os.path.basename(p).lower()
            if any(s in n for s in ['config.', 'split_', 'dpi_', 'abi_']):
                continue
            candidates.append(p)
        if candidates:
            return max(candidates, key=lambda x: os.path.getsize(x))
        if apk_files:
            return max(apk_files, key=lambda x: os.path.getsize(x))
        return None

    def convert_apks_to_apk(self, apks_path, output_dir=None):
        action = f"convert_apks_to_apk {apks_path}"
        if not os.path.exists(apks_path):
            printc(f"    ❌ Error: {apks_path} not found.", Colors.RED)
            self.save_log(action, "FAIL", "not found")
            return False

        apks_path = os.path.expanduser(apks_path)
        base_name = os.path.splitext(os.path.basename(apks_path))[0]
        if not output_dir:
            output_dir = os.path.dirname(apks_path) or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        out_apk = os.path.join(output_dir, f"{base_name}.apk")

        try:
            apk_files = self.list_apks_inside(apks_path)
            if not apk_files:
                printc("    ❌ No .apk files found in bundle.", Colors.RED)
                self.save_log(action, "FAIL", "no apk in bundle")
                return False

            printc(f"    📦 Found {len(apk_files)} APK(s) inside bundle.", Colors.CYAN)
            main = self.find_main_apk(apk_files)
            if main:
                shutil.copy2(main, out_apk)
                size_mb = os.path.getsize(out_apk) / (1024*1024)
                printc(f"    ✅ Main APK extracted: {out_apk} ({size_mb:.2f} MB)", Colors.GREEN)
                self.save_log(action, "OK", out_apk)
                return True
            else:
                printc("    ❌ Could not determine main APK.", Colors.RED)
                self.save_log(action, "FAIL", "no main apk")
                return False
        except Exception as e:
            printc(f"    ❌ Error: {e}", Colors.RED)
            self.save_log(action, "FAIL", str(e))
            return False

    def process_directory_apks(self, directory):
        action = f"process_directory_apks {directory}"
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            printc(f"    ❌ Directory not found: {directory}", Colors.RED)
            self.save_log(action, "FAIL", "dir missing")
            return
        files = [f for f in os.listdir(directory) if f.lower().endswith('.apks')]
        if not files:
            printc("    ℹ️ No .apks files found.", Colors.YELLOW)
            self.save_log(action, "OK", "none")
            return

        printc(f"    📊 Found {len(files)} .apks files.", Colors.CYAN)
        success = 0
        for i, f in enumerate(files, 1):
            printc(f"\n    🔁 Processing [{i}/{len(files)}] {f}", Colors.BLUE)
            if self.convert_apks_to_apk(os.path.join(directory, f), directory):
                success += 1
        printc(f"\n    📈 SUMMARY: {success}/{len(files)} succeeded.", Colors.GREEN)
        self.save_log(action, "OK", f"{success}/{len(files)}")

    # ---------------------------
    # Decompile with apktool (no timeout)
    # ---------------------------
    def get_apktool_version(self):
        try:
            r = subprocess.run(['apktool', '--version'], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return r.stdout.strip().splitlines()[0]
        except Exception:
            pass
        return "Not installed"

    def decompile_apk(self, apk_path):
        action = f"decompile_apk {apk_path}"
        if self.apktool_version == "Not installed":
            printc("    ❌ apktool not installed. Run 'Install dependencies' first.", Colors.RED)
            self.save_log(action, "FAIL", "apktool missing")
            return False

        apk_path = os.path.expanduser(apk_path)
        if not os.path.exists(apk_path):
            printc(f"    ❌ APK not found: {apk_path}", Colors.RED)
            self.save_log(action, "FAIL", "apk missing")
            return False

        base_dir = os.path.dirname(apk_path)
        name = os.path.splitext(os.path.basename(apk_path))[0]
        out_dir = os.path.join(base_dir, f"{name}_decompiled")

        printc(f"\n    📄 APK: {os.path.basename(apk_path)}", Colors.CYAN)
        printc(f"    📂 Output: {out_dir}", Colors.CYAN)
        printc("    ⏳ Decompilation may take several minutes depending on size (approx. 5 minutes for large apps).", Colors.YELLOW)

        if not self.headless:
            cont = input("    Continue with decompilation? (y/n): ").strip().lower()
            if cont not in ['y', 'yes', 's', 'si']:
                printc("    ⚠️ Decompilation cancelled.", Colors.YELLOW)
                self.save_log(action, "CANCELLED", "user")
                return False

        # overwrite check
        if os.path.exists(out_dir):
            if not self.headless:
                over = input(f"    Output exists ({out_dir}). Overwrite? (y/n): ").strip().lower()
                if over not in ['y', 'yes', 's', 'si']:
                    printc("    ⚠️ Decompilation cancelled.", Colors.YELLOW)
                    self.save_log(action, "CANCELLED", "exists")
                    return False
            shutil.rmtree(out_dir, ignore_errors=True)

        # Run apktool and stream output; show intermittent spinner/progress
        try:
            proc = subprocess.Popen(['apktool', 'd', apk_path, '-o', out_dir, '-f'],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            start = time.time()
            last_print = time.time()
            printed_lines = 0
            while True:
                line = proc.stdout.readline()
                if line == '' and proc.poll() is not None:
                    break
                if line:
                    low = line.strip().lower()
                    # Print important lines
                    if any(k in low for k in ['error', 'exception', 'warning', 'finished', 'success', 'writing', 'install']):
                        printc(f"    {line.strip()}", Colors.YELLOW if 'warning' in low else Colors.GREEN if 'finished' in low or 'success' in low else Colors.RED if 'error' in low or 'exception' in low else Colors.CYAN)
                    printed_lines += 1
                else:
                    # Show spinner occasionally
                    if time.time() - last_print > 2:
                        printc("    ... decompiling (still working) ...", Colors.DIM)
                        last_print = time.time()

            ret = proc.poll()
            elapsed = int(time.time() - start)
            if ret == 0:
                printc(f"    ✅ Decompilation completed in {elapsed}s", Colors.GREEN)
                self.save_log(action, "OK", out_dir)
                self.show_decompile_stats(out_dir)
                return True
            else:
                printc(f"    ❌ Decompilation finished with code {ret}", Colors.RED)
                self.save_log(action, "FAIL", f"exit {ret}")
                return False
        except KeyboardInterrupt:
            try:
                proc.kill()
            except Exception:
                pass
            printc("\n    ❌ Decompilation interrupted by user.", Colors.RED)
            self.save_log(action, "INTERRUPTED", "user")
            return False
        except Exception as e:
            printc(f"    ❌ Unexpected error: {e}", Colors.RED)
            self.save_log(action, "FAIL", str(e))
            return False

    def show_decompile_stats(self, output_dir):
        try:
            if not os.path.exists(output_dir):
                printc("    ⚠️ Output folder missing; cannot compute stats.", Colors.YELLOW)
                return
            file_count = 0
            total_size = 0
            structure = {'smali': 0, 'resources': 0, 'xml': 0, 'other': 0}
            for root, _, files in os.walk(output_dir):
                for f in files:
                    file_count += 1
                    fp = os.path.join(root, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        pass
                    if 'smali' in root:
                        structure['smali'] += 1
                    elif f.endswith('.xml'):
                        structure['xml'] += 1
                    elif 'res' in root:
                        structure['resources'] += 1
                    else:
                        structure['other'] += 1
            size_mb = total_size / (1024*1024) if total_size else 0.0
            printc("\n    📊 DECOMPILATION STATS:", Colors.CYAN)
            printc(f"    📁 Total files: {file_count}", Colors.CYAN)
            printc(f"    📏 Total size: {size_mb:.2f} MB", Colors.CYAN)
            printc(f"    🔤 Smali files: {structure['smali']}", Colors.CYAN)
            printc(f"    🎨 Resources: {structure['resources']}", Colors.CYAN)
            printc(f"    📄 XML files: {structure['xml']}", Colors.CYAN)
            printc(f"    📋 Others: {structure['other']}", Colors.CYAN)
            top_items = os.listdir(output_dir)[:12]
            printc("\n    📂 TOP-LEVEL:", Colors.DIM)
            for t in top_items:
                tp = os.path.join(output_dir, t)
                if os.path.isdir(tp):
                    cnt = sum(len(files) for _, _, files in os.walk(tp))
                    printc(f"       📁 {t}/ ({cnt} files)", Colors.DIM)
                else:
                    printc(f"       📄 {t}", Colors.DIM)
        except Exception as e:
            printc(f"    ⚠️ Could not compute stats: {e}", Colors.YELLOW)

    # ---------------------------
    # Rebuild (apktool b)
    # ---------------------------
    def rebuild_apk(self, decompiled_dir, output_apk=None):
        action = f"rebuild_apk {decompiled_dir}"
        decompiled_dir = os.path.expanduser(decompiled_dir)
        if not os.path.isdir(decompiled_dir):
            printc(f"    ❌ Decompiled directory not found: {decompiled_dir}", Colors.RED)
            self.save_log(action, "FAIL", "dir missing")
            return False
        if not output_apk:
            output_apk = os.path.join(os.path.dirname(decompiled_dir), os.path.basename(decompiled_dir) + "_rebuilt.apk")
        printc(f"    🔧 Rebuilding from: {decompiled_dir}", Colors.CYAN)
        try:
            rc, out = self.run_cmd(['apktool', 'b', decompiled_dir, '-o', output_apk], capture=True)
            if rc == 0:
                printc(f"    ✅ Rebuild succeeded: {output_apk}", Colors.GREEN)
                self.save_log(action, "OK", output_apk)
                return output_apk
            else:
                printc(f"    ❌ Rebuild failed: {out}", Colors.RED)
                self.save_log(action, "FAIL", out)
                return False
        except Exception as e:
            printc(f"    ❌ Error rebuilding: {e}", Colors.RED)
            self.save_log(action, "FAIL", str(e))
            return False

    # ---------------------------
    # Signing
    # ---------------------------
    def sign_apk(self, apk_path, keystore=None, keystore_pass="android"):
        action = f"sign_apk {apk_path}"
        apk_path = os.path.expanduser(apk_path)
        if not os.path.exists(apk_path):
            printc(f"    ❌ APK not found: {apk_path}", Colors.RED)
            self.save_log(action, "FAIL", "apk missing")
            return False

        # Try apksigner
        if shutil.which('apksigner'):
            printc("    🛡️ Signing with apksigner...", Colors.CYAN)
            out_path = apk_path.replace('.apk', '.signed.apk')
            try:
                # run apksigner sign (keystore path needs to exist). we try default path if none.
                ks = keystore or "/data/local/tmp/debug.keystore"
                subprocess.run(['apksigner', 'sign', '--ks', ks, '--ks-pass', f'pass:{keystore_pass}', '--out', out_path, apk_path], check=True)
                printc(f"    ✅ Signed APK: {out_path}", Colors.GREEN)
                self.save_log(action, "OK", out_path)
                return out_path
            except Exception as e:
                printc(f"    ⚠️ apksigner failed: {e}", Colors.YELLOW)

        # Fallback jarsigner
        if shutil.which('jarsigner'):
            printc("    🛡️ Signing with jarsigner (fallback)...", Colors.CYAN)
            try:
                ks_file = keystore or os.path.join(os.getcwd(), "debug.keystore")
                if not os.path.exists(ks_file) and shutil.which('keytool'):
                    printc("    ⚙️ Creating temporary debug keystore (keytool)...", Colors.YELLOW)
                    subprocess.run([
                        'keytool', '-genkeypair', '-alias', 'zero_two_alias',
                        '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
                        '-keystore', ks_file, '-storepass', keystore_pass,
                        '-dname', 'CN=ZeroTwo, OU=Dev, O=ZeroTwo, L=None, S=None, C=None'
                    ], check=True)
                out_path = apk_path.replace('.apk', '.signed.apk')
                shutil.copy2(apk_path, out_path)
                subprocess.run(['jarsigner', '-keystore', ks_file, '-storepass', keystore_pass, out_path, 'zero_two_alias'], check=True)
                printc(f"    ✅ Signed APK (jarsigner): {out_path}", Colors.GREEN)
                self.save_log(action, "OK", out_path)
                return out_path
            except Exception as e:
                printc(f"    ❌ jarsigner failed: {e}", Colors.RED)
                self.save_log(action, "FAIL", str(e))
                return False

        printc("    ❌ No signing tool available (apksigner or jarsigner). Install dependencies.", Colors.RED)
        self.save_log(action, "FAIL", "no-sign-tool")
        return False

    # ---------------------------
    # APK information
    # ---------------------------
    def show_apk_info(self, apk_path):
        action = f"show_apk_info {apk_path}"
        apk_path = os.path.expanduser(apk_path)
        if not os.path.exists(apk_path):
            printc(f"    ❌ APK not found: {apk_path}", Colors.RED)
            self.save_log(action, "FAIL", "apk missing")
            return

        printc(f"\n    🔎 APK INFO: {os.path.basename(apk_path)}", Colors.CYAN)
        # Try aapt
        if shutil.which('aapt') or shutil.which('aapt2'):
            aapt_cmd = 'aapt' if shutil.which('aapt') else 'aapt2'
            try:
                rc, out = self.run_cmd([aapt_cmd, 'dump', 'badging', apk_path], capture=True, timeout=20)
                if rc == 0:
                    # Print package + launchable activity + version lines
                    for line in out.splitlines():
                        if line.startswith('package:') or line.startswith('launchable-activity:') or line.startswith('uses-permission:'):
                            printc(f"    {line.strip()}", Colors.DIM)
                    self.save_log(action, "OK", "aapt info")
                    return
            except Exception as e:
                printc(f"    ⚠️ aapt failed: {e}", Colors.YELLOW)

        # Fallback: use apktool to extract manifest (no src)
        if self.apktool_version != "Not installed":
            temp_dir = tempfile.mkdtemp(prefix="zero_two_info_")
            try:
                subprocess.run(['apktool', 'd', apk_path, '-o', temp_dir, '-f', '--no-src'], capture_output=True, text=True, timeout=60)
                manifest = os.path.join(temp_dir, 'AndroidManifest.xml')
                if os.path.exists(manifest):
                    printc("    📄 AndroidManifest.xml (first 80 lines):", Colors.DIM)
                    with open(manifest, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, ln in enumerate(f):
                            if i >= 80: break
                            printc(f"    {ln.rstrip()}", Colors.DIM)
                    self.save_log(action, "OK", "manifest shown")
                else:
                    printc("    ⚠️ Manifest not found after apktool extraction.", Colors.YELLOW)
                    self.save_log(action, "FAIL", "manifest missing")
            except Exception as e:
                printc(f"    ❌ Error extracting manifest: {e}", Colors.RED)
                self.save_log(action, "FAIL", str(e))
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            printc("    ⚠️ Cannot show APK info: aapt and apktool not available.", Colors.YELLOW)
            self.save_log(action, "FAIL", "no tools")

    # ---------------------------
    # Auto mode
    # ---------------------------
    def auto_mode(self, directory):
        action = f"auto_mode {directory}"
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            printc(f"    ❌ Directory not found: {directory}", Colors.RED)
            self.save_log(action, "FAIL", "dir missing")
            return

        items = os.listdir(directory)
        apks = [f for f in items if f.lower().endswith('.apks')]
        apk_files = [f for f in items if f.lower().endswith('.apk')]

        printc(f"    🔎 Scanning {directory} -> {len(apks)} .apks, {len(apk_files)} .apk", Colors.CYAN)
        self.save_log(action, "OK", f"{len(apks)} .apks, {len(apk_files)} .apk")

        for a in apks:
            self.convert_apks_to_apk(os.path.join(directory, a), directory)

        if apk_files and not self.headless:
            cont = input("\n    Decompile all found .apk files? (y/n): ").strip().lower()
            if cont in ['y', 'yes', 's', 'si']:
                for a in apk_files:
                    self.decompile_apk(os.path.join(directory, a))

        printc("    ✅ Auto mode finished.", Colors.GREEN)
        self.save_log(action, "OK", "finished")

    # ---------------------------
    # Dependencies / Install
    # ---------------------------
    def install_dependencies(self):
        action = "install_dependencies"
        printc("    ⚙️  Installing dependencies (Termux-friendly)...", Colors.CYAN)
        if not self.termux:
            printc("    ⚠️ Automatic install is optimized for Termux. Please install apktool, openjdk, zipalign, apksigner manually if needed.", Colors.YELLOW)
            self.save_log(action, "WARN", "not termux")
            return
        try:
            # Attempt to install common packages via pkg
            subprocess.run(['pkg', 'update', '-y'], check=False)
            subprocess.run(['pkg', 'install', '-y', 'apktool', 'openjdk-17', 'zipalign', 'apksigner', 'curl'], check=False)
            # refresh cached statuses
            self.apktool_version = self.get_apktool_version()
            self.apksigner_available = bool(shutil.which('apksigner'))
            printc("    ✅ Dependency installation attempted. Verify tools are installed.", Colors.GREEN)
            self.save_log(action, "OK", "attempted")
        except Exception as e:
            printc(f"    ❌ Error during install attempt: {e}", Colors.RED)
            self.save_log(action, "FAIL", str(e))

    # ---------------------------
    # Update handling (check and optional download)
    # ---------------------------
    def check_for_updates(self, interactive=True):
        """
        Checks GitHub releases (github_api_release) and if newer version exists,
        prompts to download and replace the current script.
        """
        action = "check_for_updates"
        printc("    🔎 Checking for updates...", Colors.CYAN)
        # Try to use requests if available; otherwise try curl
        json_text = None
        try:
            import requests
            try:
                r = requests.get(self.github_api_release, timeout=15)
                if r.status_code == 200:
                    json_text = r.json()
            except Exception as e:
                printc(f"    ⚠️ Network error using requests: {e}", Colors.YELLOW)
        except Exception:
            # fallback to curl if available
            if shutil.which('curl'):
                try:
                    rc, out = self.run_cmd(['curl', '-sL', self.github_api_release], capture=True, timeout=15)
                    if rc == 0 and out:
                        import json
                        json_text = json.loads(out)
                except Exception as e:
                    printc(f"    ⚠️ curl fallback failed: {e}", Colors.YELLOW)
            else:
                printc("    ⚠️ Neither 'requests' nor 'curl' available to check updates. Install 'requests' or 'curl'.", Colors.YELLOW)
                self.save_log(action, "FAIL", "no-network-tool")
                return

        if not json_text:
            printc("    ⚠️ Could not fetch release info from GitHub.", Colors.YELLOW)
            self.save_log(action, "FAIL", "no release info")
            return

        # parse release
        latest_tag = json_text.get('tag_name') or json_text.get('name') or json_text.get('id')
        latest_name = json_text.get('name') or latest_tag
        assets = json_text.get('assets') or []
        latest_url_html = json_text.get('html_url') or f"https://github.com/CHICO-CP/zero-two-toolkit/releases/latest"
        # Compare versions naively (string compare); we can parse semver if needed
        if latest_tag and latest_tag.strip() != self.version:
            printc(f"    🚀 New version available: {latest_tag}", Colors.MAGENTA)
            printc(f"    🔗 Release page: {latest_url_html}", Colors.CYAN)
            self.save_log(action, "OK", f"latest {latest_tag}")
            if interactive and not self.headless:
                ans = input("    Would you like to update Zero Two now? (y/n): ").strip().lower()
            else:
                ans = 'n'
            if ans in ['y', 'yes', 's', 'si']:
                # Determine asset to download: prefer a direct python script or zip asset
                download_url = None
                if assets:
                    # prefer asset with .py or .zip
                    for a in assets:
                        name = a.get('name', '')
                        if name.endswith('.py') or name.endswith('.zip') or name.endswith('.tar.gz'):
                            download_url = a.get('browser_download_url')
                            break
                    if not download_url:
                        download_url = assets[0].get('browser_download_url')
                else:
                    # fallback: attempt to download the "latest" release tarball
                    download_url = json_text.get('tarball_url') or json_text.get('zipball_url')

                if not download_url:
                    printc("    ❌ No downloadable asset found in release. Please update manually.", Colors.RED)
                    return

                printc(f"    ⏬ Downloading: {download_url}", Colors.CYAN)
                tmp_file = os.path.join(tempfile.gettempdir(), f"zero_two_update_{int(time.time())}")
                try:
                    # try requests download if available
                    try:
                        import requests
                        with requests.get(download_url, stream=True, timeout=60) as r:
                            r.raise_for_status()
                            total = int(r.headers.get('content-length', 0))
                            with open(tmp_file, 'wb') as f:
                                downloaded = 0
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        # progress
                                        self.print_progress(downloaded, total, prefix="    Downloading")
                    except Exception:
                        # fallback to curl
                        if shutil.which('curl'):
                            rc, out = self.run_cmd(['curl', '-L', '-o', tmp_file, download_url], capture=True, timeout=300)
                            if rc != 0:
                                raise RuntimeError(f"curl failed: {out}")
                        else:
                            raise RuntimeError("No download method available (requests and curl both missing).")

                    # Now determine how to replace current script:
                    cur_path = os.path.abspath(sys.argv[0])
                    backup_path = cur_path + ".bak"
                    try:
                        # Make a backup
                        shutil.copy2(cur_path, backup_path)
                    except Exception:
                        pass

                    # If asset is a single .py, just replace; if zip/tar, we can't auto-extract reliably -> ask user
                    if download_url.endswith('.py'):
                        shutil.copy2(tmp_file, cur_path)
                        printc(f"\n    🎉 Zero Two has been successfully updated to {latest_tag}!", Colors.GREEN)
                        printc("    Please restart the tool manually to apply the changes.", Colors.YELLOW)
                        self.save_log(action, "OK", f"updated {latest_tag}")
                    else:
                        # If it's an archive, suggest manual steps
                        printc("\n    ⚠️ Downloaded package is an archive. Automatic replacement not performed.", Colors.YELLOW)
                        printc(f"    Please extract the archive from: {tmp_file} and replace the script manually.", Colors.YELLOW)
                        self.save_log(action, "OK", f"downloaded archive {tmp_file}")
                except Exception as e:
                    printc(f"    ❌ Update failed: {e}", Colors.RED)
                    self.save_log(action, "FAIL", str(e))
                finally:
                    try:
                        if os.path.exists(tmp_file) and not download_url.endswith('.py'):
                            # keep archive for manual install
                            pass
                        elif os.path.exists(tmp_file):
                            os.remove(tmp_file)
                    except Exception:
                        pass
            else:
                printc("    ⚠️ Update cancelled by user.", Colors.YELLOW)
        else:
            printc("    ✅ Zero Two is already up to date.", Colors.GREEN)
            self.save_log(action, "OK", f"version {self.version}")

    def print_progress(self, current, total, prefix=""):
        # Simple progress bar print
        try:
            width = 36
            if total <= 0:
                pct = 0
            else:
                pct = current / total
            filled = int(width * pct)
            bar = "█" * filled + "-" * (width - filled)
            print(f"\r{prefix} |{bar}| {pct*100:6.2f}% ", end="", flush=True)
            if current >= total:
                print()
        except Exception:
            pass

    # ---------------------------
    # System info & credits
    # ---------------------------
    def show_system_info_and_credits(self):
        self.clear()
        printc("SYSTEM INFORMATION", Colors.CYAN, bold=True)
        info = {
            "Platform": "Termux Android" if self.termux else platform.system(),
            "System": platform.system(),
            "OS Release": platform.release(),
            "Architecture": platform.architecture()[0],
            "Python": platform.python_version(),
            "APKTool": self.apktool_version,
            "Working Dir": os.getcwd(),
            "/sdcard accessible": "Yes" if os.path.exists("/sdcard") else "No"
        }
        for k, v in info.items():
            printc(f"    {k}: {v}", Colors.DIM)
        print()
        printc("CREDITS", Colors.CYAN, bold=True)
        printc(f"    Developer: {self.developer}", Colors.DIM)
        printc(f"    GitHub: {self.github}", Colors.DIM)
        printc(f"    Telegram: {self.telegram}", Colors.DIM)
        printc(f"    Version: {self.version}", Colors.DIM)
        if not self.headless:
            input("\n    Press Enter to continue...")

    # ---------------------------
    # CLI / Main loop
    # ---------------------------
    def handle_args_update(self):
        # Called by CLI subcommand --update
        self.check_for_updates(interactive=not self.headless)

    def run_interactive(self):
        while True:
            try:
                self.clear()
                self.show_banner()
                self.show_menu()
                choice = input("    Select an option (1-11): ").strip()
                if choice == '1':
                    apks = input("    Path to .apks file: ").strip()
                    out = input("    Output directory (blank = same folder): ").strip() or None
                    if apks:
                        self.convert_apks_to_apk(apks, out)
                elif choice == '2':
                    d = input("    Directory to scan for .apks: ").strip()
                    if d:
                        self.process_directory_apks(d)
                elif choice == '3':
                    apk = input("    Path to .apk to decompile: ").strip()
                    if apk:
                        self.decompile_apk(apk)
                elif choice == '4':
                    dd = input("    Decompiled directory to rebuild: ").strip()
                    if dd:
                        self.rebuild_apk(dd)
                elif choice == '5':
                    apk = input("    Path to .apk to sign: ").strip()
                    if apk:
                        self.sign_apk(apk)
                elif choice == '6':
                    apk = input("    Path to .apk to inspect: ").strip()
                    if apk:
                        self.show_apk_info(apk)
                elif choice == '7':
                    self.check_for_updates(interactive=True)
                elif choice == '8':
                    d = input("    Directory to auto-scan: ").strip()
                    if d:
                        self.auto_mode(d)
                elif choice == '9':
                    self.install_dependencies()
                elif choice == '10':
                    self.show_system_info_and_credits()
                elif choice == '11':
                    printc(f"\n    👋 Thanks for using {self.name} — Goodbye!\n", Colors.CYAN)
                    break
                else:
                    printc("    ❌ Invalid option. Please select 1-11.", Colors.RED)
                if not self.headless:
                    input("\n    Press Enter to continue...")
            except KeyboardInterrupt:
                printc("\n\n    👋 Exiting. Bye!", Colors.CYAN)
                break
            except Exception as e:
                printc(f"\n    ❌ Unexpected error: {e}", Colors.RED)
                self.save_log("main_loop", "FAIL", str(e))
                if not self.headless:
                    input("\n    Press Enter to continue...")

# ---------------------------
# Entry point and argument parsing
# ---------------------------
def main():
    parser = argparse.ArgumentParser(prog="zero_two.py", description="ZERO TWO — APKs Toolkit for Termux")
    parser.add_argument('--update', action='store_true', help='Check for updates and optionally update the tool')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no interactive prompts)')
    parser.add_argument('--convert', metavar='FILE', help='Convert a .apks bundle to .apk (single file)')
    parser.add_argument('--decompile', metavar='APK', help='Decompile a single APK file')
    parser.add_argument('--rebuild', metavar='DIR', help='Rebuild an APK from a decompiled directory')
    parser.add_argument('--sign', metavar='APK', help='Sign an APK using available tools')
    parser.add_argument('--info', metavar='APK', help='Show APK info (aapt/apktool)')
    args = parser.parse_args()

    app = ZeroTwo(headless=args.headless)

    # If a direct subcommand is used, run it and exit
    if args.update:
        app.handle_args_update()
        return
    if args.convert:
        outdir = None
        # convert and exit
        app.convert_apks_to_apk(args.convert, outdir)
        return
    if args.decompile:
        app.decompile_apk(args.decompile)
        return
    if args.rebuild:
        app.rebuild_apk(args.rebuild)
        return
    if args.sign:
        app.sign_apk(args.sign)
        return
    if args.info:
        app.show_apk_info(args.info)
        return

    # Otherwise launch interactive menu
    app.run_interactive()

if __name__ == '__main__':
    main()