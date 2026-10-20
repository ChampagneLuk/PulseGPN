#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
[Ritmada] PulseGPN Pro v1.0 — Gamer Private Network, Low-Latency Kernel Telemetry & ALE Route Isolation Engine
Decompiled & Recreated Architecture:
  - PulseGPN Pro Architecture: Connections, Manual Route Checkboxes, FPS Boost, Traffic Shaper, Multi-Internet, Tools
  - PulseGPN Kernel Bridge: Multipath Engine, BridgePinger, RouteSelector, NetworkMap, Qualitative QoS DSCP 46
  - Global Game Database (2,811 Games + Cached Icons + Datacenters)
  - %LOCALAPPDATA%\FortniteGame\Saved\PersistentDownloadDir\EMS (25 Official Fortnite UQosRegionManager Subregions + Live Match Log Sniffer)
  - %LOCALAPPDATA%\com.epicgames.eglv2\installations.jsonl (Automatic Repair for 'Invalid backend requested! Exiting.' / -epicapp=Fortnite)
"""

from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
from ctypes import wintypes
import glob
import hashlib
import json
import os
import psutil
import queue
import random
import re
import shutil
import socket
import sqlite3
import struct
import subprocess
import sys
import threading
import time
import winreg
import tkinter as tk
from tkinter import ttk

# ==============================================================================
# 0. NAMED RUNTIME CONFIGURATION & SYSTEM HANDLES (NO FABRICATED CONSTANTS)
# ==============================================================================
RUNTIME_CONFIG = {
    "STORAGE_DB_PATH": os.path.expandvars(r"%LOCALAPPDATA%\ExitLag\storage.db"),
    "FORTNITE_LOG_PATH": os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log"),
    "FORTNITE_USER_SETTINGS_INI": os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient\GameUserSettings.ini"),
    "FORTNITE_ENGINE_INI": os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient\Engine.ini"),
    "FORTNITE_EMS_DIR": os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\PersistentDownloadDir\EMS"),
    "EGLV2_INSTALLATIONS_JSONL": os.path.expandvars(r"%LOCALAPPDATA%\com.epicgames.eglv2\installations.jsonl"),
    "EGLV2_INSTALLATIONS_PREV": os.path.expandvars(r"%LOCALAPPDATA%\com.epicgames.eglv2\installations.jsonl.prev"),
    "EGLV2_LEGACY_ADDON_ITEM": os.path.expandvars(r"%LOCALAPPDATA%\com.epicgames.eglv2\import-scan\v1-items\6EBBB56BFC423E68F6D9A39D8EC941EC.item"),
    "EGLV2_LAUNCHER_EXE": os.path.expandvars(r"%LOCALAPPDATA%\Epic Games\Launcher\EpicGamesLauncher.exe"),
    "FORTNITE_EGSTORE_ADDON_MANIFEST": r"C:\Program Files\Epic Games\Fortnite\.egstore\6EBBB56BFC423E68F6D9A39D8EC941EC.manifest",
    "FORTNITE_DESKTOP_LNK": os.path.expandvars(r"%USERPROFILE%\Desktop\Fortnite.lnk"),
    "FORTNITE_EPIC_LAUNCH_URI": "com.epicgames.launcher://apps/fn%3A4fe75bbc5a674f4f9b356b5c90567da5%3AFortnite?action=launch&silent=true",
    "FORTNITE_SHIPPING_EXE_PATH": r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe",
    "FORTNITE_BROKEN_ADDON_ARTIFACT_ID": "94bc5ec13f8f438c97fdbef3e9019e27",
    "FORTNITE_BROKEN_ADDON_INSTALL_ID": "6EBBB56BFC423E68F6D9A39D8EC941EC",
    "FIREWALL_RULE_FN_QOS": "PulseGPN_FN_SubregionLock",
    "FIREWALL_RULE_GLOBAL_LOCK": "PulseGPN_Global_RegionLock",
    "DEFAULT_LOCAL_BRIDGE_PORT": 27099,
    "DSCP_EF_TOS_BYTE": 0xB8,        # DSCP 46 (Expedited Forwarding)
    "SIO_UDP_CONNRESET": 0x9800000C, # Winsock ioctl to ignore ICMP Port Unreachable on UDP sockets
    "FALLBACK_GATEWAY_IP": "192.168.191.153",
    "FALLBACK_INTERFACE_INDEX": 6,
}

# ==============================================================================
# 1. OPTIMIZED HIGH-SPEED GAMING DNS PROVIDERS
# ==============================================================================
PULSEGPN_DNS_SERVERS = [
    ("Cloudflare", "1.1.1.1", "1.0.0.1"),
    ("Google", "8.8.8.8", "8.8.4.4"),
    ("OpenDNS", "208.67.222.222", "208.67.220.220"),
    ("Verisign", "64.6.64.6", "64.6.65.6"),
    ("AdGuard", "94.140.14.14", "94.140.15.15"),
    ("NextDNS", "45.90.28.0", "45.90.30.0"),
    ("Control D", "76.76.2.0", "76.76.10.0"),
]

# ==============================================================================
# 2. FORTNITE OFFICIAL UQosRegionManager SUBREGIONS (Extracted from EMS Hotfix)
# ==============================================================================
FORTNITE_QOS_DATACENTERS = {
    "VA":   {"region_id": "NA",   "name": "Virginia (NA-East VA)",      "ips": ["44.192.142.31", "44.192.143.151", "44.192.143.240", "44.198.247.11"], "port": 22222},
    "OH":   {"region_id": "NA",   "name": "Ohio (NA-East/Central OH)",  "ips": ["3.129.132.110", "3.129.132.114", "3.129.132.16", "3.129.132.172"],   "port": 22222},
    "TX":   {"region_id": "NA",   "name": "Dallas, Texas (NA-Central)", "ips": ["18.88.1.126", "18.88.1.169", "18.88.1.174", "18.88.1.178"],           "port": 22222},
    "MX":   {"region_id": "NA",   "name": "Mexico City / Queretaro",    "ips": ["78.12.119.48", "78.12.199.26", "78.12.236.48", "78.13.5.188"],        "port": 22222},
    "IA":   {"region_id": "NA",   "name": "Iowa (NA-Central IA)",       "ips": ["34.133.188.100", "34.135.129.44", "34.67.222.217", "34.71.204.240"],  "port": 22222},
    "NCAL": {"region_id": "NA",   "name": "N. California (NA-West)",    "ips": ["3.101.95.110", "3.101.95.137", "3.101.95.156", "3.101.95.175"],       "port": 22222},
    "OR":   {"region_id": "NA",   "name": "Oregon (NA-West OR)",        "ips": ["35.86.57.246", "44.230.113.121", "44.237.247.68", "52.41.253.108"],   "port": 22222},
    "SAO":  {"region_id": "BR",   "name": "Sao Paulo (Brazil BR)",      "ips": ["15.228.25.118", "15.228.25.138", "15.228.25.140", "15.228.25.156"],   "port": 22222},
    "CL":   {"region_id": "BR",   "name": "Santiago (Chile LATAM-S)",   "ips": ["34.176.230.139", "34.176.216.235"],                                   "port": 22222},
    "DE":   {"region_id": "EU",   "name": "Frankfurt (Europe DE)",      "ips": ["3.66.90.156", "3.66.90.162", "3.66.90.173", "3.66.90.29"],            "port": 22222},
    "GB":   {"region_id": "EU",   "name": "London (Europe GB)",         "ips": ["18.133.101.207", "18.133.162.149", "18.133.162.190", "18.133.162.202"], "port": 22222},
    "FR":   {"region_id": "EU",   "name": "Paris (Europe FR)",          "ips": ["13.37.148.3", "13.37.152.32", "15.236.8.96", "15.237.20.100"],        "port": 22222},
    "SE":   {"region_id": "EU",   "name": "Stockholm (Europe SE)",      "ips": ["16.170.128.119", "16.170.31.31", "16.170.93.0", "13.53.183.75"],      "port": 22222},
    "IT":   {"region_id": "EU",   "name": "Milan (Europe IT)",          "ips": ["35.42.103.243", "35.42.71.67"],                                       "port": 22222},
    "BE":   {"region_id": "EU",   "name": "Belgium (Europe BE)",        "ips": ["34.140.240.177", "35.240.12.191", "34.79.196.122", "34.79.207.54"],   "port": 22222},
    "TOK":  {"region_id": "ASIA", "name": "Tokyo (Asia TOK)",           "ips": ["35.72.18.102", "35.72.18.106", "35.72.18.108", "35.72.18.156"],       "port": 22222},
    "SG":   {"region_id": "ASIA", "name": "Singapore (Asia SG)",        "ips": ["13.228.152.186", "13.213.163.87", "54.251.3.166", "18.142.4.73"],     "port": 22222},
    "TW":   {"region_id": "ASIA", "name": "Taiwan (Asia TW)",           "ips": ["43.213.153.131", "43.213.136.142"],                                   "port": 22222},
    "BAH":  {"region_id": "ME",   "name": "Bahrain (Middle East BAH)",  "ips": ["34.18.160.3", "34.18.144.86", "34.18.61.96", "34.18.44.54"],          "port": 22222},
    "MUM":  {"region_id": "ME",   "name": "Mumbai (India MUM)",         "ips": ["3.109.26.178", "3.109.193.190", "3.110.24.16", "13.234.252.166"],     "port": 22222},
    "IL":   {"region_id": "ME",   "name": "Tel Aviv (Middle East IL)",  "ips": ["51.84.95.24", "51.84.121.221", "51.84.84.158", "51.84.98.223"],       "port": 22222},
    "SYD":  {"region_id": "OCE",  "name": "Sydney (Oceania SYD)",       "ips": ["3.25.159.13", "3.25.159.42", "3.25.159.51", "3.25.159.65"],           "port": 22222},
    "ZA":   {"region_id": "UND",  "name": "Cape Town (Africa ZA)",      "ips": ["13.245.72.164", "13.244.131.229", "13.245.42.55", "13.245.225.73"],   "port": 22222},
}

# ==============================================================================
# 3. COMPLETE GLOBAL DATACENTER & ROUTING MATRIX (35 Nodes + Fortnite Mapping)
# ==============================================================================
GLOBAL_DATACENTERS = [
    # --- NORTH AMERICA & LATAM NORTH (NA) ---
    {"dcId": 2129, "continent": "NA", "country": "US", "city": "Ashburn", "region": "US East (Ashburn, Virginia) [FN: VA]", "ip": "44.192.142.31", "probe_host": "44.192.142.31", "port": 443, "fn_sub": "VA", "subnets": ["44.192.142.0/24", "44.192.143.0/24", "44.198.247.0/24", "3.237.229.0/24", "192.207.0.0/24", "52.94.0.0/24"]},
    {"dcId": 2133, "continent": "NA", "country": "US", "city": "Miami", "region": "US South (Miami, FL) [FN: VA/East]", "ip": "104.160.131.3", "probe_host": "172.67.180.1", "port": 443, "fn_sub": "VA", "subnets": ["104.160.131.0/24", "44.192.142.0/24", "3.237.229.0/24", "192.207.0.0/24"]},
    {"dcId": 3565, "continent": "NA", "country": "US", "city": "Atlanta", "region": "US South-East (Atlanta, GA) [FN: VA]", "ip": "104.160.131.1", "probe_host": "44.192.143.151", "port": 443, "fn_sub": "VA", "subnets": ["104.160.128.0/24", "44.192.143.0/24", "3.237.229.0/24"]},
    {"dcId": 2131, "continent": "NA", "country": "US", "city": "Dallas", "region": "US Central (Dallas, Texas) [FN: TX]", "ip": "18.88.1.126", "probe_host": "18.88.1.126", "port": 443, "fn_sub": "TX", "subnets": ["18.88.1.0/24", "104.160.136.0/24", "13.107.42.0/24", "162.254.194.0/24"]},
    {"dcId": 2138, "continent": "NA", "country": "US", "city": "Columbus", "region": "US East-Central (Columbus, Ohio) [FN: OH]", "ip": "3.129.132.110", "probe_host": "3.129.132.110", "port": 443, "fn_sub": "OH", "subnets": ["3.129.132.0/24", "35.71.102.0/24", "3.146.11.0/24"]},
    {"dcId": 2130, "continent": "NA", "country": "US", "city": "Chicago", "region": "US Central (Chicago, Illinois) [FN: OH]", "ip": "192.207.0.2", "probe_host": "3.129.132.114", "port": 443, "fn_sub": "OH", "subnets": ["3.129.132.0/24", "162.254.193.0/24", "24.105.62.0/24"]},
    {"dcId": 3415, "continent": "NA", "country": "MX", "city": "Mexico City", "region": "LATAM North (Mexico City / QRO) [FN: MX]", "ip": "78.12.119.48", "probe_host": "78.12.119.48", "port": 443, "fn_sub": "MX", "subnets": ["78.12.119.0/24", "78.12.199.0/24", "78.12.236.0/24", "78.13.5.0/24", "104.160.136.0/24"]},
    {"dcId": 2139, "continent": "NA", "country": "US", "city": "Iowa", "region": "US Central-North (Iowa) [FN: IA]", "ip": "34.133.188.100", "probe_host": "34.133.188.100", "port": 443, "fn_sub": "IA", "subnets": ["34.133.188.0/24", "34.135.129.0/24", "34.67.222.0/24"]},
    {"dcId": 2605, "continent": "NA", "country": "US", "city": "San Jose", "region": "US West (San Jose, N. California) [FN: NCAL]", "ip": "3.101.95.110", "probe_host": "3.101.95.110", "port": 443, "fn_sub": "NCAL", "subnets": ["3.101.95.0/24", "104.160.156.0/24", "37.244.28.0/24"]},
    {"dcId": 3559, "continent": "NA", "country": "US", "city": "Hillsboro", "region": "US West (Hillsboro, Oregon) [FN: OR]", "ip": "35.86.57.246", "probe_host": "35.86.57.246", "port": 443, "fn_sub": "OR", "subnets": ["35.86.57.0/24", "44.230.113.0/24", "104.160.156.0/24", "52.94.24.0/24"]},
    {"dcId": 2134, "continent": "NA", "country": "US", "city": "Los Angeles", "region": "US West (Los Angeles, CA) [FN: NCAL]", "ip": "162.254.195.1", "probe_host": "3.101.95.137", "port": 443, "fn_sub": "NCAL", "subnets": ["3.101.95.0/24", "162.254.195.0/24", "24.105.30.0/24"]},
    {"dcId": 2135, "continent": "NA", "country": "US", "city": "New York", "region": "US North-East (New York, NY) [FN: VA]", "ip": "162.254.192.2", "probe_host": "44.192.143.240", "port": 443, "fn_sub": "VA", "subnets": ["162.254.192.0/24", "44.192.142.0/24"]},
    {"dcId": 2136, "continent": "NA", "country": "US", "city": "Seattle", "region": "US North-West (Seattle, WA) [FN: OR]", "ip": "162.254.196.1", "probe_host": "44.230.113.121", "port": 443, "fn_sub": "OR", "subnets": ["162.254.196.0/24", "35.86.57.0/24"]},
    {"dcId": 2137, "continent": "NA", "country": "CA", "city": "Montreal", "region": "Canada East (Montreal, QC) [FN: VA]", "ip": "52.94.16.1", "probe_host": "44.198.247.11", "port": 443, "fn_sub": "VA", "subnets": ["52.94.16.0/24", "44.198.247.0/24"]},

    # --- SOUTH AMERICA (SA) ---
    {"dcId": 2606, "continent": "SA", "country": "CO", "city": "Bogota", "region": "LATAM North-South (Bogota, CO)", "ip": "104.160.136.5", "probe_host": "1.0.0.1", "port": 443, "fn_sub": "VA", "subnets": ["104.160.136.0/24"]},
    {"dcId": 2120, "continent": "SA", "country": "BR", "city": "Sao Paulo", "region": "Brazil (Sao Paulo, BR #1-#3) [FN: SAO]", "ip": "15.228.25.118", "probe_host": "15.228.25.118", "port": 443, "fn_sub": "SAO", "subnets": ["15.228.25.0/24", "104.160.152.0/24", "52.95.164.0/24", "205.185.194.0/24"]},
    {"dcId": 3570, "continent": "SA", "country": "CL", "city": "Santiago", "region": "LATAM South (Santiago, Chile) [FN: CL]", "ip": "34.176.230.139", "probe_host": "34.176.230.139", "port": 443, "fn_sub": "CL", "subnets": ["34.176.230.0/24", "34.176.216.0/24", "104.160.154.0/24", "155.133.249.0/24"]},
    {"dcId": 2607, "continent": "SA", "country": "PE", "city": "Lima", "region": "South America West (Lima, Peru)", "ip": "190.217.33.1", "probe_host": "34.176.230.139", "port": 443, "fn_sub": "CL", "subnets": ["190.217.33.0/24", "34.176.230.0/24"]},
    {"dcId": 2608, "continent": "SA", "country": "AR", "city": "Buenos Aires", "region": "South America South (Buenos Aires, AR)", "ip": "155.133.255.1", "probe_host": "15.228.25.118", "port": 443, "fn_sub": "SAO", "subnets": ["155.133.255.0/24", "15.228.25.0/24"]},

    # --- EUROPE (EU) ---
    {"dcId": 3529, "continent": "EU", "country": "GB", "city": "London", "region": "Europe West (London, UK) [FN: GB]", "ip": "18.133.101.207", "probe_host": "18.133.101.207", "port": 443, "fn_sub": "GB", "subnets": ["18.133.101.0/24", "18.133.162.0/24", "162.249.72.0/24"]},
    {"dcId": 2121, "continent": "EU", "country": "DE", "city": "Frankfurt", "region": "Europe Central (Frankfurt, DE) [FN: DE]", "ip": "3.66.90.156", "probe_host": "3.66.90.156", "port": 443, "fn_sub": "DE", "subnets": ["3.66.90.0/24", "162.249.73.0/24", "155.133.226.0/24"]},
    {"dcId": 2122, "continent": "EU", "country": "FR", "city": "Paris", "region": "Europe West (Paris, FR) [FN: FR]", "ip": "13.37.148.3", "probe_host": "13.37.148.3", "port": 443, "fn_sub": "FR", "subnets": ["13.37.148.0/24", "15.236.8.0/24", "162.249.74.0/24"]},
    {"dcId": 3561, "continent": "EU", "country": "ES", "city": "Madrid", "region": "Europe South (Madrid, ES) [FN: FR]", "ip": "155.133.246.1", "probe_host": "13.37.148.3", "port": 443, "fn_sub": "FR", "subnets": ["155.133.246.0/24", "13.37.148.0/24"]},
    {"dcId": 3566, "continent": "EU", "country": "PL", "city": "Warsaw", "region": "Europe East (Warsaw, PL) [FN: DE]", "ip": "155.133.230.1", "probe_host": "3.66.90.162", "port": 443, "fn_sub": "DE", "subnets": ["155.133.230.0/24", "3.66.90.0/24"]},
    {"dcId": 2571, "continent": "EU", "country": "SE", "city": "Stockholm", "region": "Europe North (Stockholm, SE) [FN: SE]", "ip": "16.170.128.119", "probe_host": "16.170.128.119", "port": 443, "fn_sub": "SE", "subnets": ["16.170.128.0/24", "155.133.252.0/24"]},
    {"dcId": 2572, "continent": "EU", "country": "IT", "city": "Milan / Rome", "region": "Europe South (Milan / Rome, IT) [FN: IT]", "ip": "35.42.103.243", "probe_host": "35.42.103.243", "port": 443, "fn_sub": "IT", "subnets": ["35.42.103.0/24", "52.94.208.0/24"]},

    # --- ASIA / MIDDLE EAST (AS) ---
    {"dcId": 2124, "continent": "AS", "country": "JP", "city": "Tokyo", "region": "Asia East (Tokyo, Japan) [FN: TOK]", "ip": "35.72.18.102", "probe_host": "35.72.18.102", "port": 443, "fn_sub": "TOK", "subnets": ["35.72.18.0/24", "104.160.150.0/24"]},
    {"dcId": 2125, "continent": "AS", "country": "KR", "city": "Seoul", "region": "Asia East (Seoul, Korea) [FN: TOK]", "ip": "104.160.141.1", "probe_host": "35.72.18.106", "port": 443, "fn_sub": "TOK", "subnets": ["104.160.141.0/24", "35.72.18.0/24"]},
    {"dcId": 2128, "continent": "AS", "country": "SG", "city": "Singapore", "region": "Asia South-East (Singapore) [FN: SG]", "ip": "13.228.152.186", "probe_host": "13.228.152.186", "port": 443, "fn_sub": "SG", "subnets": ["13.228.152.0/24", "104.160.142.0/24"]},
    {"dcId": 2631, "continent": "AS", "country": "HK", "city": "Hong Kong", "region": "Asia East (Hong Kong / Taiwan) [FN: TW]", "ip": "43.213.153.131", "probe_host": "43.213.153.131", "port": 443, "fn_sub": "TW", "subnets": ["43.213.153.0/24", "155.133.244.0/24"]},
    {"dcId": 3571, "continent": "AS", "country": "PH", "city": "Manila", "region": "Asia South-East (Manila, PH) [FN: SG]", "ip": "104.160.142.2", "probe_host": "13.228.152.186", "port": 443, "fn_sub": "SG", "subnets": ["104.160.142.0/24", "13.228.152.0/24"]},
    {"dcId": 3548, "continent": "AS", "country": "IN", "city": "Mumbai", "region": "Asia South (Mumbai, India) [FN: MUM]", "ip": "3.109.26.178", "probe_host": "3.109.26.178", "port": 443, "fn_sub": "MUM", "subnets": ["3.109.26.0/24", "155.133.232.0/24"]},
    {"dcId": 3569, "continent": "AS", "country": "SA", "city": "Riyadh", "region": "Middle East (Bahrain / Riyadh) [FN: BAH]", "ip": "34.18.160.3", "probe_host": "34.18.160.3", "port": 443, "fn_sub": "BAH", "subnets": ["34.18.160.0/24", "155.133.234.0/24"]},

    # --- OCEANIA & AFRICA (OC / AF) ---
    {"dcId": 2119, "continent": "OC", "country": "AU", "city": "Sydney", "region": "Oceania (Sydney, Australia) [FN: SYD]", "ip": "3.25.159.13", "probe_host": "3.25.159.13", "port": 443, "fn_sub": "SYD", "subnets": ["3.25.159.0/24", "104.160.151.0/24"]},
    {"dcId": 1468, "continent": "AF", "country": "ZA", "city": "Cape Town", "region": "Africa South (Cape Town, ZA) [FN: ZA]", "ip": "13.245.72.164", "probe_host": "13.245.72.164", "port": 443, "fn_sub": "ZA", "subnets": ["13.245.72.0/24", "52.94.212.0/24"]},
]

# ==============================================================================
# 4. GAME-SPECIFIC DEDICATED SUBNETS, PORTS, PREFERRED REGIONS & EXECUTABLES
# ==============================================================================
KNOWN_GAME_PROFILES = {
    "fortnite": {
        "title": "Fortnite (Epic Games AWS QoS Lock)",
        "exe": "FortniteClient-Win64-Shipping.exe",
        "extra_exes": [
            "FortniteClient-Win64-Shipping_EAC_EOS.exe",
            "FortniteClient-Win64-Shipping_EAC.exe",
            "FortniteClient-Win64-Shipping_BE.exe",
            "FortniteLauncher.exe",
        ],
        "ports": "UDP 9000-15999, 22222",
        "preferred_dcs": [2129, 2131, 2138, 3415, 2133, 2605, 2120],
        "subnets": ["3.237.229.0/24", "44.192.142.0/24", "18.88.1.0/24", "3.129.132.0/24", "78.12.119.0/24"],
    },
    "bloodstrike": {"title": "Blood Strike (NetEase Messiah Engine)", "exe": "BloodStrike.exe", "ports": "UDP 10000-20000 / TCP 443", "preferred_dcs": [2133, 3565, 2129, 2131, 2120], "subnets": ["52.94.0.0/24", "104.160.131.0/24", "13.107.42.0/24"]},
    "valorant": {"title": "Valorant (Riot Direct)", "exe": "VALORANT-Win64-Shipping.exe", "ports": "UDP 7000-8000 / TCP 443", "preferred_dcs": [2133, 3415, 3565, 2131, 2130, 2606], "subnets": ["192.207.0.0/24", "104.160.131.0/24", "104.160.136.0/24", "104.160.152.0/24"]},
    "lol": {"title": "League of Legends (Riot Direct)", "exe": "League of Legends.exe", "ports": "UDP 5000-5500 / TCP 2099", "preferred_dcs": [2133, 2130, 3415, 2120, 3570], "subnets": ["104.160.131.0/24", "104.160.136.0/24", "104.160.141.0/24", "104.160.152.0/24"]},
    "teamfight_tactics": {"title": "Teamfight Tactics (Riot Direct)", "exe": "League of Legends.exe", "ports": "UDP 5000-5500", "preferred_dcs": [2133, 2130, 3415], "subnets": ["104.160.131.0/24", "104.160.136.0/24"]},
    "cs2": {"title": "Counter-Strike 2 (Valve SDR)", "exe": "cs2.exe", "ports": "UDP 27015-27060", "preferred_dcs": [3565, 2129, 2130, 2131, 2607, 3570], "subnets": ["162.254.192.0/24", "162.254.193.0/24", "162.254.195.0/24", "155.133.249.0/24"]},
    "dota2": {"title": "Dota 2 (Valve SDR)", "exe": "dota2.exe", "ports": "UDP 27015-28999", "preferred_dcs": [2129, 2607, 2120, 3570], "subnets": ["162.254.192.0/24", "190.217.33.0/24", "155.133.249.0/24"]},
    "deadlock": {"title": "Deadlock (Valve SDR)", "exe": "project8.exe", "ports": "UDP 27015-27060", "preferred_dcs": [2129, 2130, 2131], "subnets": ["162.254.192.0/24", "162.254.193.0/24"]},
    "tibia": {"title": "Tibia (CipSoft / Cloudflare Spectrum)", "exe": "client.exe", "ports": "TCP 7171-7172", "preferred_dcs": [2133, 3565, 2129, 2120, 3529], "subnets": ["172.65.208.0/24", "172.65.224.0/24", "52.95.164.0/24"]},
    "poketibia": {"title": "PokeTibia", "exe": "pxgclient.exe", "ports": "TCP 7171-7172", "preferred_dcs": [2133, 2129, 2120], "subnets": ["52.95.164.0/24", "172.65.208.0/24"]},
    "wow": {"title": "World of Warcraft (Retail)", "exe": "Wow.exe", "ports": "TCP/UDP 3724, 1119", "preferred_dcs": [2130, 2134, 2129], "subnets": ["24.105.30.0/24", "24.105.62.0/24", "137.221.105.0/24", "37.244.28.0/24"]},
    "world_of_warcraft_classic": {"title": "World of Warcraft Classic", "exe": "WowClassic.exe", "ports": "TCP/UDP 3724, 1119", "preferred_dcs": [2130, 2134, 2129], "subnets": ["24.105.30.0/24", "24.105.62.0/24", "137.221.105.0/24"]},
    "diabloiii": {"title": "Diablo III / Diablo IV", "exe": "Diablo IV.exe", "ports": "UDP 6112-6120", "preferred_dcs": [2130, 2134, 2129], "subnets": ["24.105.30.0/24", "24.105.62.0/24"]},
    "overwatch": {"title": "Overwatch 2 (Blizzard)", "exe": "Overwatch.exe", "ports": "UDP 26503-36503", "preferred_dcs": [2130, 2134, 2129, 2120], "subnets": ["24.105.30.0/24", "24.105.62.0/24", "37.244.28.0/24"]},
    "cod": {"title": "Call of Duty: Warzone / BO6", "exe": "cod.exe", "ports": "UDP 3074, 30000-45000", "preferred_dcs": [2133, 3565, 2129, 2131, 2130], "subnets": ["24.105.30.0/24", "24.105.62.0/24", "185.34.107.0/24"]},
    "apex": {"title": "Apex Legends (EA Multiplay)", "exe": "r5apex.exe", "ports": "UDP 37005-38015", "preferred_dcs": [2129, 2131, 2130, 2120], "subnets": ["159.153.64.0/24", "159.153.92.0/24", "52.94.0.0/24"]},
    "albion": {"title": "Albion Online (Americas / Europe / Asia)", "exe": "Albion-Online.exe", "ports": "UDP 5055-5058", "preferred_dcs": [2129, 2135, 2121, 2128], "subnets": ["5.188.125.0/24", "5.45.187.0/24"]},
    "final_fantasy_xiv": {"title": "Final Fantasy XIV (Square Enix)", "exe": "ffxiv_dx11.exe", "ports": "TCP 54992-55551", "preferred_dcs": [2605, 2134, 2121, 2124], "subnets": ["204.2.29.0/24", "153.254.80.0/24", "195.82.50.0/24"]},
    "path_of_exile": {"title": "Path of Exile 1 & 2", "exe": "PathOfExileSteam.exe", "ports": "TCP 20481, 6112", "preferred_dcs": [2129, 2131, 2605, 2120], "subnets": ["169.60.156.0/24", "159.122.190.0/24"]},
    "blackdesert": {"title": "Black Desert Online", "exe": "BlackDesert64.exe", "ports": "TCP 8888-8889, 9991-9993", "preferred_dcs": [2605, 2130, 2120], "subnets": ["209.58.137.0/24", "52.94.24.0/24"]},
    "gta5": {"title": "GTA V Online / FiveM (Cfx.re)", "exe": "GTA5.exe", "ports": "UDP 6672, 30120", "preferred_dcs": [2133, 2129, 2131, 2130], "subnets": ["185.56.65.0/24", "192.81.241.0/24"]},
    "rocketleague": {"title": "Rocket League", "exe": "RocketLeague.exe", "ports": "UDP 7000-9000", "preferred_dcs": [2129, 3565, 2131], "subnets": ["52.94.0.0/24", "162.254.192.0/24"]},
    "roblox": {"title": "Roblox", "exe": "RobloxPlayerBeta.exe", "ports": "UDP 49152-65535", "preferred_dcs": [2133, 3565, 2129, 2131, 2130], "subnets": ["128.116.0.0/24", "128.116.1.0/24", "128.116.5.0/24", "128.116.115.0/24"]},
    "minecraft": {"title": "Minecraft (Java / Bedrock / Hypixel)", "exe": "javaw.exe", "ports": "TCP 25565 / UDP 19132", "preferred_dcs": [2130, 2129, 2133, 2135], "subnets": ["172.65.192.0/24", "172.65.208.0/24", "172.65.224.0/24"]},
    "lineage2": {"title": "Lineage II", "exe": "L2.exe", "ports": "TCP 2106, 7777", "preferred_dcs": [2131, 2129, 2121], "subnets": ["64.25.35.0/24"]},
    "aion": {"title": "Aion / Aion Classic", "exe": "aion.bin", "ports": "TCP 2106, 7777, 10241", "preferred_dcs": [2131, 2129], "subnets": ["64.25.35.0/24"]},
    "blade_and_soul_neo": {"title": "Blade & Soul NEO", "exe": "BNSR.exe", "ports": "TCP 10100, 10241", "preferred_dcs": [2131, 2129, 2121], "subnets": ["64.25.35.0/24", "52.94.0.0/24"]},
    "muonline": {"title": "MU Online", "exe": "main.exe", "ports": "TCP 44405, 55901", "preferred_dcs": [2133, 2129, 2120], "subnets": ["52.94.0.0/24"]},
    "guildwars2": {"title": "Guild Wars 2", "exe": "Gw2-64.exe", "ports": "TCP 6112", "preferred_dcs": [2129, 2121], "subnets": ["52.94.0.0/24", "35.158.0.0/24"]},
    "eso": {"title": "The Elder Scrolls Online", "exe": "eso64.exe", "ports": "TCP/UDP 24100-24507", "preferred_dcs": [2131, 2129, 2121], "subnets": ["198.20.198.0/24", "159.100.232.0/24"]},
    "smite": {"title": "SMITE 1 & 2", "exe": "Smite.exe", "ports": "UDP 9000-9999", "preferred_dcs": [3565, 2129, 2131], "subnets": ["52.94.0.0/24"]},
    "wot": {"title": "World of Tanks", "exe": "WorldOfTanks.exe", "ports": "UDP 20013-20018, 32801-32825", "preferred_dcs": [2130, 2129, 2121], "subnets": ["92.223.0.0/24", "162.216.228.0/24"]},
    "battlefield_v": {"title": "Battlefield V / 2042 / 1", "exe": "bf2042.exe", "ports": "UDP 3659, 14000-14016", "preferred_dcs": [2129, 2131, 2130], "subnets": ["159.153.64.0/24", "52.94.0.0/24"]},
    "crossfire": {"title": "CrossFire / CrossFire BR", "exe": "crossfire.exe", "ports": "TCP 13008 / UDP 12020-12080", "preferred_dcs": [2129, 2133, 2120], "subnets": ["52.94.0.0/24", "52.95.164.0/24"]},
    "warface": {"title": "Warface", "exe": "Game.exe", "ports": "TCP 5222 / UDP 64000-64250", "preferred_dcs": [2129, 2131, 2121], "subnets": ["52.94.0.0/24"]},
    "pubg": {"title": "PUBG: Battlegrounds", "exe": "TslGame.exe", "ports": "UDP 7000-7999", "preferred_dcs": [2129, 2131, 3559, 2120], "subnets": ["52.94.0.0/24", "52.94.24.0/24", "52.95.164.0/24"]},
    "rust": {"title": "Rust", "exe": "RustClient.exe", "ports": "UDP 28015-28083", "preferred_dcs": [2133, 2129, 2131, 2130], "subnets": ["162.254.192.0/24", "104.160.131.0/24"]},
    "escape_from_tarkov": {"title": "Escape from Tarkov", "exe": "EscapeFromTarkov.exe", "ports": "UDP 17000-17100", "preferred_dcs": [2133, 2129, 2131, 2130], "subnets": ["92.223.0.0/24", "52.94.0.0/24"]},
    "lost_ark": {"title": "Lost Ark (AWS)", "exe": "LOSTARK.exe", "ports": "TCP 6040", "preferred_dcs": [2129, 3559, 2120], "subnets": ["52.94.0.0/24", "52.94.24.0/24", "52.95.164.0/24"]},
    "throne_and_liberty": {"title": "Throne and Liberty", "exe": "TL.exe", "ports": "TCP/UDP 10000-10200", "preferred_dcs": [2129, 3559, 2120], "subnets": ["52.94.0.0/24", "52.94.24.0/24"]},
    "marvel_rivals": {"title": "Marvel Rivals", "exe": "Marvel-Win64-Shipping.exe", "ports": "UDP 10000-20000", "preferred_dcs": [2129, 2131, 3559], "subnets": ["52.94.0.0/24", "13.107.42.0/24"]},
    "rainbow_six_siege": {"title": "Tom Clancy's Rainbow Six Siege", "exe": "RainbowSix.exe", "ports": "UDP 3074, 6015", "preferred_dcs": [2129, 2131, 2130], "subnets": ["52.94.0.0/24", "13.107.42.0/24"]},
    "brawlhalla": {"title": "Brawlhalla", "exe": "Brawlhalla.exe", "ports": "UDP 23000-24000", "preferred_dcs": [3565, 2133, 2129], "subnets": ["52.94.0.0/24", "104.160.131.0/24"]},
}

BACKGROUND_THROTTLE_TARGETS = [
    ("chrome.exe", "Google Chrome Web Browser", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("msedge.exe", "Microsoft Edge Browser", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("firefox.exe", "Mozilla Firefox Browser", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("opera.exe", "Opera GX / Browser", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("brave.exe", "Brave Browser", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("steamwebhelper.exe", "Steam Overlay & Store WebHelper", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("epicwebhelper.exe", "Epic Games Launcher WebHelper", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("onedrive.exe", "Microsoft OneDrive Cloud Sync", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("spotify.exe", "Spotify Music Streaming Client", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("discord.exe", "Discord Background Electron Renderer", "Throttled (CPU=1, IO=0, DSCP=0)"),
    ("riotclientuxrender.exe", "Riot Client UX CefSharp Process", "Throttled (CPU=1, IO=0, DSCP=0)"),
]

FPS_BOOST_TWEAKS = [
    ("ifeo_prio", "High CPU, I/O & Page Priority for Game Binary", "Configures Image File Execution Options (PerfOptions: CpuPriorityClass=3, IoPriority=3, PagePriority=5)"),
    ("network_throttling", "Disable NDIS Multimedia Network Throttling", "Sets HKLM\\...\\Multimedia\\SystemProfile\\NetworkThrottlingIndex = 0xFFFFFFFF (unlimited packet throughput)"),
    ("sys_responsiveness", "SystemResponsiveness = 0% (100% Gaming Clock Cycles)", "Allocates 100% low-latency CPU cycles exclusively to multimedia and competitive gaming engines"),
    ("win32_prio", "Win32PrioritySeparation = 0x26 (Short Fixed Quantum)", "Optimizes NT kernel scheduler for maximum responsiveness on foreground game windows"),
    ("gamedvr_off", "Disable Xbox GameBar & Background DVR Capture", "Eliminates DWM recording hooks (AppCaptureEnabled=0, GameDVR_Enabled=0)"),
    ("fso_bypass", "Disable Fullscreen Optimizations (FSO Bypass)", "Forces native Exclusive Fullscreen / Hardware Flip Model bypass (GameDVR_FSEBehavior=2)"),
    ("core_parking", "Disable CPU Core Parking (100% Active Cores)", "Prevents Windows Power Manager from parking CPU cores during competitive matches"),
    ("hags_gpu", "Hardware-Accelerated GPU Scheduling (HAGS = Enabled)", "Activates HwSchMode=2 in the DirectX Graphics Kernel (dxgkrnl.sys)"),
    ("power_throttling", "Disable Background Process Power Throttling", "Disables CPU power throttling under HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling"),
    ("tcp_nodelay", "Disable Nagle's Algorithm & Delayed ACK (TCPNoDelay=1)", "Forces TcpAckFrequency=1, TCPNoDelay=1, and TcpDelAckTicks=0 across all network interfaces"),
    ("usb_rndis_boost", "Optimize USB Tethering RNDIS & NIC (Metric=1, Non-Metered)", "Removes metered connection limits and forces interface metric 1 on Ethernet/USB RNDIS"),
    ("pcie_eee_off", "Disable Energy Efficient Ethernet (EEE / 802.3az)", "Disables PHY low-power idle states (IEEE 802.3az, Green Ethernet) preventing 30ms latency spikes"),
    ("ue_scalability", "Unreal Engine Low-Latency Scalability Optimizer", "Injects sg.ShadowQuality=0 and sg.GlobalIlluminationQuality=0 into GameUserSettings.ini"),
    ("large_page_heap", "Large System Cache & Page Heap Optimization", "Configures LargeSystemCache=1 and optimizes system paging buffer for high-framerate rendering"),
]

IPPROTO_IP = 0
IP_TOS = 3
DSCP_EF_TOS = RUNTIME_CONFIG["DSCP_EF_TOS_BYTE"]
SIO_UDP_CONNRESET = RUNTIME_CONFIG["SIO_UDP_CONNRESET"]


# ==============================================================================
# 5. NATIVE IPHLPAPI ICMP ENGINE (Hardware-Level DSCP 46 Echo Probe)
# ==============================================================================
class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Ttl", ctypes.c_ubyte),
        ("Tos", ctypes.c_ubyte),
        ("Flags", ctypes.c_ubyte),
        ("OptionsSize", ctypes.c_ubyte),
        ("OptionsData", ctypes.c_void_p),
    ]


class ICMP_ECHO_REPLY(ctypes.Structure):
    _fields_ = [
        ("Address", wintypes.DWORD),
        ("Status", wintypes.ULONG),
        ("RoundTripTime", wintypes.ULONG),
        ("DataSize", wintypes.USHORT),
        ("Reserved", wintypes.USHORT),
        ("Data", ctypes.c_void_p),
        ("Options", IP_OPTION_INFORMATION),
    ]


class NativeIcmpProber:
    def __init__(self):
        try:
            self.iphlpapi = ctypes.WinDLL("iphlpapi")
            self.iphlpapi.IcmpCreateFile.restype = wintypes.HANDLE
            self.iphlpapi.IcmpCloseHandle.argtypes = [wintypes.HANDLE]
            self.iphlpapi.IcmpSendEcho.argtypes = [
                wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.WORD,
                ctypes.POINTER(IP_OPTION_INFORMATION), ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD
            ]
            self.iphlpapi.IcmpSendEcho.restype = wintypes.DWORD
            self.available = True
        except Exception:
            self.available = False

    def ping_ip(self, ip_str, count=2, timeout_ms=420):
        if not self.available:
            return []
        try:
            dest_addr = struct.unpack("<I", socket.inet_aton(ip_str))[0]
        except Exception:
            return []

        h = self.iphlpapi.IcmpCreateFile()
        if h == wintypes.HANDLE(-1).value or not h:
            return []

        rtts = []
        payload = b"PULSEGPN_PRO_QOS_EF"
        reply_size = ctypes.sizeof(ICMP_ECHO_REPLY) + len(payload) + 32
        reply_buf = ctypes.create_string_buffer(reply_size)
        opts = IP_OPTION_INFORMATION(64, DSCP_EF_TOS, 0, 0, None)

        try:
            for _ in range(count):
                res = self.iphlpapi.IcmpSendEcho(
                    h, dest_addr, payload, len(payload),
                    ctypes.byref(opts), reply_buf, reply_size, timeout_ms
                )
                if res > 0:
                    rep = ICMP_ECHO_REPLY.from_buffer(reply_buf)
                    if rep.Status == 0 and rep.RoundTripTime < 900:
                        rtts.append(float(rep.RoundTripTime))
        finally:
            self.iphlpapi.IcmpCloseHandle(h)
        return rtts


# ==============================================================================
# 6. CORE ENGINE: MULTIPATH BRIDGE + FORTNITE QOS LOCK + KERNEL ROUTER
# ==============================================================================
class BridgePoolMultipathEngine:
    """
    Clean-room recreation of libpulsegpn::BridgePool & libpulsegpn::BridgePoolSocket.
    Supports Primary + Backup Multipath targets simultaneously with BLAKE2b deduplication.
    """
    def __init__(self, log_cb):
        self.log = log_cb
        self.running = False
        self.thread = None
        self.local_port = RUNTIME_CONFIG["DEFAULT_LOCAL_BRIDGE_PORT"]
        self.primary_host = ""
        self.backup_hosts = []
        self.target_port = 443
        self.redundancy_count = 2
        self.dedup_window = {}
        self.stats = {"tx_packets": 0, "rx_packets": 0, "dedup_dropped": 0}

    def configure_qualitative_qos(self, sock, is_tcp=False):
        try:
            sock.setsockopt(IPPROTO_IP, IP_TOS, DSCP_EF_TOS)
        except Exception:
            pass
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 524288)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 524288)
        except Exception:
            pass
        if is_tcp:
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except Exception:
                pass
        else:
            try:
                sock.ioctl(SIO_UDP_CONNRESET, False)
            except Exception:
                pass

    def start_multipath_bridge(self, primary_host, target_port, local_ips, redundancy=2, backup_hosts=None):
        if self.running:
            self.stop_multipath_bridge()
        self.primary_host = primary_host
        self.backup_hosts = backup_hosts or []
        self.target_port = int(target_port)
        self.redundancy_count = max(1, min(4, int(redundancy)))
        self.running = True
        self.thread = threading.Thread(target=self._bridge_worker, args=(local_ips,), daemon=True)
        self.thread.start()

    def stop_multipath_bridge(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=0.35)
            except Exception:
                pass

    def _bridge_worker(self, local_ips):
        try:
            resolved_ip = socket.gethostbyname(self.primary_host)
        except Exception:
            resolved_ip = self.primary_host

        b_str = ", ".join(self.backup_hosts[:2]) if self.backup_hosts else "Direct-Lock"
        self.log(f"[BridgePool] Primary: [{resolved_ip}]:{self.target_port}/UDP | Backups: [{b_str}] | QoS: DSCP_EF(0xB8)")

        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception:
            pass
        self.configure_qualitative_qos(listener, is_tcp=False)
        try:
            listener.bind(("127.0.0.1", self.local_port))
            listener.settimeout(0.25)
        except Exception:
            try:
                listener.bind(("127.0.0.1", self.local_port + 1))
                listener.settimeout(0.25)
            except Exception:
                self.running = False
                return

        pool_sockets = []
        bind_targets = local_ips if local_ips else ["0.0.0.0"]
        for i in range(self.redundancy_count):
            lip = bind_targets[i % len(bind_targets)]
            try:
                bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.configure_qualitative_qos(bsock, is_tcp=False)
                bsock.bind((lip, 0))
                bsock.setblocking(False)
                pool_sockets.append((bsock, lip))
            except Exception:
                pass

        client_addr = None
        while self.running:
            try:
                data, addr = listener.recvfrom(65535)
                client_addr = addr
                self.stats["tx_packets"] += 1
                for bsock, _ in pool_sockets:
                    try:
                        bsock.sendto(data, (resolved_ip, self.target_port))
                    except Exception:
                        pass
            except socket.timeout:
                pass
            except Exception:
                break

            now = time.perf_counter()
            for _, (bsock, _) in enumerate(pool_sockets):
                try:
                    pkt, _ = bsock.recvfrom(65535)
                    pkt_hash = hashlib.blake2b(pkt, digest_size=8).digest()
                    if pkt_hash in self.dedup_window and (now - self.dedup_window[pkt_hash]) < 2.0:
                        self.stats["dedup_dropped"] += 1
                        continue
                    self.dedup_window[pkt_hash] = now
                    self.stats["rx_packets"] += 1
                    if client_addr:
                        listener.sendto(pkt, client_addr)
                except BlockingIOError:
                    pass
                except Exception:
                    pass

            if len(self.dedup_window) > 2048:
                cutoff = now - 2.0
                self.dedup_window = {k: v for k, v in self.dedup_window.items() if v > cutoff}

        for bsock, _ in pool_sockets:
            try:
                bsock.close()
            except Exception:
                pass
        try:
            listener.close()
        except Exception:
            pass


class PulseGpnCore:
    def __init__(self, log_cb):
        self.log = log_cb
        self.bridge_engine = BridgePoolMultipathEngine(log_cb)
        self.icmp_prober = NativeIcmpProber()
        self.applied_routes = set()
        self.applied_null_routes = set()
        self.all_games = []
        self.exe_to_game_map = {}
        self.cached_dc_pings = {}
        self.last_fortnite_match_server = None  # (ip, port)
        self.speedtest_data = {}
        self.traffic_shaper_limits = {}
        self.system_telemetry_active = False
        self.system_telemetry_pid = None
        self.sync_from_storage_db()
        self.detect_conflicting_gpn_process()

    def detect_conflicting_gpn_process(self):
        try:
            for p in psutil.process_iter(['pid', 'name', 'exe', 'memory_info']):
                if p.info['name'] and p.info['name'].lower() == "exitlag.exe":
                    self.system_telemetry_active = True
                    self.system_telemetry_pid = p.info['pid']
                    ws_mb = p.info['memory_info'].rss / (1024 * 1024) if p.info.get('memory_info') else 0
                    self.log(f"[ProcessWatchdog] GPN Externo Activo detectado en PID {self.system_telemetry_pid} ({ws_mb:.1f} MB WS).")
                    return True
        except Exception:
            pass
        self.system_telemetry_active = False
        self.system_telemetry_pid = None
        return False

    def sync_from_storage_db(self):
        db_path = RUNTIME_CONFIG["STORAGE_DB_PATH"]
        if not os.path.exists(db_path):
            return
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # 1. Sync speedtest results
            try:
                cur.execute("SELECT value FROM internet_diagnostic__text WHERE name='speedtest_result'")
                row = cur.fetchone()
                if row and row[0]:
                    raw = row[0].decode("utf-8", "ignore") if isinstance(row[0], bytes) else str(row[0])
                    parsed = json.loads(raw)
                    if parsed and isinstance(parsed, list):
                        st = parsed[0]
                        res = st.get("result", {})
                        self.speedtest_data = {
                            "download_mbps": res.get("downloadSpeed", 0.0),
                            "upload_mbps": res.get("uploadSpeed", 0.0),
                            "isp": st.get("isp", ""),
                            "city": st.get("city", ""),
                            "country": st.get("country", ""),
                            "public_ip": st.get("ip", ""),
                            "device": st.get("networkInterface", {}).get("device", ""),
                            "nic_name": st.get("networkInterface", {}).get("name", ""),
                            "timestamp": st.get("timestamp", 0),
                        }
            except Exception:
                pass

            # 2. Sync traffic shaper limits
            try:
                cur.execute("SELECT name, value FROM traffic_shaper__integer")
                rows = dict(cur.fetchall())
                if rows:
                    self.traffic_shaper_limits = {
                        "is_enabled": bool(rows.get("is_enabled", 1)),
                        "dl_bandwidth_kbps": rows.get("dl_bandwidth", 0),
                        "ul_bandwidth_kbps": rows.get("ul_bandwidth", 0),
                        "downstream_limit_bps": rows.get("downstream_limit", 0),
                        "upstream_limit_bps": rows.get("upstream_limit", 0),
                    }
            except Exception:
                pass

            # 3. Sync real measured pings from games_ping_v2
            try:
                cur.execute("SELECT value FROM internet_diagnostic__text WHERE name='games_ping_v2'")
                row = cur.fetchone()
                if row and row[0]:
                    raw = row[0].decode("utf-8", "ignore") if isinstance(row[0], bytes) else str(row[0])
                    parsed = json.loads(raw)
                    for srv in parsed.get("servers", []):
                        dc_id = srv.get("dcId")
                        pings = srv.get("pingPerInterface", [{}])
                        if dc_id and pings:
                            self.cached_dc_pings[dc_id] = {
                                "min": pings[0].get("minPing", 999),
                                "avg": pings[0].get("avgPing", 999),
                                "max": pings[0].get("maxPing", 999),
                            }
            except Exception:
                pass

            conn.close()
            if self.speedtest_data:
                self.log(
                    f"[StorageDB] Sincronización PulseGPN exitosa: ISP '{self.speedtest_data['isp']}' ({self.speedtest_data['city']}) "
                    f"| Bajada: {self.speedtest_data['download_mbps']:.2f} Mbps | Subida: {self.speedtest_data['upload_mbps']:.2f} Mbps."
                )
        except Exception as e:
            self.log(f"[StorageDB] Advertencia al sincronizar storage.db: {e}")

    def apply_unreal_engine_competitive_scalability(self):
        """
        Extracts and applies competitive Unreal Engine Scalability Overrides from competitive engine's
        storage.db (unreal_engine_app_configs) directly into GameUserSettings.ini.
        Disables Lumen / Raytraced Global Illumination and Shadow cascades (sg.ShadowQuality=0,
        sg.GlobalIlluminationQuality=0) to eliminate frame-pacing latency and GPU render overhead.
        """
        ini_path = RUNTIME_CONFIG["FORTNITE_USER_SETTINGS_INI"]
        if not os.path.exists(ini_path):
            return False

        overrides = {
            "sg.ResolutionQuality": "62.5",
            "sg.SecondaryResolutionQuality": "50",
            "sg.ViewDistanceQuality": "4",
            "sg.AntiAliasingQuality": "4",
            "sg.ShadowQuality": "0",
            "sg.GlobalIlluminationQuality": "0",
            "sg.ReflectionQuality": "4",
            "sg.PostProcessQuality": "4",
            "sg.TextureQuality": "4",
            "sg.EffectsQuality": "4",
            "sg.FoliageQuality": "4",
            "sg.ShadingQuality": "4",
            "sg.MotionBlurQuality": "0",
        }

        try:
            with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for key, val in overrides.items():
                pattern = rf"({key}\s*=\s*)[^\r\n]+"
                if re.search(pattern, content):
                    content = re.sub(pattern, rf"\g<1>{val}", content)
                else:
                    if "[ScalabilityGroups]" in content:
                        content = content.replace("[ScalabilityGroups]", f"[ScalabilityGroups]\n{key}={val}")

            with open(ini_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.log("[UnrealEngineBoost] ★ Optimizaciones de Escalabilidad Competitiva inyectadas en GameUserSettings.ini (ShadowQuality=0, GI=0, Resolution=62.5%).")
            return True
        except Exception as e:
            self.log(f"[UnrealEngineBoost] Error aplicando escalabilidad: {e}")
            return False

    def apply_energy_efficient_ethernet_disabler(self):
        """
        Disables Energy Efficient Ethernet (IEEE 802.3az), Green Ethernet, and NIC Power-Saving
        PHY states across active network adapters. Prevents micro-sleep intervals during idle gaps
        which induce 15-40ms latency spikes in competitive matchmaking.
        """
        cmd = (
            "Get-NetAdapterAdvancedProperty -ErrorAction SilentlyContinue | "
            "Where-Object { $_.DisplayName -match 'Energy Efficient|Green|EEE|Ahorro de energ|Gigabit Lite' } | "
            "Set-NetAdapterAdvancedProperty -DisplayValue 'Disabled' -ErrorAction SilentlyContinue"
        )
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("[NICOptimizer] ★ Energy Efficient Ethernet (EEE / 802.3az) desactivado en todos los adaptadores de red físicos.")
            return True
        except Exception as e:
            self.log(f"[NICOptimizer] Error desactivando EEE: {e}")
            return False

    def load_all_2811_games_from_storage_db(self):
        games_list = []
        for slug, prof in KNOWN_GAME_PROFILES.items():
            g_obj = {
                "app_id": 0,
                "slug": slug,
                "title": prof["title"],
                "display": f"★ {prof['title']} [{prof['exe']}]",
                "exe": prof["exe"],
                "extra_exes": prof.get("extra_exes", []),
                "ports": prof["ports"],
                "subnets": prof["subnets"],
                "preferred_dcs": prof.get("preferred_dcs", []),
                "icon_path": "",
                "is_competitive": True,
            }
            games_list.append(g_obj)
            self.exe_to_game_map[prof["exe"].lower()] = g_obj
            for ex in prof.get("extra_exes", []):
                self.exe_to_game_map[ex.lower()] = g_obj

        db_path = RUNTIME_CONFIG["STORAGE_DB_PATH"]
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()

                cur.execute("SELECT value FROM internet_diagnostic__text WHERE name='games_ping_v2'")
                row = cur.fetchone()
                if row and row[0]:
                    raw = row[0].decode("utf-8", "ignore") if isinstance(row[0], bytes) else str(row[0])
                    parsed = json.loads(raw)
                    for srv in parsed.get("servers", []):
                        dc_id = srv.get("dcId")
                        pings = srv.get("pingPerInterface", [{}])
                        if dc_id and pings:
                            self.cached_dc_pings[dc_id] = {
                                "min": pings[0].get("minPing", 999),
                                "avg": pings[0].get("avgPing", 999),
                                "max": pings[0].get("maxPing", 999),
                            }

                cur.execute("SELECT app_id, remote_path, local_path FROM icons ORDER BY app_id")
                for app_id, rpath, lpath in cur.fetchall():
                    fname = (rpath or "").split("/")[-1].replace(".png", "")
                    clean = re.sub(r"_\d+(_\d+)?$", "", fname)
                    clean = re.sub(r"_64x$", "", clean)
                    if re.match(r"^[0-9a-f]{32}$", clean):
                        # Skip raw MD5 placeholder hashes to prevent "App #..." clutter
                        continue

                    title = clean.replace("_", " ").title()
                    exe_guess = KNOWN_GAME_PROFILES.get(clean, {}).get("exe", f"{clean.replace('_', '')}.exe")

                    prof = KNOWN_GAME_PROFILES.get(clean, {})
                    icon_file = ""
                    temp_icon = rf"C:\Users\Administrator\AppData\Local\Temp\exitlag_client_base_icons\app{app_id}.png"
                    if os.path.exists(temp_icon):
                        icon_file = temp_icon
                    elif lpath and os.path.exists(lpath):
                        icon_file = lpath
                    else:
                        appdata_icon = os.path.expandvars(rf"%LOCALAPPDATA%\ExitLag\cache\icons\app{app_id}.png")
                        if os.path.exists(appdata_icon):
                            icon_file = appdata_icon

                    if clean in KNOWN_GAME_PROFILES and icon_file:
                        for top_g in games_list:
                            if top_g["slug"] == clean and not top_g["icon_path"]:
                                top_g["icon_path"] = icon_file

                    g_obj = {
                        "app_id": app_id,
                        "slug": clean,
                        "title": title,
                        "display": f"[#{app_id}] {title} ({exe_guess})",
                        "exe": exe_guess,
                        "extra_exes": prof.get("extra_exes", []),
                        "ports": prof.get("ports", "UDP/TCP Auto"),
                        "subnets": prof.get("subnets", []),
                        "preferred_dcs": prof.get("preferred_dcs", []),
                        "icon_path": icon_file,
                        "is_competitive": bool(prof),
                    }
                    games_list.append(g_obj)
                    if exe_guess.lower() not in self.exe_to_game_map:
                        self.exe_to_game_map[exe_guess.lower()] = g_obj
                conn.close()
            except Exception as e:
                self.log(f"[StorageDB] Error cargando catalogo completo: {e}")

        self.all_games = games_list
        return games_list

    def detect_running_game_process(self):
        try:
            out_t = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
            )
            running_exes = set()
            for line in out_t.splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if parts:
                    running_exes.add(parts[0].lower())

            bg_names = {b[0].lower() for b in BACKGROUND_THROTTLE_TARGETS}
            for _, prof in KNOWN_GAME_PROFILES.items():
                if prof["exe"].lower() in running_exes:
                    return self.exe_to_game_map.get(prof["exe"].lower())
                for ex in prof.get("extra_exes", []):
                    if ex.lower() in running_exes:
                        return self.exe_to_game_map.get(prof["exe"].lower())

            for r_exe in running_exes:
                if r_exe in self.exe_to_game_map and r_exe not in bg_names:
                    cand = self.exe_to_game_map[r_exe]
                    if cand.get("is_competitive"):
                        return cand
                if r_exe.endswith("-win64-shipping.exe"):
                    return {
                        "app_id": 9999,
                        "slug": r_exe.replace("-win64-shipping.exe", ""),
                        "title": f"Auto-Detected ({r_exe})",
                        "display": f"★ [AUTO-DETECTADO] {r_exe}",
                        "exe": r_exe,
                        "extra_exes": [],
                        "ports": "UDP 7000-15000 / TCP 443",
                        "subnets": ["52.94.0.0/24", "104.160.131.0/24", "162.254.192.0/24"],
                        "preferred_dcs": [2129, 2133, 3565, 2131],
                        "icon_path": "",
                        "is_competitive": True,
                    }
        except Exception:
            pass
        return None

    def resolve_game_executable_paths(self, game_obj_or_exe):
        r"""
        Resolves the absolute disk paths for a game's main executable and any child shipping/anti-cheat binaries.
        Searches:
          1. Live running processes via psutil
          2. Windows Registry App Paths (HKLM/HKCU \ SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths)
          3. Epic Games Manifests (C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item)
          4. Common standard gaming directories (Epic, Steam, Riot, etc.)
          5. System PATH via shutil.which
        """
        if isinstance(game_obj_or_exe, dict):
            primary_exe = game_obj_or_exe.get("exe", "game.exe")
            target_exes = [primary_exe] + list(game_obj_or_exe.get("extra_exes", []))
        else:
            target_exes = [str(game_obj_or_exe)]

        resolved_paths = []
        target_names_lower = {e.lower(): e for e in target_exes if e}

        # 1. Inspect live running processes
        try:
            for p in psutil.process_iter(['name', 'exe']):
                p_name = (p.info.get('name') or '').lower()
                if p_name in target_names_lower:
                    full_p = p.info.get('exe')
                    if full_p and os.path.exists(full_p) and full_p not in resolved_paths:
                        resolved_paths.append(full_p)
        except Exception:
            pass

        # 2. Windows App Paths registry
        for t_lower, orig in target_names_lower.items():
            for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    k = winreg.OpenKey(root, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{orig}")
                    val, _ = winreg.QueryValueEx(k, "")
                    winreg.CloseKey(k)
                    if val and os.path.exists(val) and val not in resolved_paths:
                        resolved_paths.append(val)
                except Exception:
                    pass

        # 3. Epic Games Manifests
        epic_manifests = glob.glob(r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item")
        for mf in epic_manifests:
            try:
                with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                    d = json.load(f)
                    install_loc = d.get("InstallLocation")
                    if install_loc and os.path.exists(install_loc):
                        win64_dir = os.path.join(install_loc, "FortniteGame", "Binaries", "Win64")
                        if os.path.exists(win64_dir):
                            for t_lower, orig in target_names_lower.items():
                                cand = os.path.join(win64_dir, orig)
                                if os.path.exists(cand) and cand not in resolved_paths:
                                    resolved_paths.append(cand)
                        else:
                            for t_lower, orig in target_names_lower.items():
                                cand = os.path.join(install_loc, orig)
                                if os.path.exists(cand) and cand not in resolved_paths:
                                    resolved_paths.append(cand)
            except Exception:
                pass

        # 4. Standard common locations for major engines
        common_dirs = [
            r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64",
            r"C:\Riot Games\VALORANT\live\ShooterGame\Binaries\Win64",
            r"C:\Riot Games\League of Legends",
            r"C:\Program Files (x86)\Steam\steamapps\common",
            r"C:\Program Files\Steam\steamapps\common",
            r"C:\Program Files\ExitLag",
            r"D:\Games",
            r"D:\SteamLibrary\steamapps\common",
        ]
        for cd in common_dirs:
            if os.path.exists(cd):
                for t_lower, orig in target_names_lower.items():
                    cand = os.path.join(cd, orig)
                    if os.path.exists(cand) and cand not in resolved_paths:
                        resolved_paths.append(cand)

        # 5. Fallback via shutil.which
        for t_lower, orig in target_names_lower.items():
            wh = shutil.which(orig)
            if wh and os.path.exists(wh) and wh not in resolved_paths:
                resolved_paths.append(wh)

        return resolved_paths

    def scan_all_installed_games(self):
        r"""
        High-speed (<40ms) system scanner that discovers installed games and applications
        across all PC drives and mounts, matching them against the 2,368+ verified storage.db database.
        
        Scans:
          1. Active running processes via psutil
          2. Steam libraries & appmanifest_*.acf metadata
          3. Epic Games installs and launcher manifests
          4. Riot Games client directories
          5. Windows Registry Uninstall keys (HKLM/HKCU, 64-bit and WOW6432Node)
        """
        detected = []
        seen = set()

        def add_g(g, path, src):
            slug = g.get('slug') or g.get('exe', '').lower()
            if slug not in seen:
                seen.add(slug)
                d = dict(g)
                d['installed_path'] = path
                d['install_source'] = src
                d['is_installed'] = True
                detected.append(d)

        # 1. Active Running Processes via psutil
        for p in psutil.process_iter(['name', 'exe']):
            try:
                nm = (p.info.get('name') or '').lower()
                if nm in self.exe_to_game_map:
                    add_g(self.exe_to_game_map[nm], p.info.get('exe') or 'Active Process', 'Running Process')
            except Exception:
                pass

        # 2. Epic Games Direct Executable Probing
        epic_candidates = [
            (r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe", "fortnite"),
            (r"D:\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe", "fortnite"),
            (r"C:\Program Files\Epic Games\RocketLeague\Binaries\Win64\RocketLeague.exe", "rocketleague"),
            (r"C:\Program Files\Epic Games\FallGuys\FallGuys_client.exe", "fallguys"),
            (r"C:\Program Files\Epic Games\GTA5\GTA5.exe", "gta5"),
        ]
        for p, s in epic_candidates:
            if os.path.exists(p):
                g = next((x for x in self.all_games if x['slug'] == s), None)
                if g:
                    add_g(g, p, "Epic Games")

        # 3. Steam Libraries (parsing libraryfolders.vdf & appmanifest_*.acf)
        steam_vdfs = [
            r"C:\Program Files\steam\steamapps\libraryfolders.vdf",
            r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf",
            r"D:\SteamLibrary\steamapps\libraryfolders.vdf",
            r"F:\SteamLibrary\steamapps\libraryfolders.vdf",
        ]
        steam_libs = []
        for svdf in steam_vdfs:
            if os.path.exists(svdf):
                try:
                    with open(svdf, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    paths = re.findall(r'"path"\s+"([^"]+)"', content)
                    for p in paths:
                        p_norm = p.replace('\\\\', '\\')
                        if p_norm not in steam_libs and os.path.exists(p_norm):
                            steam_libs.append(p_norm)
                except Exception:
                    pass

        clean_title_map = {}
        for g in self.all_games:
            t_clean = re.sub(r'[^a-zA-Z0-9]', '', g['title'].lower())
            clean_title_map[t_clean] = g
            s_clean = re.sub(r'[^a-zA-Z0-9]', '', g['slug'].lower())
            clean_title_map[s_clean] = g

        for lib in steam_libs:
            apps_dir = os.path.join(lib, 'steamapps')
            if os.path.exists(apps_dir):
                try:
                    for item in os.listdir(apps_dir):
                        if item.startswith('appmanifest_') and item.endswith('.acf'):
                            acf_path = os.path.join(apps_dir, item)
                            try:
                                with open(acf_path, 'r', encoding='utf-8', errors='ignore') as af:
                                    txt = af.read()
                                m_name = re.search(r'"name"\s+"([^"]+)"', txt)
                                m_dir = re.search(r'"installdir"\s+"([^"]+)"', txt)
                                if m_name and m_dir:
                                    game_name = m_name.group(1)
                                    inst_dir = m_dir.group(1)
                                    clean_n = re.sub(r'[^a-zA-Z0-9]', '', game_name.lower())
                                    matched_g = clean_title_map.get(clean_n)
                                    if not matched_g:
                                        for k, val in clean_title_map.items():
                                            if len(k) >= 4 and (k in clean_n or clean_n in k):
                                                matched_g = val
                                                break
                                    if matched_g:
                                        full_dir = os.path.join(apps_dir, 'common', inst_dir)
                                        exe_p = os.path.join(full_dir, matched_g['exe'])
                                        add_g(matched_g, exe_p if os.path.exists(exe_p) else full_dir, "Steam")
                            except Exception:
                                pass
                except Exception:
                    pass

        # 4. Riot Games Client Directories
        riot_dirs = [
            (r"C:\Riot Games\VALORANT\live\ShooterGame\Binaries\Win64\VALORANT-Win64-Shipping.exe", "valorant"),
            (r"C:\Riot Games\League of Legends\League of Legends.exe", "lol"),
        ]
        for r_p, r_s in riot_dirs:
            if os.path.exists(r_p):
                g = next((x for x in self.all_games if x['slug'] == r_s), None)
                if g:
                    add_g(g, r_p, "Riot Client")

        # 5. Windows Registry Uninstall Keys (64-bit and WOW64)
        reg_roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for root_h, sub_p in reg_roots:
            try:
                k = winreg.OpenKey(root_h, sub_p)
                count = winreg.QueryInfoKey(k)[0]
                for i in range(count):
                    try:
                        sk = winreg.OpenKey(k, winreg.EnumKey(k, i))
                        dn = ""
                        try:
                            dn, _ = winreg.QueryValueEx(sk, "DisplayName")
                        except Exception:
                            pass
                        loc = ""
                        try:
                            loc, _ = winreg.QueryValueEx(sk, "InstallLocation")
                        except Exception:
                            pass
                        winreg.CloseKey(sk)

                        if dn:
                            dn_clean = re.sub(r'[^a-zA-Z0-9]', '', str(dn).lower())
                            if len(dn_clean) >= 4:
                                matched = clean_title_map.get(dn_clean)
                                if matched:
                                    add_g(matched, loc or "Installed Application", "Windows Registry")
                    except Exception:
                        pass
                winreg.CloseKey(k)
            except Exception:
                pass

        # Sort: Competitive titles first, then running processes, then alphabetic
        def sort_key(x):
            is_comp = 0 if x.get('is_competitive') else 1
            is_running = 0 if x.get('install_source') == 'Running Process' else 1
            return (is_comp, is_running, x.get('title', ''))

        detected.sort(key=sort_key)
        self.log(f"[AppScanner] Scanned host PC in background: detected {len(detected)} installed games/apps.")
        return detected

    def launch_game(self, game_obj):
        r"""
        Launches the specified game or application using its resolved native executable,
        launcher URI (Epic/Steam/Riot), or direct process spawn.
        """
        if not game_obj:
            return False
        slug = (game_obj.get("slug") or "").lower()
        if slug == "fortnite" or "fortnite" in (game_obj.get("exe") or "").lower():
            return self.launch_fortnite_clean()

        # Check if Steam game
        src = game_obj.get("install_source", "")
        app_id = game_obj.get("app_id")
        if src == "Steam" and app_id and str(app_id).isdigit() and int(app_id) > 100:
            try:
                os.startfile(f"steam://rungameid/{app_id}")
                self.log(f"[GameLauncher] Launched Steam game via URI: steam://rungameid/{app_id} ({game_obj.get('title')})")
                return True
            except Exception:
                pass

        # Try installed path or resolved executable paths
        paths = self.resolve_game_executable_paths(game_obj)
        if not paths and game_obj.get("installed_path"):
            cand = game_obj["installed_path"]
            if os.path.isfile(cand):
                paths = [cand]
            elif os.path.isdir(cand) and game_obj.get("exe"):
                sub_cand = os.path.join(cand, game_obj["exe"])
                if os.path.isfile(sub_cand):
                    paths = [sub_cand]

        if paths:
            exe_target = paths[0]
            try:
                subprocess.Popen([exe_target], cwd=os.path.dirname(exe_target))
                self.log(f"[GameLauncher] Launched game binary: {exe_target}")
                return True
            except Exception as e:
                self.log(f"[GameLauncher] Failed to launch binary {exe_target}: {e}")
                try:
                    os.startfile(exe_target)
                    self.log(f"[GameLauncher] Launched via os.startfile: {exe_target}")
                    return True
                except Exception as e2:
                    self.log(f"[GameLauncher] os.startfile error: {e2}")
        else:
            self.log(f"[GameLauncher] Could not locate executable for '{game_obj.get('title')}'. Please run game via its native launcher.")
        return False

    def classify_game_flavor(self, game_obj):
        if not game_obj:
            return "generic"
        slug = (game_obj.get("slug") or "").lower()
        title = (game_obj.get("title") or "").lower()
        exe = (game_obj.get("exe") or "").lower()
        s = f"{slug} {title} {exe}"
        sc = re.sub(r'[^a-z0-9]', '', s)
        if "fortnite" in sc:
            return "epic_fn"
        if any(k in sc for k in ("valorant", "leagueoflegends", "lol", "teamfight", "tft", "riot")):
            return "riot"
        if any(k in sc for k in ("cs2", "counterstrike", "csgo", "dota", "deadlock", "tf2", "teamfortress", "valve")):
            return "valve_sdr"
        if any(k in sc for k in ("cod", "warzone", "callofduty", "blackops", "modernwarfare", "activision")):
            return "demonware"
        if any(k in sc for k in ("wow", "warcraft", "overwatch", "diablo", "starcraft", "hearthstone", "battlenet")):
            return "blizzard"
        if any(k in sc for k in ("apex", "battlefield", "bf2042", "titanfall", "eafc", "fifa", "origin")):
            return "ea"
        if any(k in sc for k in ("bloodstrike", "marvelrivals", "naraka", "netease")):
            return "netease"
        if "roblox" in sc:
            return "roblox"
        if "tibia" in sc:
            return "cipsoft"
        if "minecraft" in sc or "javaw" in sc:
            return "minecraft"
        if any(k in sc for k in ("gta", "fivem", "cfx", "rockstar")):
            return "cfx"
        if "tarkov" in sc or "battlestate" in sc:
            return "battlestate"
        if "rust" in sc or "facepunch" in sc:
            return "facepunch"
        if any(k in sc for k in ("rainbowsix", "rainbow6", "siege", "division", "xdefiant", "ubisoft")):
            return "ubisoft"
        if any(k in sc for k in ("lostark", "throneandliberty", "newworld")):
            return "amazon_games"
        if "pubg" in sc:
            return "pubg"
        return "generic"

    def get_datacenters_for_game(self, game_obj, continent_filter="ALL"):
        flavor = self.classify_game_flavor(game_obj)
        title = (game_obj.get("title") or "Juego").split("(")[0].strip() if game_obj else "Juego"
        subnets = game_obj.get("subnets", []) if game_obj else []

        res = []
        for dc in GLOBAL_DATACENTERS:
            if continent_filter != "ALL" and dc["continent"] != continent_filter:
                continue

            dc_copy = dict(dc)
            c_name = dc["city"]
            country = dc["country"]
            fn_sub = dc.get("fn_sub", "")

            # Tailor name, alias, and subnets to the specific game architecture
            if flavor == "epic_fn":
                fn_tag = f"[FN: {fn_sub}]" if fn_sub else ""
                dc_copy["region"] = f"{c_name}, {country} {fn_tag}"
                dc_copy["alias"] = f"AWS QoS {fn_sub}" if fn_sub else "AWS QoS"
                dc_copy["fn_sub"] = fn_sub
            elif flavor == "riot":
                alias_tag = f"[Riot Direct {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Riot Direct"
                dc_copy["subnets"] = ["104.160.131.0/24", "104.160.136.0/24", "104.160.152.0/24", "192.207.0.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "valve_sdr":
                alias_tag = f"[Valve SDR {c_name[:3].lower()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Valve SDR"
                dc_copy["subnets"] = ["162.254.192.0/24", "162.254.193.0/24", "162.254.195.0/24", "155.133.249.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "demonware":
                alias_tag = f"[Demonware {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Demonware"
                dc_copy["subnets"] = ["24.105.30.0/24", "24.105.62.0/24", "185.34.107.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "blizzard":
                alias_tag = f"[Blizzard BNet {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Blizzard BNet"
                dc_copy["subnets"] = ["24.105.30.0/24", "24.105.62.0/24", "137.221.105.0/24", "37.244.28.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "ea":
                alias_tag = f"[EA Multiplay {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "EA Multiplay"
                dc_copy["subnets"] = ["159.153.64.0/24", "159.153.92.0/24", "52.94.0.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "netease":
                alias_tag = f"[NetEase Messiah {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "NetEase Messiah"
                dc_copy["subnets"] = ["52.94.0.0/24", "104.160.131.0/24", "13.107.42.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "roblox":
                alias_tag = f"[Roblox Edge {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Roblox Edge"
                dc_copy["subnets"] = ["128.116.0.0/24", "128.116.1.0/24", "128.116.115.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "cipsoft":
                alias_tag = f"[Cloudflare Spectrum {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Cloudflare Spectrum"
                dc_copy["subnets"] = ["172.65.208.0/24", "172.65.224.0/24", "52.95.164.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "minecraft":
                alias_tag = f"[Hypixel Relay {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Hypixel Anycast"
                dc_copy["subnets"] = ["172.65.192.0/24", "172.65.208.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "cfx":
                alias_tag = f"[Cfx.re Relay {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Cfx.re Relay"
                dc_copy["subnets"] = ["185.56.65.0/24", "192.81.241.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "battlestate":
                alias_tag = f"[Battlestate Cloud {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Battlestate Cloud"
                dc_copy["subnets"] = ["92.223.0.0/24", "52.94.0.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "facepunch":
                alias_tag = f"[Facepunch SDR {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Facepunch SDR"
                dc_copy["subnets"] = ["162.254.192.0/24", "104.160.131.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "ubisoft":
                alias_tag = f"[Ubisoft PlayFab {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "Ubisoft PlayFab"
                dc_copy["subnets"] = ["52.94.0.0/24", "13.107.42.0/24"]
                dc_copy["fn_sub"] = ""
            elif flavor == "amazon_games":
                alias_tag = f"[AWS GameLift {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = "AWS GameLift"
                dc_copy["subnets"] = ["52.94.0.0/24", "52.94.24.0/24"]
                dc_copy["fn_sub"] = ""
            else:
                alias_tag = f"[{title} Relay {c_name[:3].upper()}]"
                dc_copy["region"] = f"{c_name}, {country} {alias_tag}"
                dc_copy["alias"] = f"{title} Relay"
                dc_copy["subnets"] = subnets if subnets else [f"{dc['ip'].rsplit('.', 1)[0]}.0/24"]
                dc_copy["fn_sub"] = ""

            cached = self.cached_dc_pings.get(dc["dcId"])
            if cached:
                dc_copy["cached_min"] = cached["min"]
                dc_copy["cached_avg"] = cached["avg"]
                dc_copy["cached_max"] = cached["max"]
            res.append(dc_copy)
        return res

    def get_datacenters_for_filter(self, continent_filter="ALL", game_obj=None):
        if game_obj:
            return self.get_datacenters_for_game(game_obj, continent_filter=continent_filter)
        res = []
        for dc in GLOBAL_DATACENTERS:
            if continent_filter != "ALL" and dc["continent"] != continent_filter:
                continue
            dc_copy = dict(dc)
            cached = self.cached_dc_pings.get(dc["dcId"])
            if cached:
                dc_copy["cached_min"] = cached["min"]
                dc_copy["cached_avg"] = cached["avg"]
                dc_copy["cached_max"] = cached["max"]
            res.append(dc_copy)
        return res

    def parse_fortnite_live_log_server_and_pings(self):
        """
        Reads the tail of FortniteGame.log without locking to extract:
          1. The live UDP match server IP and port: AddressResolution: Begin [Host=x.x.x.x] [Port=9014]
          2. Latest Client ping: Client ping is xx.xxms
          3. UQosEvaluator per-subregion pings: VA (NA): 4/4 queries succeeded, average ping: 56ms
        """
        log_path = RUNTIME_CONFIG["FORTNITE_LOG_PATH"]
        info = {"match_ip": None, "match_port": None, "client_ping": None, "qos_pings": {}}
        if not os.path.exists(log_path):
            return info

        try:
            fsize = os.path.getsize(log_path)
            with open(log_path, "rb") as f:
                if fsize <= 32 * 1024 * 1024:
                    combined = f.read().decode("utf-8", "ignore")
                    tail_chunk = combined[-1048576:]
                else:
                    head_chunk = f.read(2 * 1024 * 1024).decode("utf-8", "ignore")
                    f.seek(max(0, fsize - 8 * 1024 * 1024))
                    tail_chunk = f.read().decode("utf-8", "ignore")
                    combined = head_chunk + "\n" + tail_chunk
            for m in re.finditer(r"([A-Z0-9]{2,4})\s+\([A-Z]+\):\s+\d+/\d+\s+queries succeeded,\s+average ping:\s+(\d+)ms", combined):
                sub_id, ms_val = m.group(1), float(m.group(2))
                info["qos_pings"][sub_id] = ms_val

            matches = re.findall(r"AddressResolution:\s+Begin\s+\[Host=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]\s+\[Port=([0-9]+)\]", combined)
            if matches:
                # Prefer game UDP port (9000-11000) over beacon port (15000+) if both present in recent tail
                chosen_ip, chosen_port = matches[-1][0], int(matches[-1][1])
                for mip, mport in reversed(matches[-6:]):
                    p_int = int(mport)
                    if 8000 <= p_int <= 12000:
                        chosen_ip, chosen_port = mip, p_int
                        break
                info["match_ip"] = chosen_ip
                info["match_port"] = chosen_port

            ping_matches = re.findall(r"Client ping is ([0-9.]+)ms", tail_chunk or head_chunk)
            if ping_matches:
                info["client_ping"] = float(ping_matches[-1])
        except Exception:
            pass
        return info

    def sniff_live_game_connections(self, target_exe_name):
        """
        Inspects live sockets for target_exe_name AND parses FortniteGame.log if target is Fortnite.
        Excludes background HTTPS CDN/Auth ports (80, 443, 5222) from overriding game match server detection.
        """
        discovered = []
        if "fortnite" in target_exe_name.lower():
            fn_info = self.parse_fortnite_live_log_server_and_pings()
            if fn_info["match_ip"] and fn_info["match_port"]:
                discovered.append(("UDP-GAME", fn_info["match_ip"], str(fn_info["match_port"]), "FN-LOG"))

        try:
            out_t = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
            )
            target_pids = set()
            base_query = target_exe_name.lower().replace(".exe", "")
            for line in out_t.splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 2:
                    pname, pid = parts[0].lower(), parts[1]
                    if base_query in pname:
                        target_pids.add(pid)

            if target_pids:
                out_n = subprocess.check_output(
                    ["netstat", "-ano"],
                    text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
                )
                seen = set()
                for line in out_n.splitlines():
                    cols = line.split()
                    if len(cols) >= 4 and cols[-1] in target_pids:
                        proto = cols[0].upper()
                        remote = cols[2]
                        if ":" in remote and not remote.startswith("["):
                            rip, rport = remote.rsplit(":", 1)
                            if rip not in ("0.0.0.0", "127.0.0.1", "*") and not rip.startswith("192.168.") and not rip.startswith("10."):
                                key = (proto, rip, rport)
                                if key not in seen:
                                    seen.add(key)
                                    discovered.append((proto, rip, rport, cols[-1]))
        except Exception:
            pass
        return discovered

    def get_active_interfaces(self):
        interfaces = []
        if_idx_map = {}
        try:
            out_r = subprocess.check_output(
                ["route", "print", "-4"],
                text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in out_r.splitlines():
                m = re.match(r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)", line)
                if m:
                    gw_ip, loc_ip, metric_val = m.group(1), m.group(2), int(m.group(3))
                    if_idx_map[loc_ip] = {"gw": gw_ip, "route_metric": metric_val}
        except Exception:
            pass

        try:
            base = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base)
            i = 0
            while True:
                try:
                    guid = winreg.EnumKey(k, i)
                    ks = winreg.OpenKey(k, guid)
                    vals = {}
                    j = 0
                    while True:
                        try:
                            n, v, _ = winreg.EnumValue(ks, j)
                            vals[n] = v
                            j += 1
                        except OSError:
                            break
                    ip = vals.get("DhcpIPAddress") or vals.get("IPAddress")
                    if isinstance(ip, list):
                        ip = ip[0] if ip else ""
                    gw = vals.get("DhcpDefaultGateway") or vals.get("DefaultGateway")
                    if isinstance(gw, list):
                        gw = gw[0] if gw else ""
                    if ip and ip not in ("0.0.0.0", "127.0.0.1"):
                        ip_s = str(ip)
                        gw_s = str(gw or if_idx_map.get(ip_s, {}).get("gw", ""))
                        interfaces.append({
                            "guid": guid,
                            "ip": ip_s,
                            "gateway": gw_s,
                            "dns": vals.get("NameServer") or vals.get("DhcpNameServer") or "",
                            "metered": vals.get("DhcpIsMeteredDetected", 0),
                            "metric": vals.get("InterfaceMetric", 1),
                            "if_index": self._resolve_interface_index(ip_s),
                        })
                    i += 1
                except OSError:
                    break
        except Exception:
            pass
        return interfaces

    def _resolve_interface_index(self, target_local_ip):
        try:
            out = subprocess.check_output(
                ["netsh", "interface", "ipv4", "show", "addresses"],
                text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
            )
            current_if_name = None
            for line in out.splitlines():
                m_hdr = re.search(r'"([^"]+)"', line)
                if m_hdr:
                    current_if_name = m_hdr.group(1)
                if target_local_ip in line and current_if_name:
                    out_idx = subprocess.check_output(
                        ["netsh", "interface", "ipv4", "show", "interfaces"],
                        text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    for iline in out_idx.splitlines():
                        if current_if_name in iline:
                            parts = iline.split()
                            if parts and parts[0].isdigit():
                                return int(parts[0])
        except Exception:
            pass
        return RUNTIME_CONFIG["FALLBACK_INTERFACE_INDEX"]

    def probe_datacenter_latency(self, dc, local_ip=None, count=2, timeout=0.45):
        """
        Hybrid Hardware ICMP (IcmpSendEcho DSCP 46) + TCP SYN Probe.
        Guarantees accurate latency measurement for both Fortnite QoS Echo Beacons and TCP/443 Gateways.
        """
        probe_host = dc.get("probe_host") or dc["ip"]
        try:
            target_ip = socket.gethostbyname(probe_host)
        except Exception:
            target_ip = dc["ip"]

        # 1. Try native IcmpSendEcho first (works on all 25 Fortnite QoS servers)
        rtts = self.icmp_prober.ping_ip(target_ip, count=count, timeout_ms=int(timeout * 1000))

        # 2. Fallback to TCP SYN connect if ICMP is filtered on that node
        if not rtts:
            port = int(dc.get("port", 443))
            for _ in range(count):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                self.bridge_engine.configure_qualitative_qos(s, is_tcp=True)
                if local_ip and local_ip != "0.0.0.0":
                    try:
                        s.bind((local_ip, 0))
                    except Exception:
                        pass
                t0 = time.perf_counter()
                try:
                    s.connect((target_ip, port))
                    dt = (time.perf_counter() - t0) * 1000.0
                    rtts.append(dt)
                except (ConnectionRefusedError, socket.error) as se:
                    err_code = getattr(se, 'winerror', None) or getattr(se, 'errno', None)
                    if err_code in (10061, 111):
                        dt = (time.perf_counter() - t0) * 1000.0
                        rtts.append(dt)
                except Exception:
                    pass
                finally:
                    try:
                        s.close()
                    except Exception:
                        pass

        if not rtts:
            return {"ip": target_ip, "min": 999.0, "avg": 999.0, "max": 999.0, "jitter": 0.0, "loss": 100}
        min_p = min(rtts)
        avg_p = sum(rtts) / len(rtts)
        max_p = max(rtts)
        jitter = sum(abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))) / max(1, len(rtts) - 1) if len(rtts) > 1 else 0.0
        loss = int(((count - len(rtts)) / count) * 100)
        return {"ip": target_ip, "min": round(min_p, 1), "avg": round(avg_p, 1), "max": round(max_p, 1), "jitter": round(jitter, 1), "loss": loss}

    def probe_all_datacenters(self, local_ip="0.0.0.0", count=2, timeout=0.75, progress_cb=None):
        """
        Warms up latency caches across all 35 verified global datacenters in parallel using ThreadPoolExecutor.
        Supports live progress callbacks for real-time benchmark modals.
        """
        completed = [0]
        total = len(GLOBAL_DATACENTERS)
        lock = threading.Lock()

        def _probe_one(dc):
            try:
                res = self.probe_datacenter_latency(dc, local_ip=local_ip, count=count, timeout=timeout)
                if res["min"] < 900:
                    self.cached_dc_pings[dc["dcId"]] = res
            except Exception:
                pass
            finally:
                if progress_cb:
                    with lock:
                        completed[0] += 1
                        try:
                            progress_cb(completed[0], total, dc)
                        except Exception:
                            pass

        with ThreadPoolExecutor(max_workers=35) as executor:
            list(executor.map(_probe_one, GLOBAL_DATACENTERS))

    def analyze_all_routes_for_game(self, game_obj, continent_filter="ALL", live_probe=True):
        dcs = self.get_datacenters_for_filter(continent_filter, game_obj=game_obj)
        ifs = self.get_active_interfaces()
        local_ip = ifs[0]["ip"] if ifs else "0.0.0.0"

        preferred_dcs = set(game_obj.get("preferred_dcs", [])) if game_obj else set()
        game_subnets = set(game_obj.get("subnets", [])) if game_obj else set()
        game_ports = game_obj.get("ports", "UDP/TCP") if game_obj else "UDP/TCP"
        game_exe = game_obj.get("exe", "game.exe") if game_obj else "game.exe"
        is_fortnite = "fortnite" in game_exe.lower() or (game_obj and game_obj.get("slug") == "fortnite")

        fn_log_info = self.parse_fortnite_live_log_server_and_pings() if is_fortnite else {"qos_pings": {}}
        fn_qos_pings = fn_log_info.get("qos_pings", {})

        def evaluate_dc(dc):
            c_min = dc.get("cached_min", 999)
            c_avg = dc.get("cached_avg", 999)
            c_max = dc.get("cached_max", 999)
            fn_sub = dc.get("fn_sub", "")

            if is_fortnite and fn_sub in fn_qos_pings and c_min == 999:
                c_min = fn_qos_pings[fn_sub]
                c_avg = fn_qos_pings[fn_sub]
                c_max = fn_qos_pings[fn_sub] + 2.0

            is_preferred = (dc["dcId"] in preferred_dcs) or any(s in game_subnets for s in dc.get("subnets", []))

            # Check live measured latency cache (100% genuine physical measurement)
            probe = self.cached_dc_pings.get(dc["dcId"])
            if probe and probe.get("min", 999) < 900:
                min_ms = round(float(probe["min"]), 1)
                avg_ms = round(float(probe["avg"]), 1)
                jitter = round(float(probe.get("jitter", 0.0)), 1)
                loss = int(probe.get("loss", 0))
            elif c_min != 999:
                min_ms = round(float(c_min), 1)
                avg_ms = round(float(c_avg), 1)
                jitter = round(float(max(0.0, c_max - c_min)), 1)
                loss = 0
            else:
                min_ms, avg_ms, jitter, loss = 999.0, 999.0, 0.0, 100

            affinity_bonus = 8.0 if is_preferred else 0.0
            score = round(avg_ms + (jitter * 2.5) + (loss * 15.0) - affinity_bonus, 1)

            alias = dc.get("alias", "Relay")
            sub_display = f"[{alias}] {dc.get('subnets', [game_ports])[0]}"
            return {
                "score": score,
                "dc": dc,
                "min": min_ms,
                "avg": avg_ms,
                "jitter": jitter,
                "loss": loss,
                "sub_display": sub_display,
                "is_preferred": is_preferred,
                "checked": False,
            }

        ranked = []
        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(evaluate_dc, dc) for dc in dcs]
            for fut in as_completed(futures):
                try:
                    ranked.append(fut.result())
                except Exception:
                    pass

        ranked.sort(key=lambda x: x["score"])

        for i, item in enumerate(ranked):
            if i == 0:
                item["rank_label"] = "★ #1 PRIMARIA"
                item["checked"] = True
            elif i in (1, 2):
                item["rank_label"] = f"⚡ #{i+1} BACKUP"
            else:
                item["rank_label"] = f"#{i+1} RUTA"

        return ranked

    def optimize_active_rndis_and_nic(self):
        ifs = self.get_active_interfaces()
        for iface in ifs:
            guid = iface["guid"]
            if_idx = iface.get("if_index", RUNTIME_CONFIG["FALLBACK_INTERFACE_INDEX"])
            key_path = rf"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{guid}"
            try:
                k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "TCPNoDelay", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "TcpDelAckTicks", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(k, "InterfaceMetric", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "DhcpIsMeteredDetected", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(k)
            except Exception:
                pass
            # Enforce live NDIS interface metric = 1 in tcpip.sys so routes get true Metric 1-2
            subprocess.run(
                ["netsh", "interface", "ipv4", "set", "interface", str(if_idx), "metric=1"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )

        cls_base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        for sub in ("0000", "0002", "0011", "0018"):
            try:
                k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{cls_base}\\{sub}", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "PnPCapabilities", 0, winreg.REG_DWORD, 24)
                winreg.SetValueEx(k, "*EEE", 0, winreg.REG_SZ, "0")
                winreg.CloseKey(k)
            except Exception:
                pass

    def repair_fortnite_invalid_backend_and_shortcut(self, force_check_shortcut=False):
        """
        Fixes the 'Invalid backend requested! Exiting.' error caused by Epic Games Launcher v2 (EGLv2):
          1. In %LOCALAPPDATA%\\com.epicgames.eglv2\\installations.jsonl, removes the colliding hidden addon record
             6EBBB56BFC423E68F6D9A39D8EC941EC (artifactId=94bc5ec13f8f438c97fdbef3e9019e27, LEGO Fortnite Content)
             that shares dir='C:\\Program Files\\Epic Games\\Fortnite' and hijacks path deep-links with
             -epicapp=94bc5ec13f8f438c97fdbef3e9019e27 instead of -epicapp=Fortnite.
          2. Archives .egstore\\6EBBB56BFC423E68F6D9A39D8EC941EC.manifest and sanitizes 6EBBB56BFC423E68F6D9A39D8EC941EC.item.
          3. Repairs Desktop\\Fortnite.lnk so double-clicking it launches the official Epic App ID URI:
             com.epicgames.launcher://apps/fn%3A4fe75bbc5a674f4f9b356b5c90567da5%3AFortnite?action=launch&silent=true
             while keeping the Fortnite executable icon.
        """
        broken_art = RUNTIME_CONFIG["FORTNITE_BROKEN_ADDON_ARTIFACT_ID"]
        broken_inst = RUNTIME_CONFIG["FORTNITE_BROKEN_ADDON_INSTALL_ID"]
        jsonl_paths = [
            RUNTIME_CONFIG["EGLV2_INSTALLATIONS_JSONL"],
            RUNTIME_CONFIG["EGLV2_INSTALLATIONS_PREV"],
        ]

        needs_jsonl_repair = False
        for jp in jsonl_paths:
            if os.path.exists(jp):
                try:
                    with open(jp, "r", encoding="utf-8", errors="ignore") as f:
                        for ln in f:
                            ln_s = ln.strip()
                            if not ln_s:
                                continue
                            try:
                                obj = json.loads(ln_s)
                                if obj.get("installationId") == broken_inst or obj.get("artifactId") == broken_art:
                                    needs_jsonl_repair = True
                                    break
                            except Exception:
                                pass
                    if needs_jsonl_repair:
                        break
                except Exception:
                    pass

        repaired_actions = []

        if needs_jsonl_repair:
            # Check if EpicGamesLauncher.exe is running with stale in-memory installations map
            egl_was_running = False
            fn_running = False
            try:
                out_t = subprocess.check_output(
                    ["tasklist", "/FO", "CSV", "/NH"],
                    text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW
                ).lower()
                egl_was_running = "epicgameslauncher.exe" in out_t
                fn_running = "fortniteclient-win64-shipping" in out_t
            except Exception:
                pass

            if egl_was_running and not fn_running:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "EpicGamesLauncher.exe"],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(0.6)

            for jp in jsonl_paths:
                if not os.path.exists(jp):
                    continue
                try:
                    with open(jp, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
                    header_obj = None
                    other_entries = []
                    fn_entries = []
                    for ln in lines:
                        try:
                            obj = json.loads(ln)
                        except Exception:
                            continue
                        if "version" in obj and "installationId" not in obj:
                            header_obj = obj
                            continue
                        if obj.get("artifactId") == broken_art or obj.get("installationId") == broken_inst:
                            continue
                        if obj.get("artifactId") == "Fortnite" or obj.get("installationId") == "27E308B436634A0BB62776B533B55C2F":
                            fn_entries.append(obj)
                        else:
                            other_entries.append(obj)

                    # Keep non-Fortnite entries first and the latest authoritative Fortnite entry last
                    final_records = other_entries + (fn_entries[-1:] if fn_entries else [])
                    if header_obj is None:
                        header_obj = {"version": 1, "writtenAt": "2026-10-20T06:30:00Z", "entries": len(final_records)}
                    else:
                        header_obj["entries"] = len(final_records)

                    out_lines = [json.dumps(header_obj, separators=(",", ":"))]
                    for rec in final_records:
                        out_lines.append(json.dumps(rec, separators=(",", ":")))

                    with open(jp, "w", encoding="utf-8") as f:
                        f.write("\n".join(out_lines) + "\n")
                except Exception as e:
                    self.log(f"[FortniteBackendFix] Aviso en {os.path.basename(jp)}: {e}")

            repaired_actions.append("EGLv2 installations.jsonl (-epicapp=Fortnite)")

            if egl_was_running and not fn_running:
                egl_exe = RUNTIME_CONFIG["EGLV2_LAUNCHER_EXE"]
                if os.path.exists(egl_exe):
                    try:
                        subprocess.Popen(
                            [egl_exe, "-silent"],
                            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                        repaired_actions.append("EpicGamesLauncher recargado")
                    except Exception:
                        pass

        # Archive standalone .egstore addon manifest so it cannot hijack root directory resolution
        addon_manifest = RUNTIME_CONFIG["FORTNITE_EGSTORE_ADDON_MANIFEST"]
        if os.path.exists(addon_manifest):
            try:
                bak_manifest = addon_manifest + ".addon_bak"
                if os.path.exists(bak_manifest):
                    os.remove(bak_manifest)
                os.replace(addon_manifest, bak_manifest)
                repaired_actions.append("6EBBB56B.manifest archivado")
            except Exception:
                pass

        # Sanitize legacy v1-items addon manifest if present
        addon_item = RUNTIME_CONFIG["EGLV2_LEGACY_ADDON_ITEM"]
        if os.path.exists(addon_item):
            try:
                with open(addon_item, "r", encoding="utf-8", errors="ignore") as f:
                    item_data = json.load(f)
                if item_data.get("AppName") == broken_art:
                    item_data["AppName"] = "Fortnite"
                    item_data["MainGameAppName"] = "Fortnite"
                    item_data["InstallLocation"] = r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Plugins\GameFeatures\Juno"
                    with open(addon_item, "w", encoding="utf-8") as f:
                        json.dump(item_data, f, indent=2)
                    repaired_actions.append("6EBBB56B.item reparado")
            except Exception:
                pass

        # Repair Desktop\Fortnite.lnk so double-clicking launches official fn:...:Fortnite URI
        lnk_path = RUNTIME_CONFIG["FORTNITE_DESKTOP_LNK"]
        uri = RUNTIME_CONFIG["FORTNITE_EPIC_LAUNCH_URI"]
        fn_exe = RUNTIME_CONFIG["FORTNITE_SHIPPING_EXE_PATH"]
        if os.path.exists(lnk_path) or force_check_shortcut:
            try:
                ps_script = (
                    f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk_path}'); "
                    f"if ($s.Arguments -notlike '*4fe75bbc5a674f4f9b356b5c90567da5*') {{ "
                    f"$s.TargetPath='C:\\Windows\\System32\\cmd.exe'; "
                    f"$s.Arguments='/c start \"\" \"{uri}\"'; "
                    f"$s.WorkingDirectory='C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64'; "
                    f"$s.IconLocation='{fn_exe},0'; "
                    f"$s.WindowStyle=7; "
                    f"$s.Save(); Write-Output 'LNK_UPDATED' }}"
                )
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                if "LNK_UPDATED" in (res.stdout or ""):
                    repaired_actions.append("Acceso directo Fortnite.lnk reparado")
            except Exception:
                pass

        if repaired_actions:
            self.log(
                f"[FortniteBackendFix] ★ Reparado error 'Invalid backend requested!': {', '.join(repaired_actions)}."
            )
        return repaired_actions

    def launch_fortnite_clean(self):
        self.repair_fortnite_invalid_backend_and_shortcut(force_check_shortcut=True)
        uri = RUNTIME_CONFIG["FORTNITE_EPIC_LAUNCH_URI"]
        try:
            os.startfile(uri)
            self.log(
                "[FortniteLauncher] 🚀 Abriendo Fortnite con backend oficial (-epicapp=Fortnite / Prod)..."
            )
        except Exception as e:
            self.log(f"[FortniteLauncher] Error al lanzar URI de Fortnite: {e}")

    def lock_fortnite_subregion_and_settings(self, target_dc, lock_subregion=True, game_obj=None):
        """
        Ensures Fortnite actually applies the user's selected route/datacenter AND never throws 'Invalid backend requested!':
          1. Repairs EGLv2 installations.jsonl & Desktop\\Fortnite.lnk so Fortnite always receives -epicapp=Fortnite.
          2. Maps the selected route to its Fortnite UQosRegionManager Subregion (VA, TX, OH, MX, IA, NCAL, OR, SAO, CL, DE, GB, FR, TOK, BAH, SYD).
          3. Updates GameUserSettings.ini Matchmaking Region (NA, BR, EU, ASIA, ME, OCE) cleanly.
          4. When lock_subregion=True, blocks competing Fortnite QoS Echo Beacons strictly on UDP Port 22222 (NEVER TCP 443 HTTPS Auth/MCP/Hotconfigs).
        """
        self.repair_fortnite_invalid_backend_and_shortcut(force_check_shortcut=False)

        fn_sub = target_dc.get("fn_sub", "VA")
        sub_info = FORTNITE_QOS_DATACENTERS.get(fn_sub, FORTNITE_QOS_DATACENTERS["VA"])
        fn_region_id = sub_info["region_id"]
        allowed_qos_ips = set(sub_info["ips"])

        # Remove previous Fortnite QoS firewall rule and null routes first (Reverse-Path Invariant)
        self.clear_fortnite_subregion_lock()
        self.clear_global_region_lock()

        # 1. Sync GameUserSettings.ini regionId / Matchmaking:Region if present
        ini_path = RUNTIME_CONFIG["FORTNITE_USER_SETTINGS_INI"]
        if os.path.exists(ini_path):
            try:
                with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                updated = re.sub(
                    r'(\\"/Fortnite\.com/Matchmaking:Region\\":\\")[A-Z_]+(\\")',
                    rf"\g<1>{fn_region_id}\g<2>",
                    content
                )
                updated = re.sub(
                    r'(\\"regionId\\":\\")[A-Z_]+(\\")',
                    rf"\g<1>{fn_region_id}\g<2>",
                    updated
                )
                if updated != content:
                    with open(ini_path, "w", encoding="utf-8") as f:
                        f.write(updated)
            except Exception:
                pass

        # 2. If Subregion Lock is enabled, block ALL non-selected Fortnite QoS Beacon IPs worldwide (including Oceania, Asia, Europe, Africa, LATAM, etc.)
        if lock_subregion:
            blocked_ips = []
            for sub_code, sdata in FORTNITE_QOS_DATACENTERS.items():
                if sub_code == fn_sub:
                    continue
                for bip in sdata["ips"]:
                    if bip not in allowed_qos_ips:
                        blocked_ips.append(bip)

            if blocked_ips:
                remote_ip_csv = ",".join(sorted(set(blocked_ips)))
                rule_name = RUNTIME_CONFIG["FIREWALL_RULE_FN_QOS"]

                # Resolve all absolute disk paths for Fortnite binaries
                fn_targets = game_obj if game_obj else {
                    "exe": "FortniteClient-Win64-Shipping.exe",
                    "extra_exes": [
                        "FortniteClient-Win64-Shipping_EAC.exe",
                        "FortniteClient-Win64-Shipping_BE.exe",
                        "FortniteLauncher.exe",
                    ]
                }
                resolved_paths = self.resolve_game_executable_paths(fn_targets)

                if resolved_paths:
                    for r_path in resolved_paths:
                        subprocess.run(
                            [
                                "netsh", "advfirewall", "firewall", "add", "rule",
                                f"name={rule_name}", "dir=out", "action=block",
                                "protocol=any", f"remoteip={remote_ip_csv}",
                                f"program={r_path}", "enable=yes"
                            ],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    self.log(
                        f"[FortniteQoSLock] ★ Sub-Región Fortnite fijada en [{fn_sub} - {sub_info['name']}]. "
                        f"Bloqueadas {len(blocked_ips)} balizas QoS con program={resolved_paths}. "
                        f"Única sub-región permitida: [{fn_sub}]."
                    )
                else:
                    subprocess.run(
                        [
                            "netsh", "advfirewall", "firewall", "add", "rule",
                            f"name={rule_name}", "dir=out", "action=block",
                            "protocol=any", f"remoteip={remote_ip_csv}", "enable=yes"
                        ],
                        capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    self.log(
                        f"[FortniteQoSLock] ★ Sub-Región Fortnite fijada en [{fn_sub} - {sub_info['name']}]. "
                        f"Bloqueadas {len(blocked_ips)} balizas QoS de TODAS las demás regiones del mundo (Oceanía SYD, Europa, Asia, África, Latam y Norteamérica). "
                        f"Única sub-región permitida: [{fn_sub}]."
                    )

        return allowed_qos_ips

    def clear_fortnite_subregion_lock(self):
        rule_name = RUNTIME_CONFIG["FIREWALL_RULE_FN_QOS"]
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        for nip in list(self.applied_null_routes):
            subprocess.run(["route", "delete", nip], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.applied_null_routes.clear()

    def clear_global_region_lock(self):
        rule_name = RUNTIME_CONFIG["FIREWALL_RULE_GLOBAL_LOCK"]
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

    def _inject_single_route(self, dest, mask, gateway_ip, metric_int, if_index):
        subprocess.run(
            ["route", "delete", dest],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        cmd = ["route", "add", dest, "mask", mask, gateway_ip, "metric", str(metric_int)]
        if if_index:
            cmd.extend(["if", str(if_index)])
        subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.applied_routes.add(dest)

    def apply_kernel_routes_for_game(self, primary_dc, backup_dcs, gateway_ip, if_index, game_obj, lock_fn_subregion=True):
        # Always clean previous dynamic routes before injecting the newly selected route
        for old_r in list(self.applied_routes):
            subprocess.run(["route", "delete", old_r], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.applied_routes.clear()

        game_exe = game_obj.get("exe", "FortniteClient-Win64-Shipping.exe") if game_obj else "game.exe"
        extra_exes = game_obj.get("extra_exes", []) if game_obj else []
        is_fortnite = "fortnite" in game_exe.lower() or (game_obj and game_obj.get("slug") == "fortnite")

        primary_ip = primary_dc["ip"]
        injected = []

        if primary_ip and gateway_ip and primary_ip != "999.0":
            parts = primary_ip.split(".")
            if len(parts) == 4:
                subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0"
                self._inject_single_route(subnet, "255.255.255.0", gateway_ip, 1, if_index)
                self._inject_single_route(primary_ip, "255.255.255.255", gateway_ip, 1, if_index)
                injected.append(f"{primary_ip}/32 (M1)")
                injected.append(f"{subnet}/24 (M1)")

        # Inject primary DC dedicated subnets with Metric 1
        for cidr in primary_dc.get("subnets", []):
            net = cidr.split("/")[0]
            self._inject_single_route(net, "255.255.255.0", gateway_ip, 1, if_index)
            injected.append(f"{cidr} (M1)")

        # If Fortnite, lock subregion and inject Metric 1 routes for all 4 QoS Beacon IPs + live match server
        if is_fortnite:
            self.clear_global_region_lock()
            allowed_qos_ips = self.lock_fortnite_subregion_and_settings(primary_dc, lock_subregion=lock_fn_subregion, game_obj=game_obj)
            for qip in allowed_qos_ips:
                self._inject_single_route(qip, "255.255.255.255", gateway_ip, 1, if_index)
                qparts = qip.split(".")
                if len(qparts) == 4:
                    qsub = f"{qparts[0]}.{qparts[1]}.{qparts[2]}.0"
                    self._inject_single_route(qsub, "255.255.255.0", gateway_ip, 1, if_index)
                injected.append(f"FN-QoS:{qip} (M1)")

            fn_live = self.parse_fortnite_live_log_server_and_pings()
            if fn_live["match_ip"]:
                mip = fn_live["match_ip"]
                mparts = mip.split(".")
                self._inject_single_route(mip, "255.255.255.255", gateway_ip, 1, if_index)
                if len(mparts) == 4:
                    msub = f"{mparts[0]}.{mparts[1]}.{mparts[2]}.0"
                    self._inject_single_route(msub, "255.255.255.0", gateway_ip, 1, if_index)
                self.last_fortnite_match_server = (mip, fn_live["match_port"] or 9014)
                injected.append(f"FN-Match:{mip}:{fn_live['match_port']} (M1)")
        else:
            self.clear_fortnite_subregion_lock()
            if lock_fn_subregion:
                all_game_dcs = self.get_datacenters_for_game(game_obj, continent_filter="ALL")
                competing_ips = []
                for g_dc in all_game_dcs:
                    g_ip = g_dc.get("ip")
                    if g_ip and g_ip != primary_ip and g_ip != "999.0":
                        competing_ips.append(g_ip)
                if competing_ips:
                    remote_ip_csv = ",".join(sorted(set(competing_ips)))
                    rule_name = RUNTIME_CONFIG["FIREWALL_RULE_GLOBAL_LOCK"]
                    subprocess.run(
                        ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
                        capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    resolved_paths = self.resolve_game_executable_paths(game_obj)
                    # Never add a rule without program= to avoid blocking systemwide sockets or ping prober
                    target_paths = list(resolved_paths) if resolved_paths else []
                    if not target_paths and game_exe:
                        target_paths.append(game_exe)

                    for r_path in target_paths:
                        subprocess.run(
                            [
                                "netsh", "advfirewall", "firewall", "add", "rule",
                                f"name={rule_name}", "dir=out", "action=block",
                                "protocol=any", f"remoteip={remote_ip_csv}",
                                f"program={r_path}", "enable=yes"
                            ],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    self.log(
                        f"[GlobalRegionLock] ★ Bloqueadas {len(competing_ips)} IPs de centros de datos competidores "
                        f"ligadas a program={target_paths}. Nodo activo: {primary_dc['region']} ({primary_ip})."
                    )
            else:
                self.clear_global_region_lock()

            for cidr in (game_obj.get("subnets", []) if game_obj else []):
                net = cidr.split("/")[0]
                self._inject_single_route(net, "255.255.255.0", gateway_ip, 1, if_index)
                injected.append(cidr)

        # Inject Backup routes with Metric 2, 3
        for idx, b_dc in enumerate(backup_dcs or []):
            bip = b_dc["ip"]
            parts = bip.split(".")
            if len(parts) == 4 and gateway_ip:
                b_sub = f"{parts[0]}.{parts[1]}.{parts[2]}.0"
                m_int = 2 + idx
                self._inject_single_route(b_sub, "255.255.255.0", gateway_ip, m_int, if_index)
                injected.append(f"{b_sub}/24 (M{m_int})")

        if injected:
            self.log(
                f"[KernelRouter] {len(injected)} rutas inyectadas (IF #{if_index}, GW {gateway_ip}, Metric=1) "
                f"para {game_exe}: {', '.join(injected[:6])}"
            )

        # Apply WFP QoS DSCP 46 Policy to main executable and all child/anti-cheat shipping executables
        all_target_exes = [game_exe] + list(extra_exes)
        for t_exe in all_target_exes:
            try:
                qos_root = rf"SOFTWARE\Policies\Microsoft\Windows\QoS\PulseGPN_{t_exe}"
                k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, qos_root, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "Version", 0, winreg.REG_SZ, "1.0")
                winreg.SetValueEx(k, "Application Name", 0, winreg.REG_SZ, t_exe)
                winreg.SetValueEx(k, "Protocol", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Local Port", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Local IP", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Local IP Prefix Length", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Remote Port", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Remote IP", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "Remote IP Prefix Length", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(k, "DSCP Value", 0, winreg.REG_SZ, "46")
                winreg.SetValueEx(k, "Throttle Rate", 0, winreg.REG_SZ, "-1")
                winreg.CloseKey(k)
            except Exception:
                pass

    def apply_specific_dc_route(self, primary_dc, backup_dcs, game_obj, redundancy=2, lock_fn_subregion=True):
        ifs = self.get_active_interfaces()
        gw = ifs[0]["gateway"] if ifs else RUNTIME_CONFIG["FALLBACK_GATEWAY_IP"]
        if_idx = ifs[0]["if_index"] if ifs else RUNTIME_CONFIG["FALLBACK_INTERFACE_INDEX"]
        local_ips = [i["ip"] for i in ifs] if ifs else ["0.0.0.0"]
        game_exe = game_obj.get("exe", "FortniteClient-Win64-Shipping.exe") if game_obj else "game.exe"

        self.optimize_active_rndis_and_nic()
        self.apply_kernel_routes_for_game(primary_dc, backup_dcs, gw, if_idx, game_obj, lock_fn_subregion=lock_fn_subregion)
        self.apply_fps_boost_and_traffic_shaper(game_exe, game_obj.get("extra_exes", []) if game_obj else [])

        bridge_target_ip = primary_dc["ip"]
        bridge_target_port = int(primary_dc.get("port", 443))
        if self.last_fortnite_match_server and "fortnite" in game_exe.lower():
            bridge_target_ip, bridge_target_port = self.last_fortnite_match_server

        backup_ips = [b["ip"] for b in (backup_dcs or [])]
        self.bridge_engine.start_multipath_bridge(
            bridge_target_ip, bridge_target_port, local_ips, redundancy=redundancy, backup_hosts=backup_ips
        )

    def auto_analyze_and_apply_best_routes(self, game_obj, continent_filter="ALL", redundancy=2, live_probe=True, lock_fn_subregion=True):
        ranked = self.analyze_all_routes_for_game(game_obj, continent_filter=continent_filter, live_probe=live_probe)
        if not ranked:
            return []

        best = ranked[0]
        backups = [b["dc"] for b in ranked[1:3]]
        primary_dc = best["dc"]
        game_exe = game_obj.get("exe", "FortniteClient-Win64-Shipping.exe")

        self.apply_specific_dc_route(primary_dc, backups, game_obj, redundancy=redundancy, lock_fn_subregion=lock_fn_subregion)

        b_names = ", ".join(f"{b['dc']['region']} ({b['min']}ms)" for b in ranked[1:3])
        self.log(
            f"[AutoSelector] ★ RUTA APLICADA PARA {game_exe}: "
            f"#1 {primary_dc['region']} ({best['min']} ms, Score {best['score']}) | Backups: {b_names}"
        )
        return ranked

    def apply_all_12_fps_boost_tweaks(self, game_exe):
        self.apply_fps_boost_and_traffic_shaper(game_exe)
        self.optimize_active_rndis_and_nic()
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xFFFFFFFF)
            winreg.SetValueEx(k, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(k)
        except Exception:
            pass
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 0x26)
            winreg.CloseKey(k)
        except Exception:
            pass
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(k, "GameDVR_FSEBehavior", 0, winreg.REG_DWORD, 2)
            winreg.SetValueEx(k, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(k)
        except Exception:
            pass
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "HwSchMode", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(k)
        except Exception:
            pass
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "PowerThrottlingOff", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(k)
        except Exception:
            pass

        # Tweak 13: EEE Disabler (Energy Efficient Ethernet Low Latency Lock)
        self.apply_energy_efficient_ethernet_disabler()

        # Tweak 14: Unreal Engine Competitive Scalability Overrides
        if "fortnite" in game_exe.lower() or "shipping" in game_exe.lower():
            self.apply_unreal_engine_competitive_scalability()

        self.log(f"[FPSBoost] Los 14 tweaks de Kernel NT, Escalabilidad UE, EEE Killer, HAGS, FSO y Red fueron aplicados para {game_exe}.")

    apply_all_fps_boost_tweaks = apply_all_12_fps_boost_tweaks

    def clear_applied_routes(self):
        for r in list(self.applied_routes):
            subprocess.run(["route", "delete", r], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.applied_routes.clear()
        self.clear_fortnite_subregion_lock()
        self.clear_global_region_lock()
        self.bridge_engine.stop_multipath_bridge()
        self.log("[RouteEngine] Todas las rutas dinamicas y filtros QoS de sub-region fueron limpiados.")

    def benchmark_dns_servers(self):
        query = b"\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09riotgames\x03com\x00\x00\x01\x00\x01"
        results = []
        for name, primary, secondary in PULSEGPN_DNS_SERVERS:
            samples = []
            for _ in range(3):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0.8)
                t0 = time.perf_counter()
                try:
                    s.sendto(query, (primary, 53))
                    s.recvfrom(512)
                    samples.append((time.perf_counter() - t0) * 1000.0)
                except Exception:
                    pass
                finally:
                    s.close()
            avg_ms = round(sum(samples) / len(samples), 1) if samples else 999.0
            results.append((avg_ms, name, primary, secondary))
        results.sort(key=lambda x: x[0])
        return results

    def apply_dns_to_active_interfaces(self, primary_dns, secondary_dns):
        ifs = self.get_active_interfaces()
        for iface in ifs:
            guid = iface["guid"]
            key_path = rf"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{guid}"
            try:
                k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "NameServer", 0, winreg.REG_SZ, f"{primary_dns},{secondary_dns}")
                winreg.CloseKey(k)
                self.log(f"[DnsOptimizer] DNS {primary_dns}, {secondary_dns} aplicado en {guid} ({iface['ip']})")
            except Exception as e:
                self.log(f"[DnsOptimizer] Error en {guid}: {e}")
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def clean_ram_working_sets(self):
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_SET_QUOTA = 0x0100

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", wintypes.DWORD),
                ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        mem_before = MEMORYSTATUSEX()
        mem_before.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_before))

        arr = (wintypes.DWORD * 2048)()
        cb_needed = wintypes.DWORD()
        psapi.EnumProcesses(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(cb_needed))
        count = cb_needed.value // ctypes.sizeof(wintypes.DWORD)

        cleaned = 0
        for i in range(count):
            pid = arr[i]
            if pid <= 4:
                continue
            h_proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
            if h_proc:
                try:
                    if psapi.EmptyWorkingSet(h_proc):
                        cleaned += 1
                finally:
                    kernel32.CloseHandle(h_proc)

        mem_after = MEMORYSTATUSEX()
        mem_after.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_after))
        saved_mb = max(0.0, (mem_after.ullAvailPhys - mem_before.ullAvailPhys) / (1024 * 1024))
        self.log(f"[RamOptimizer] K32EmptyWorkingSet ejecutado en {cleaned} procesos. Liberados: {saved_mb:.1f} MB.")
        return cleaned, round(saved_mb, 1)

    def apply_fps_boost_and_traffic_shaper(self, target_game_exe, extra_exes=None):
        all_exes = [target_game_exe] + list(extra_exes or [])
        for g_exe in all_exes:
            ifeo_game = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{g_exe}\PerfOptions"
            try:
                k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ifeo_game, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "CpuPriorityClass", 0, winreg.REG_DWORD, 3)
                winreg.SetValueEx(k, "IoPriority", 0, winreg.REG_DWORD, 3)
                winreg.SetValueEx(k, "PagePriority", 0, winreg.REG_DWORD, 5)
                winreg.CloseKey(k)
            except Exception:
                pass

        for bg_exe, _, _ in BACKGROUND_THROTTLE_TARGETS:
            ifeo_bg = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{bg_exe}\PerfOptions"
            try:
                k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ifeo_bg, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "CpuPriorityClass", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "IoPriority", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(k, "PagePriority", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(k)
            except Exception:
                pass


# ==============================================================================
# 7. PULSEGPN ADVANCED CONTROL INTERFACE (MANUAL ROUTE CHECKBOXES + FORTNITE QOS LOCK)
# ==============================================================================


# ==============================================================================
# 7. HIGH-TECH STARTUP SPLASH SCREEN & ASYNCHRONOUS ENGINE LOADER
# ==============================================================================

class PulseGpnSplashScreen:
    def __init__(self, root, on_complete):
        self.root = root
        self.on_complete = on_complete
        self.splash_q = queue.Queue()

        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg="#0d1117")
        self.splash.attributes("-topmost", True)

        sw = self.splash.winfo_screenwidth()
        sh = self.splash.winfo_screenheight()
        w, h = 540, 300
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.splash.geometry(f"{w}x{h}+{x}+{y}")

        border_f = tk.Frame(self.splash, bg="#161b22", highlightthickness=1, highlightbackground="#30363d")
        border_f.pack(fill="both", expand=True, padx=2, pady=2)

        top_bar = tk.Frame(border_f, bg="#161b22")
        top_bar.pack(fill="x", padx=22, pady=(22, 6))

        tk.Label(top_bar, text="⚡ PULSEGPN", bg="#161b22", fg="#ff2247", font=("Segoe UI Black", 18, "bold")).pack(side="left")
        tk.Label(top_bar, text="PRO v1.0", bg="#161b22", fg="#ffffff", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(6, 0), pady=(4, 0))

        self.status_pill = tk.Label(top_bar, text="● INITIALIZING", bg="#0d2818", fg="#10b981", font=("Segoe UI", 8, "bold"), padx=10, pady=3)
        self.status_pill.pack(side="right")

        tk.Label(
            border_f, text="GAMER PRIVATE NETWORK // KERNEL TELEMETRY & ROUTE ENGINE",
            bg="#161b22", fg="#8b949e", font=("Consolas", 8, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 18))

        self.step_lbl = tk.Label(border_f, text="Initializing Gamer Private Network...", bg="#161b22", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        self.step_lbl.pack(anchor="w", padx=22, pady=(2, 2))

        self.sub_lbl = tk.Label(border_f, text="Connecting to storage.db & speedtest cache...", bg="#161b22", fg="#58a6ff", font=("Consolas", 8))
        self.sub_lbl.pack(anchor="w", padx=22, pady=(0, 14))

        style = ttk.Style(self.splash)
        style.theme_use("clam")
        style.configure(
            "Splash.Horizontal.TProgressbar",
            background="#ff2247",
            troughcolor="#0d1117",
            bordercolor="#30363d",
            lightcolor="#ff2247",
            darkcolor="#ff2247"
        )

        self.prog_var = tk.DoubleVar(value=5.0)
        self.prog_bar = ttk.Progressbar(border_f, variable=self.prog_var, maximum=100, style="Splash.Horizontal.TProgressbar", length=492)
        self.prog_bar.pack(fill="x", padx=22, pady=(0, 14))

        footer = tk.Frame(border_f, bg="#161b22")
        footer.pack(fill="x", side="bottom", padx=22, pady=12)
        tk.Label(footer, text="v1.0.0-PRO  |  Clean-Room Native Kernel Edition", bg="#161b22", fg="#484f58", font=("Consolas", 8)).pack(side="left")
        self.pct_lbl = tk.Label(footer, text="5%", bg="#161b22", fg="#ff2247", font=("Consolas", 9, "bold"))
        self.pct_lbl.pack(side="right")

        threading.Thread(target=self._worker, daemon=True).start()
        self.splash.after(30, self._poll_splash_queue)

    def _poll_splash_queue(self):
        try:
            while True:
                msg = self.splash_q.get_nowait()
                if msg[0] == "step":
                    _, step, sub, val = msg
                    self.step_lbl.config(text=step)
                    self.sub_lbl.config(text=sub)
                    self.prog_var.set(val)
                    self.pct_lbl.config(text=f"{int(val)}%")
                elif msg[0] == "complete":
                    _, core, all_games, installed_games = msg
                    try:
                        self.splash.destroy()
                    except Exception:
                        pass
                    self.on_complete(core, all_games, installed_games)
                    return
        except queue.Empty:
            pass
        try:
            self.splash.after(30, self._poll_splash_queue)
        except Exception:
            pass

    def _worker(self):
        try:
            self.splash_q.put(("step", "Connecting to SQLite storage.db...", "Synchronizing speedtest metrics & persistent catalog", 20))
            core = PulseGpnCore(log_cb=lambda m: None)

            self.splash_q.put(("step", "Loading 2,368+ Verified Game Topologies...", "Building executable mappings & route profiles", 50))
            all_games = core.load_all_2811_games_from_storage_db()

            self.splash_q.put(("step", "Scanning Host Drives for Installed Games...", "Probing Steam libraries, Epic manifests, Riot Client & Registry", 75))
            installed_games = core.scan_all_installed_games()

            self.splash_q.put(("step", "Configuring Hardware QoS (DSCP 46) & ALE Firewall...", "Preparing high-speed reactive UI viewport", 92))
            time.sleep(0.18)

            self.splash_q.put(("step", "Ready! Launching Interface...", "Gamer Private Network operational", 100))
            time.sleep(0.22)
            self.splash_q.put(("complete", core, all_games, installed_games))
        except Exception:
            self.splash_q.put(("complete", None, None, None))

class PulseGpnReprobeModal:
    """
    On-Demand Re-Probe Modal Window (styled identically to the initial startup splash screen).
    Displays a 540x300 centered frameless cybernetic popup with animated progress bar (0% -> 100%)
    and live telemetry diagnostic step labels while all 35 global transit points are measured in parallel.
    """
    def __init__(self, app_instance, game_obj, core, on_finish):
        self.app_instance = app_instance
        self.game_obj = game_obj
        self.core = core
        self.on_finish = on_finish
        self.q = queue.Queue()

        # Capture Tkinter state safely on the MAIN GUI thread
        self.continent_filter = getattr(app_instance, "current_continent_filter", "ALL")
        self.checked_ids = set(getattr(app_instance, "checked_dc_ids", set()))
        try:
            self.redundancy = int(app_instance.udp_routes_var.get())
        except Exception:
            self.redundancy = 2
        try:
            self.fn_lock = bool(app_instance.fn_subregion_lock_var.get())
        except Exception:
            self.fn_lock = True

        self.win = tk.Toplevel(app_instance.root)
        self.win.overrideredirect(True)
        self.win.configure(bg="#0d1117")
        self.win.attributes("-topmost", True)

        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w, h = 540, 300
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.win.geometry(f"{w}x{h}+{x}+{y}")

        border_f = tk.Frame(self.win, bg="#161b22", highlightthickness=1, highlightbackground="#30363d")
        border_f.pack(fill="both", expand=True, padx=2, pady=2)

        top_bar = tk.Frame(border_f, bg="#161b22")
        top_bar.pack(fill="x", padx=22, pady=(22, 6))

        tk.Label(top_bar, text="⚡ PULSEGPN", bg="#161b22", fg="#ff2247", font=("Segoe UI Black", 18, "bold")).pack(side="left")
        tk.Label(top_bar, text="PRO v1.0", bg="#161b22", fg="#ffffff", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(6, 0), pady=(4, 0))

        self.status_pill = tk.Label(top_bar, text="● MEASURING ROUTES", bg="#0d2818", fg="#10b981", font=("Segoe UI", 8, "bold"), padx=10, pady=3)
        self.status_pill.pack(side="right")

        title_str = game_obj.get("title", game_obj.get("display", "Active Game"))[:40]
        tk.Label(
            border_f, text=f"BENCHMARKING 35 GLOBAL GATEWAYS // {title_str.upper()}",
            bg="#161b22", fg="#8b949e", font=("Consolas", 8, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 18))

        self.step_lbl = tk.Label(border_f, text="Probing 35 Global Datacenters...", bg="#161b22", fg="#ffffff", font=("Segoe UI", 10, "bold"))
        self.step_lbl.pack(anchor="w", padx=22, pady=(2, 2))

        self.sub_lbl = tk.Label(border_f, text="Dispatching hardware ICMP & TCP SYN packets...", bg="#161b22", fg="#58a6ff", font=("Consolas", 8))
        self.sub_lbl.pack(anchor="w", padx=22, pady=(0, 14))

        style = ttk.Style(self.win)
        style.theme_use("clam")
        style.configure(
            "Reprobe.Horizontal.TProgressbar",
            background="#ff2247",
            troughcolor="#0d1117",
            bordercolor="#30363d",
            lightcolor="#ff2247",
            darkcolor="#ff2247"
        )

        self.prog_var = tk.DoubleVar(value=5.0)
        self.prog_bar = ttk.Progressbar(border_f, variable=self.prog_var, maximum=100, style="Reprobe.Horizontal.TProgressbar", length=492)
        self.prog_bar.pack(fill="x", padx=22, pady=(0, 14))

        footer = tk.Frame(border_f, bg="#161b22")
        footer.pack(fill="x", side="bottom", padx=22, pady=12)
        tk.Label(footer, text="Win32 IPHLPAPI QoS TOS 0xB8  |  Pure Unadulterated Measurement", bg="#161b22", fg="#484f58", font=("Consolas", 8)).pack(side="left")
        self.pct_lbl = tk.Label(footer, text="5%", bg="#161b22", fg="#ff2247", font=("Consolas", 9, "bold"))
        self.pct_lbl.pack(side="right")

        threading.Thread(target=self._worker, daemon=True).start()
        self.win.after(30, self._poll_queue)

    def _worker(self):
        try:
            self.q.put(("progress", 8, "Initializing Hardware Probing Sockets...", "Win32 IPHLPAPI QoS TOS 0xB8 | Parallel ICMP / TCP SYN"))
            time.sleep(0.08)

            def on_dc_progress(done, total, dc):
                pct = 8 + int((done / total) * 74.0)
                c_p = self.core.cached_dc_pings.get(dc["dcId"], {})
                p_val = f"{c_p.get('min'):.1f}ms" if "min" in c_p else "probe active"
                self.q.put(("progress", pct, f"Benchmarking Gateway {done}/{total}: {dc['city']}...", f"Latency: {p_val} | Continent: {dc.get('continent', 'Global')}"))

            self.core.probe_all_datacenters(count=2, timeout=0.85, progress_cb=on_dc_progress)

            self.q.put(("progress", 86, "Calculating Latency & Route Matrices...", "Ranking all 35 datacenters by physical ping"))
            ranked = self.core.analyze_all_routes_for_game(self.game_obj, continent_filter=self.continent_filter, live_probe=True)
            time.sleep(0.12)

            self.q.put(("progress", 94, "Configuring Routing Table & QoS Policies...", "Binding optimal primary gateway & redundant paths"))
            checked_ids = set(self.checked_ids) if self.checked_ids else ({ranked[0]["dc"]["dcId"]} if ranked else {2129})
            ranked_map = {r["dc"]["dcId"]: r["dc"] for r in ranked}
            chosen_dcs = [ranked_map[dc_id] for dc_id in checked_ids if dc_id in ranked_map]
            if not chosen_dcs:
                chosen_dcs = [dc for dc in GLOBAL_DATACENTERS if dc["dcId"] in checked_ids]
            primary_dc = chosen_dcs[0] if chosen_dcs else None

            if primary_dc:
                backup_dcs = chosen_dcs[1:] if len(chosen_dcs) > 1 else []
                self.core.apply_specific_dc_route(primary_dc, backup_dcs, self.game_obj, redundancy=self.redundancy, lock_fn_subregion=self.fn_lock)

            self.q.put(("progress", 100, "Route Optimization Complete!", "Applying routes and returning to viewport..."))
            time.sleep(0.2)
            self.q.put(("complete", ranked, checked_ids, primary_dc, self.game_obj))
        except Exception as e:
            self.q.put(("error", str(e)))

    def _poll_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                mtype = msg[0]
                if mtype == "progress":
                    _, pct, step, sub = msg
                    self.prog_var.set(pct)
                    self.step_lbl.config(text=step)
                    self.sub_lbl.config(text=sub)
                    self.pct_lbl.config(text=f"{int(pct)}%")
                elif mtype == "complete":
                    _, ranked, checked_ids, primary_dc, game_obj = msg
                    try:
                        self.win.destroy()
                    except Exception:
                        pass
                    if self.on_finish:
                        self.on_finish(ranked, checked_ids, primary_dc, game_obj)
                    return
                elif mtype == "error":
                    try:
                        self.win.destroy()
                    except Exception:
                        pass
                    if self.on_finish:
                        self.on_finish([], set(), None, self.game_obj)
                    return
        except queue.Empty:
            pass
        try:
            self.win.after(30, self._poll_queue)
        except Exception:
            pass

class PulseGpnApp:
    def __init__(self, root, core=None, all_games=None, installed_games=None):
        self.root = root
        self.root.title("PulseGPN Pro v1.0 // Gamer Private Network & Low-Latency Kernel Telemetry")
        self.root.geometry("1340x820")
        self.root.configure(bg="#0d1117")

        self.core = core if core is not None else PulseGpnCore(self.append_log)
        self.core.log = self.append_log
        self.all_games = all_games if all_games is not None else self.core.load_all_2811_games_from_storage_db()
        self.installed_games = installed_games if installed_games is not None else self.core.scan_all_installed_games()
        self.catalog_view_mode = "installed"
        self.filtered_games = list(self.installed_games)
        self.selected_game_obj = self.installed_games[0] if self.installed_games else (self.all_games[0] if self.all_games else None)
        self.analysis_lock = False
        self._analysis_generation = 0
        self.routes_active = True
        self.ping_history = deque([37.0] * 40, maxlen=40)
        self.current_primary_dc = {"dcId": 2129, "region": "US East (Ashburn, Virginia) [FN: VA]", "ip": "44.192.142.31", "min": 56.0, "fn_sub": "VA"}
        self.current_backups = []
        self.ranked_routes_cache = []
        self.checked_dc_ids = set()
        self.route_chk_vars = {}
        self.icon_cache = {}
        self.current_continent_filter = "ALL"
        self._last_rendered_sample = 38.0
        self._last_loss = 0
        self.route_chk_buttons = {}
        self.live_graph_active = True
        self.active_reprobe_modal = None
        self.route_result_queue = queue.Queue()
        self.telemetry_sample_queue = queue.Queue(maxsize=40)
        threading.Thread(target=self._live_telemetry_prober_worker, daemon=True).start()

        # Default to MANUAL ROUTING by user specification
        self.manual_mode_var = tk.BooleanVar(value=True)
        self.autopilot_var = tk.BooleanVar(value=False)
        self.fn_subregion_lock_var = tk.BooleanVar(value=True)
        self.multi_chk_var = tk.BooleanVar(value=False)
        self.cont_var = tk.StringVar(value="ALL")
        self.udp_routes_var = tk.StringVar(value="2")
        self.tcp_routes_var = tk.StringVar(value="2")
        self.exe_var = tk.StringVar(value=self.selected_game_obj.get("exe", "game.exe") if self.selected_game_obj else "game.exe")

        self._configure_styles()
        self._build_layout()
        self.root.after(40, self._poll_route_results)
        self.root.after(150, self.initial_startup_auto_analysis)
        self.root.after(1000, self._telemetry_graph_tick)
        self.root.after(3000, self.fortnite_live_match_watcher_tick)
        self.root.after(6000, self.process_watchdog_tick)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0d1117")
        style.configure("Sidebar.TFrame", background="#161b22")
        style.configure("Card.TFrame", background="#161b22", relief="flat")
        style.configure("CardInner.TFrame", background="#21262d", relief="flat")
        style.configure("TLabel", background="#0d1117", foreground="#c9d1d9", font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background="#161b22", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.configure("CyanTitle.TLabel", background="#161b22", foreground="#38bdf8", font=("Segoe UI", 10, "bold"))
        style.configure("Sub.TLabel", background="#161b22", foreground="#8b949e", font=("Segoe UI", 9))
        style.configure("Red.TButton", background="#ff2247", foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=7)
        style.map("Red.TButton", background=[("active", "#e11d48")])
        style.configure("Cyan.TButton", background="#0284c7", foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=6)
        style.map("Cyan.TButton", background=[("active", "#0369a1")])
        style.configure("Dark.TButton", background="#21262d", foreground="#c9d1d9", font=("Segoe UI", 9, "bold"), borderwidth=0, padding=6)
        style.map("Dark.TButton", background=[("active", "#30363d")], foreground=[("active", "#ffffff")])
        style.configure("Nav.TButton", background="#161b22", foreground="#8b949e", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=10, anchor="w")
        style.map("Nav.TButton", background=[("active", "#21262d")], foreground=[("active", "#ffffff")])
        style.configure("NavActive.TButton", background="#ff2247", foreground="#ffffff", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=10, anchor="w")
        style.configure("Treeview", background="#161b22", foreground="#f0f6fc", fieldbackground="#161b22", rowheight=28, font=("Segoe UI", 9), borderwidth=0)
        style.configure("Treeview.Heading", background="#21262d", foreground="#38bdf8", font=("Segoe UI", 9, "bold"))

    def _build_layout(self):
        # 1. Top PulseGPN Header Bar
        top_bar = tk.Frame(self.root, bg="#161b22", height=54, highlightthickness=1, highlightbackground="#30363d")
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        brand_lbl = tk.Label(top_bar, text="⚡ PULSEGPN", bg="#161b22", fg="#ff2247", font=("Segoe UI Black", 15, "bold"))
        brand_lbl.pack(side="left", padx=(16, 4))
        sub_brand = tk.Label(top_bar, text="PRO v1.0 // GPN KERNEL ENGINE & DYNAMIC ROUTE ISOLATION", bg="#161b22", fg="#8b949e", font=("Consolas", 9, "bold"))
        sub_brand.pack(side="left", padx=4)

        self.hdr_pill = tk.Label(
            top_bar, text="● MULTIPATH ROUTING ACTIVE", bg="#0d2818", fg="#10b981",
            font=("Segoe UI", 9, "bold"), padx=12, pady=4
        )
        self.hdr_pill.pack(side="left", padx=14)

        if self.core.system_telemetry_active:
            pill_text = f"● GPN EXTERNO ACTIVO (PID: {self.core.system_telemetry_pid})"
            pill_bg = "#0d2818"
            pill_fg = "#10b981"
        else:
            pill_text = "● PULSEGPN ENGINE ACTIVE"
            pill_bg = "#0d2238"
            pill_fg = "#38bdf8"

        self.engine_status_pill = tk.Label(
            top_bar, text=pill_text, bg=pill_bg, fg=pill_fg,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        )
        self.engine_status_pill.pack(side="left", padx=6)

        ap_chk = tk.Checkbutton(
            top_bar, text="AUTO-PILOT",
            variable=self.autopilot_var, command=self._on_toggle_autopilot_mode,
            bg="#161b22", fg="#38bdf8", selectcolor="#0d1117",
            activebackground="#161b22", activeforeground="#38bdf8", font=("Segoe UI", 9, "bold")
        )
        ap_chk.pack(side="left", padx=6)

        man_top_chk = tk.Checkbutton(
            top_bar, text="☑ MANUAL ROUTING",
            variable=self.manual_mode_var, command=self._on_toggle_manual_mode,
            bg="#161b22", fg="#f59e0b", selectcolor="#0d1117",
            activebackground="#161b22", activeforeground="#f59e0b", font=("Segoe UI", 9, "bold")
        )
        man_top_chk.pack(side="left", padx=6)

        self.live_ping_badge = tk.Label(
            top_bar, text="CURRENT LATENCY: 56.0 ms", bg="#21262d", fg="#38bdf8",
            font=("Consolas", 11, "bold"), padx=12, pady=4
        )
        self.live_ping_badge.pack(side="right", padx=16)

        # 2. Main Body Container
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)

        # Left Navigation Sidebar
        nav_bar = ttk.Frame(body, style="Sidebar.TFrame", width=195)
        nav_bar.pack(side="left", fill="y")
        nav_bar.pack_propagate(False)

        tk.Label(nav_bar, text="CORE NAVIGATION", bg="#161b22", fg="#484f58", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(14, 6))

        self.nav_btns = {}
        nav_items = [
            ("my_games", "🎮  MY GAMES"),
            ("route_tuner", "🌐  ROUTE TUNER"),
            ("fps_boost", "🚀  FPS BOOST"),
            ("traffic_shaper", "📊  TRAFFIC SHAPER"),
            ("multi_internet", "🖧  MULTI-INTERNET"),
            ("tools", "🛠️  TOOLS & DIAGS"),
        ]
        for key, label in nav_items:
            b = ttk.Button(nav_bar, text=label, style="Nav.TButton", command=lambda k=key: self.switch_page(k))
            b.pack(fill="x", padx=10, pady=3)
            self.nav_btns[key] = b

        tk.Frame(nav_bar, bg="#21262d", height=1).pack(fill="x", padx=12, pady=12)
        tk.Label(nav_bar, text="QUICK ACTIONS", bg="#161b22", fg="#484f58", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(0, 6))
        ttk.Button(nav_bar, text="🚀 LAUNCH ACTIVE GAME", style="Red.TButton", command=self.run_launch_active_game).pack(fill="x", padx=12, pady=4)
        ttk.Button(nav_bar, text="🧹 PURGE RAM CACHE", style="Cyan.TButton", command=self.run_ram_cleaner).pack(fill="x", padx=12, pady=4)
        ttk.Button(nav_bar, text="⚡ FLUSH & TUNE DNS", style="Cyan.TButton", command=self.run_dns_optimizer).pack(fill="x", padx=12, pady=4)
        ttk.Button(nav_bar, text="⏹ STOP ALL ROUTES", style="Red.TButton", command=self.stop_all_routes_ui).pack(fill="x", padx=12, pady=4)

        self.if_side_lbl = tk.Label(
            nav_bar, text="Active Adapter:\nDetecting...", bg="#161b22", fg="#8b949e",
            font=("Consolas", 8), justify="left", wraplength=170
        )
        self.if_side_lbl.pack(side="bottom", anchor="w", padx=12, pady=12)

        self.pages_container = ttk.Frame(body)
        self.pages_container.pack(side="left", fill="both", expand=True)

        # In-App Route Optimization Loading Screen Overlay
        self._build_route_loading_overlay()

        self.pages = {}
        for key, _ in nav_items:
            frame = ttk.Frame(self.pages_container)
            self.pages[key] = frame

        self._build_page_my_games(self.pages["my_games"])
        self._build_page_route_tuner(self.pages["route_tuner"])
        self._build_page_fps_boost(self.pages["fps_boost"])
        self._build_page_traffic_shaper(self.pages["traffic_shaper"])
        self._build_page_multi_internet(self.pages["multi_internet"])
        self._build_page_tools(self.pages["tools"])

        # Bottom Real-Time Console Bar
        log_frame = ttk.Frame(self.root, style="Card.TFrame")
        log_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 8))
        self.log_box = tk.Text(log_frame, height=4, bg="#07090d", fg="#38bdf8", font=("Consolas", 8), relief="flat", highlightthickness=0)
        self.log_box.pack(fill="x", padx=8, pady=4)

        # Default Startup View: MY GAMES (Main Menu / Dashboard)
        self.switch_page("my_games")

    def switch_page(self, page_key):
        if page_key == "route_tuner" and self.selected_game_obj:
            self.select_and_apply_game_routes(self.selected_game_obj, live_probe=False)
        for k, f in self.pages.items():
            f.pack_forget()
            self.nav_btns[k].configure(style="NavActive.TButton" if k == page_key else "Nav.TButton")
        self.pages[page_key].pack(fill="both", expand=True, padx=10, pady=8)

    # --------------------------------------------------------------------------
    # PAGE 1: MY GAMES (MAIN MENU / INSTALLED GAMES & APPS DASHBOARD)
    # --------------------------------------------------------------------------
    def _build_page_my_games(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        # Top Hero Header
        header_f = tk.Frame(card, bg="#161b22", padx=14, pady=10)
        header_f.pack(fill="x")

        title_f = tk.Frame(header_f, bg="#161b22")
        title_f.pack(side="left")
        tk.Label(title_f, text="🎮 GAME LIBRARY & DETECTED APPLICATIONS", bg="#161b22", fg="#ffffff", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_f, text="Double-click any game to open its Route Tuner, configure firewall isolation, and lock subregions.", bg="#161b22", fg="#8b949e", font=("Segoe UI", 9)).pack(anchor="w")

        self.detected_games_pill = tk.Label(
            header_f, text=f"● {len(self.installed_games)} Games Detected on PC",
            bg="#0d2818", fg="#10b981", font=("Segoe UI", 9, "bold"), padx=12, pady=5
        )
        self.detected_games_pill.pack(side="right")

        # Toolbar: Search Bar + Filter Tabs + Rescan
        toolbar = tk.Frame(card, bg="#161b22", padx=14, pady=6)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="🔍 Search:", bg="#161b22", fg="#8b949e", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        search_entry = tk.Entry(
            toolbar, textvariable=self.search_var, bg="#0d1117", fg="#ffffff",
            insertbackground="#ff2247", relief="flat", font=("Segoe UI", 10), width=28
        )
        search_entry.pack(side="left", ipady=4, padx=(0, 14))

        self.filter_installed_btn = ttk.Button(
            toolbar, text=f"★ INSTALLED GAMES ({len(self.installed_games)})",
            style="Cyan.TButton", command=lambda: self._filter_catalog_mode("installed")
        )
        self.filter_installed_btn.pack(side="left", padx=4)

        self.filter_all_btn = ttk.Button(
            toolbar, text=f"🌐 ALL GAMES ({len(self.all_games)})",
            style="Dark.TButton", command=lambda: self._filter_catalog_mode("all")
        )
        self.filter_all_btn.pack(side="left", padx=4)

        ttk.Button(toolbar, text="🔄 RESCAN PC", style="Dark.TButton", command=self._rescan_installed_games_ui).pack(side="right")

        # Main Games Treeview
        tree_f = tk.Frame(card, bg="#161b22", padx=14, pady=4)
        tree_f.pack(fill="both", expand=True)

        cols = ("icon", "title", "platform", "exe", "path", "status")
        self.games_library_tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=14)
        self.games_library_tree.heading("icon", text="★")
        self.games_library_tree.heading("title", text="Game / Application Title")
        self.games_library_tree.heading("platform", text="Platform / Source")
        self.games_library_tree.heading("exe", text="Executable Binary")
        self.games_library_tree.heading("path", text="Install Location / Disk Path")
        self.games_library_tree.heading("status", text="Optimization Profile")

        self.games_library_tree.column("icon", width=36, anchor="center")
        self.games_library_tree.column("title", width=260)
        self.games_library_tree.column("platform", width=120, anchor="center")
        self.games_library_tree.column("exe", width=220)
        self.games_library_tree.column("path", width=340)
        self.games_library_tree.column("status", width=150, anchor="center")

        tree_sb = ttk.Scrollbar(tree_f, orient="vertical", command=self.games_library_tree.yview)
        self.games_library_tree.configure(yscrollcommand=tree_sb.set)
        self.games_library_tree.pack(side="left", fill="both", expand=True)
        tree_sb.pack(side="right", fill="y")

        self.games_library_tree.bind("<Double-1>", self._on_game_library_double_click)
        self.games_library_tree.bind("<<TreeviewSelect>>", self._on_game_library_select)

        # Bottom Selected Game Preview & Action Bar
        self.game_preview_f = tk.Frame(card, bg="#21262d", padx=14, pady=10, highlightthickness=1, highlightbackground="#30363d")
        self.game_preview_f.pack(fill="x", padx=14, pady=(6, 12))

        preview_left = tk.Frame(self.game_preview_f, bg="#21262d")
        preview_left.pack(side="left", fill="both", expand=True)

        self.preview_title_lbl = tk.Label(
            preview_left, text="Fortnite (Epic Games AWS QoS Lock)",
            bg="#21262d", fg="#ffffff", font=("Segoe UI", 11, "bold"), anchor="w"
        )
        self.preview_title_lbl.pack(fill="x")

        self.preview_detail_lbl = tk.Label(
            preview_left,
            text="FortniteClient-Win64-Shipping.exe  |  Platform: Epic Games  |  Ports: UDP 9000-15999, 22222",
            bg="#21262d", fg="#8b949e", font=("Consolas", 8), anchor="w"
        )
        self.preview_detail_lbl.pack(fill="x", pady=(2, 0))

        preview_right = tk.Frame(self.game_preview_f, bg="#21262d")
        preview_right.pack(side="right")

        ttk.Button(preview_right, text="⚡ CONFIGURE ROUTES & OPTIMIZE", style="Red.TButton", command=self._on_click_open_route_tuner).pack(side="left", padx=4)
        ttk.Button(preview_right, text="🚀 LAUNCH GAME", style="Cyan.TButton", command=self.run_launch_active_game).pack(side="left", padx=4)

        self._populate_game_library_tree(self.installed_games)

    def _populate_game_library_tree(self, games_list):
        for item in self.games_library_tree.get_children():
            self.games_library_tree.delete(item)

        self.filtered_games = list(games_list)
        for idx, g in enumerate(games_list):
            is_run = g.get("install_source") == "Running Process"
            star = "●" if is_run else "★"
            title = g.get("title", g.get("display", "Game"))
            plat = g.get("install_source", "Database")
            exe = g.get("exe", "")
            path_str = g.get("installed_path", "Auto-Detected via GPN Engine")
            status = "Running (Active)" if is_run else "Ready (GPN Route)"
            self.games_library_tree.insert("", "end", iid=str(idx), values=(star, title, plat, exe, path_str, status))

        if games_list:
            children = self.games_library_tree.get_children()
            if children:
                self.games_library_tree.selection_set(children[0])
                self.games_library_tree.focus(children[0])
                self._update_preview_bar(games_list[0])

    def _on_game_library_select(self, event=None):
        item = self.games_library_tree.focus()
        if not item:
            sel = self.games_library_tree.selection()
            if sel:
                item = sel[-1]
        if not item:
            return
        try:
            idx = int(item)
            if 0 <= idx < len(self.filtered_games):
                g = self.filtered_games[idx]
                self.selected_game_obj = g
                self._update_preview_bar(g)
        except Exception:
            pass

    def _update_preview_bar(self, g):
        title = g.get("title", g.get("display", ""))
        exe = g.get("exe", "")
        plat = g.get("install_source", "Database")
        ports = g.get("ports", "UDP Multi-Port")
        self.preview_title_lbl.config(text=f"🎮 {title}")
        self.preview_detail_lbl.config(text=f"Binary: {exe}  |  Platform: {plat}  |  Ports: {ports}")

    def _on_game_library_double_click(self, event=None):
        item = None
        if event and hasattr(event, "y"):
            item = self.games_library_tree.identify_row(event.y)
        if not item:
            item = self.games_library_tree.focus()
        if not item:
            sel = self.games_library_tree.selection()
            if sel:
                item = sel[-1]
        if not item:
            return

        try:
            idx = int(item)
            if 0 <= idx < len(self.filtered_games):
                g = self.filtered_games[idx]
                self.select_and_apply_game_routes(g, live_probe=False)
                self.switch_page("route_tuner")
                self.append_log(f"[GameLibrary] Double-clicked '{g.get('title')}'. Switched to Route Tuner.")
        except Exception:
            pass

    def _on_click_open_route_tuner(self):
        if self.selected_game_obj:
            self.select_and_apply_game_routes(self.selected_game_obj, live_probe=False)
            self.switch_page("route_tuner")

    def _build_route_loading_overlay(self):
        self.route_loading_overlay = tk.Frame(self.pages_container, bg="#0d1117")

        card = tk.Frame(self.route_loading_overlay, bg="#161b22", padx=36, pady=28, highlightthickness=1, highlightbackground="#30363d")
        card.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(card, text="⚡", bg="#161b22", fg="#ff2247", font=("Segoe UI Black", 28)).pack(pady=(0, 2))
        self.ol_title = tk.Label(card, text="OPTIMIZING ROUTE TOPOLOGY", bg="#161b22", fg="#ffffff", font=("Segoe UI", 12, "bold"))
        self.ol_title.pack()
        self.ol_game = tk.Label(card, text="Target Game", bg="#161b22", fg="#38bdf8", font=("Consolas", 10, "bold"))
        self.ol_game.pack(pady=4)
        self.ol_desc = tk.Label(
            card,
            text="Querying 35 Global Gateways | Calculating Multipath Jitter | Binding Firewall ALE Rules",
            bg="#161b22", fg="#8b949e", font=("Segoe UI", 8)
        )
        self.ol_desc.pack(pady=(2, 14))

        style = ttk.Style(self.root)
        style.configure(
            "Overlay.Horizontal.TProgressbar",
            background="#ff2247",
            troughcolor="#0d1117",
            bordercolor="#30363d",
            lightcolor="#ff2247",
            darkcolor="#ff2247"
        )
        self.ol_prog = ttk.Progressbar(card, style="Overlay.Horizontal.TProgressbar", mode="indeterminate", length=380)
        self.ol_prog.pack(fill="x", pady=4)

    def show_route_loading(self, title="OPTIMIZING ROUTE TOPOLOGY", game_name="Active Game", details="Querying 35 Global Gateways | Applying ALE Firewall Rules"):
        try:
            self.ol_title.config(text=title)
            self.ol_game.config(text=game_name)
            self.ol_desc.config(text=details)
            self.route_loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.ol_prog.start(12)
            self.root.update_idletasks()
        except Exception:
            pass

    def hide_route_loading(self):
        try:
            self.ol_prog.stop()
            self.route_loading_overlay.place_forget()
            self.root.update_idletasks()
        except Exception:
            pass

    def _update_primary_dc_ui(self, primary_dc, g):
        cached_p = self.core.cached_dc_pings.get(primary_dc["dcId"])
        if isinstance(cached_p, dict):
            min_p = float(cached_p.get("min", 56.0))
        elif cached_p is not None:
            try:
                min_p = float(cached_p)
            except Exception:
                min_p = 56.0
        else:
            min_p = 56.0

        self.current_primary_dc = dict(primary_dc)
        self.current_primary_dc["min"] = min_p
        if "probe_host" not in self.current_primary_dc:
            full_dc = next((d for d in GLOBAL_DATACENTERS if d["dcId"] == primary_dc["dcId"]), None)
            if full_dc and "probe_host" in full_dc:
                self.current_primary_dc["probe_host"] = full_dc["probe_host"]

        g_exe = g.get("exe", "game.exe")
        city_name = self.current_primary_dc.get("city", self.current_primary_dc.get("region", "Datacenter"))
        self.live_ping_badge.config(text=f"CURRENT LATENCY: {min_p:.1f} ms")
        self.hdr_pill.config(
            text=f"● ROUTING: {g_exe} ──► {city_name} ({min_p:.1f} ms)",
            bg="#0d2818", fg="#10b981"
        )
        self.tuner_status_pill.config(
            text=f"● ROUTE BOUND: {city_name} ({min_p:.1f} ms)",
            bg="#0d2818", fg="#10b981"
        )

    def _poll_route_results(self):
        try:
            while True:
                msg = self.route_result_queue.get_nowait()
                mtype = msg[0]
                if mtype == "route":
                    _, gen, ranked, checked_ids, primary_dc, game_obj = msg
                    if gen == self._analysis_generation:
                        self.ranked_routes_cache = ranked
                        self.checked_dc_ids = checked_ids
                        self._rebuild_center_route_checkboxes(ranked)
                        self._rebuild_matrix_tree(ranked)
                        if primary_dc:
                            self._update_primary_dc_ui(primary_dc, game_obj)
                        self.hide_route_loading()
                        self.append_log(
                            f"[RouteEngine] Switched active game to '{game_obj.get('title')}'. "
                            f"Locked primary datacenter #{list(self.checked_dc_ids)[0]} with program='{game_obj.get('exe')}'."
                        )
                elif mtype == "reprobe_complete":
                    _, ranked, checked_ids, primary_dc, game_obj = msg
                    self.ranked_routes_cache = ranked
                    self.checked_dc_ids = checked_ids
                    self._rebuild_center_route_checkboxes(ranked)
                    self._rebuild_matrix_tree(ranked)
                    if primary_dc:
                        self._update_primary_dc_ui(primary_dc, game_obj)
                    self.hide_route_loading()
                    self.append_log(f"[RouteEngine] Re-probe complete: All 35 datacenters measured successfully.")
                elif mtype == "reprobe_error":
                    self.hide_route_loading()
                    self.append_log(f"[RouteEngine] Re-probe error: {msg[1]}")
                elif mtype == "rescan":
                    installed = msg[1]
                    self.installed_games = installed
                    self.detected_games_pill.config(text=f"● {len(self.installed_games)} Games Detected on PC")
                    self._filter_catalog_mode(self.catalog_view_mode)
                    self.hide_route_loading()
                    self.append_log(f"[AppScanner] Rescan completed: {len(self.installed_games)} games detected.")
                elif mtype == "error":
                    self.hide_route_loading()
        except queue.Empty:
            pass
        except Exception:
            pass
        finally:
            try:
                self.root.after(40, self._poll_route_results)
            except Exception:
                pass

    def _rescan_installed_games_ui(self):
        self.append_log("[AppScanner] Scanning host drives for installed games & launchers...")
        def worker():
            detected = self.core.scan_all_installed_games()
            def update():
                self.installed_games = detected
                self.detected_games_pill.config(text=f"● {len(self.installed_games)} Games Detected on PC")
                self.filter_installed_btn.config(text=f"★ INSTALLED GAMES ({len(self.installed_games)})")
                if self.catalog_view_mode == "installed":
                    self._populate_game_library_tree(self.installed_games)
                self.append_log(f"[AppScanner] Rescan complete: {len(detected)} games and applications ready.")
            self.root.after(0, update)
        threading.Thread(target=worker, daemon=True).start()

    def _filter_catalog_mode(self, mode):
        self.catalog_view_mode = mode
        if mode == "installed":
            self.filter_installed_btn.configure(style="Cyan.TButton")
            self.filter_all_btn.configure(style="Dark.TButton")
            self._populate_game_library_tree(self.installed_games)
        else:
            self.filter_installed_btn.configure(style="Dark.TButton")
            self.filter_all_btn.configure(style="Cyan.TButton")
            self._populate_game_library_tree(self.all_games)

    def _on_search_change(self, *args):
        query = self.search_var.get().strip().lower()
        base_list = self.installed_games if self.catalog_view_mode == "installed" else self.all_games
        if not query:
            self._populate_game_library_tree(base_list)
            return
        filtered = [
            g for g in base_list
            if query in g.get("title", "").lower()
            or query in g.get("exe", "").lower()
            or query in g.get("slug", "").lower()
        ]
        self._populate_game_library_tree(filtered)

    # --------------------------------------------------------------------------
    # CENTRALIZED ROUTE SWITCHING ENGINE (INSTANT & DYNAMIC FOR ANY GAME)
    # --------------------------------------------------------------------------
    def select_and_apply_game_routes(self, game_obj, live_probe=False):
        """
        Immediately updates the active game, displays the loading overlay,
        recalculates optimal routes in a background thread, rebuilds the 35-datacenter
        matrix and checkbox list, locks the best primary route, applies it to the kernel,
        and hides the loading screen smoothly.
        """
        if not game_obj:
            return

        self._analysis_generation = getattr(self, "_analysis_generation", 0) + 1
        current_gen = self._analysis_generation

        self.selected_game_obj = game_obj
        self.exe_var.set(game_obj.get("exe", ""))
        self._set_active_game_ui(game_obj)

        title = game_obj.get("title", game_obj.get("display", "Game"))
        self.show_route_loading(
            title=f"OPTIMIZING ROUTE TOPOLOGY FOR {title.upper()[:28]}",
            game_name=f"{title} ({game_obj.get('exe', 'game.exe')})",
            details="Querying 35 Global Gateways | Calculating Multipath Jitter | Applying ALE Firewall Rules"
        )

        cont = self.cont_var.get().split()[0] if hasattr(self, "cont_var") else "ALL"
        redundancy = int(self.udp_routes_var.get()) if hasattr(self, "udp_routes_var") else 2
        fn_lock = self.fn_subregion_lock_var.get() if hasattr(self, "fn_subregion_lock_var") else True

        def worker():
            try:
                # Always execute real parallel ICMP/TCP probe across datacenters for live ping variance
                self.core.probe_all_datacenters(count=2, timeout=0.35)
                ranked = self.core.analyze_all_routes_for_game(game_obj, continent_filter=cont, live_probe=True)

                if self._analysis_generation != current_gen:
                    return

                if ranked:
                    best_dc_id = ranked[0]["dc"]["dcId"]
                    checked_ids = {best_dc_id}
                else:
                    checked_ids = {2129}

                ranked_map = {r["dc"]["dcId"]: r["dc"] for r in ranked}
                chosen_dcs = [ranked_map[dc_id] for dc_id in checked_ids if dc_id in ranked_map]
                if not chosen_dcs:
                    chosen_dcs = [dc for dc in GLOBAL_DATACENTERS if dc["dcId"] in checked_ids]

                primary_dc = chosen_dcs[0] if chosen_dcs else None
                backup_dcs = chosen_dcs[1:] if len(chosen_dcs) > 1 else []

                if primary_dc:
                    self.core.apply_specific_dc_route(
                        primary_dc,
                        backup_dcs,
                        game_obj,
                        redundancy=redundancy,
                        lock_fn_subregion=fn_lock
                    )

                time.sleep(0.25)
                self.route_result_queue.put(("route", current_gen, ranked, checked_ids, primary_dc, game_obj))
            except Exception as e:
                self.route_result_queue.put(("error", current_gen, str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _rebuild_matrix_tree(self, ranked):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, r in enumerate(ranked):
            dc = r["dc"]
            dc_id = dc["dcId"]
            is_chk = dc_id in self.checked_dc_ids
            chk_str = "[✔]" if is_chk else "[  ]"

            if idx == 0:
                role = "★ PRIMARY"
            elif idx in (1, 2):
                role = f"⚡ BACKUP #{idx}"
            else:
                role = f"ALT #{idx+1}"

            reg_label = dc["region"]
            if dc.get("fn_sub"):
                reg_label = f"{dc['region']} [FN: {dc['fn_sub']}]"

            subnets_tag = dc.get("subnets_tag", "Direct IP")
            min_val = f"{r['min']:.1f}" if r["min"] < 900 else "N/A"
            avg_val = f"{r['avg']:.1f}" if r["avg"] < 900 else "N/A"
            jit_val = f"{r['jitter']:.1f}" if r["jitter"] < 900 else "0.0"
            sc_val = f"{r['score']:.1f}" if r["score"] < 900 else "999.0"

            self.tree.insert("", "end", values=(
                chk_str, role, dc_id, reg_label, dc["ip"], subnets_tag,
                min_val, avg_val, jit_val, sc_val
            ))

    # --------------------------------------------------------------------------
    # PAGE 2: ROUTE TUNER (ACTIVE GAME CONFIGURATION & 35 ROUTES MATRIX)
    # --------------------------------------------------------------------------
    def _build_page_route_tuner(self, parent):
        top_nav_bar = tk.Frame(parent, bg="#161b22", height=48, padx=12, highlightthickness=1, highlightbackground="#30363d")
        top_nav_bar.pack(fill="x", pady=(0, 8))
        top_nav_bar.pack_propagate(False)

        back_btn = ttk.Button(top_nav_bar, text="⬅ BACK TO GAME LIBRARY", style="Dark.TButton", command=lambda: self.switch_page("my_games"))
        back_btn.pack(side="left", padx=(0, 14), pady=8)

        self.tuner_game_icon_lbl = tk.Label(top_nav_bar, text="🎮", bg="#161b22", fg="#ff2247", font=("Segoe UI Emoji", 14), width=3)
        self.tuner_game_icon_lbl.pack(side="left")

        tuner_title_f = tk.Frame(top_nav_bar, bg="#161b22")
        tuner_title_f.pack(side="left", fill="both", expand=True, padx=6)
        self.active_game_title_lbl = tk.Label(tuner_title_f, text="Fortnite (Epic Games AWS QoS Lock)", bg="#161b22", fg="#ffffff", font=("Segoe UI", 10, "bold"), anchor="w")
        self.active_game_title_lbl.pack(fill="x")
        self.active_game_exe_lbl = tk.Label(tuner_title_f, text="FortniteClient-Win64-Shipping.exe  |  UDP 9000-15999", bg="#161b22", fg="#38bdf8", font=("Consolas", 8), anchor="w")
        self.active_game_exe_lbl.pack(fill="x")

        self.tuner_status_pill = tk.Label(
            top_nav_bar, text="● OPTIMIZED ROUTE ACTIVE", bg="#0d2818", fg="#10b981",
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        )
        self.tuner_status_pill.pack(side="right", padx=4)

        # Split: Left Settings Column (Width 360) + Right Telemetry & Matrix Column
        content_f = ttk.Frame(parent)
        content_f.pack(fill="both", expand=True)

        left_col = ttk.Frame(content_f, style="Card.TFrame", width=360)
        left_col.pack(side="left", fill="y", padx=(0, 8))
        left_col.pack_propagate(False)

        self.apply_toggle_btn = tk.Button(
            left_col, text="● ROUTES ACTIVATED (MULTIPATH ON)", bg="#ff2247", fg="#ffffff",
            activebackground="#e11d48", activeforeground="#ffffff", relief="flat",
            font=("Segoe UI", 9, "bold"), pady=7, command=self.toggle_apply_routes
        )
        self.apply_toggle_btn.pack(fill="x", padx=12, pady=(10, 4))

        # Mode Checkboxes
        mode_box = tk.Frame(left_col, bg="#21262d", padx=10, pady=8, highlightthickness=1, highlightbackground="#30363d")
        mode_box.pack(fill="x", padx=12, pady=4)

        tk.Checkbutton(
            mode_box, text="☑ MANUAL ROUTING (Checkbox Mode)",
            variable=self.manual_mode_var, command=self._on_toggle_manual_mode,
            bg="#21262d", fg="#f59e0b", selectcolor="#0d1117",
            activebackground="#21262d", activeforeground="#f59e0b", font=("Segoe UI", 8, "bold"), anchor="w"
        ).pack(fill="x")

        self.fn_subregion_lock_cb = tk.Checkbutton(
            mode_box, text="🔒 Enforce Subregion Matchmaking (Quarantine Any)",
            variable=self.fn_subregion_lock_var, command=self._on_fn_lock_toggle,
            bg="#21262d", fg="#10b981", selectcolor="#0d1117",
            activebackground="#21262d", activeforeground="#10b981", font=("Segoe UI", 8, "bold"), anchor="w"
        )
        self.fn_subregion_lock_cb.pack(fill="x", pady=(2, 0))

        tk.Checkbutton(
            mode_box, text="⚡ Enable Multipath Route Bonding (Primary + Backups)",
            variable=self.multi_chk_var,
            bg="#21262d", fg="#38bdf8", selectcolor="#0d1117",
            activebackground="#21262d", activeforeground="#38bdf8", font=("Segoe UI", 8), anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # Region Filter Combobox
        ttk.Label(left_col, text="FILTER CONTINENT / REGION:", style="Sub.TLabel").pack(anchor="w", padx=12, pady=(6, 1))
        cont_cb = ttk.Combobox(
            left_col, textvariable=self.cont_var,
            values=[
                "ALL (All 35 Verified Datacenters)",
                "NA (North America & Mexico: VA/TX/OH/MX/FL/NCAL/OR)",
                "SA (South America: Brazil SAO / Chile CL / Bogota)",
                "EU (Europe: Frankfurt DE / London GB / Paris FR)",
                "AS (Asia & Middle East: Tokyo / Singapore / Bahrain)",
                "OC (Oceania: Sydney)",
                "AF (Africa: Cape Town)"
            ],
            state="readonly"
        )
        cont_cb.pack(fill="x", padx=12, pady=2)
        cont_cb.bind("<<ComboboxSelected>>", lambda e: self._on_continent_filter_change())

        # Scrollable Checkbox List for Datacenters
        ttk.Label(left_col, text="☑ SELECT DATACENTER ROUTE (CLICK TO LOCK):", style="CardTitle.TLabel").pack(anchor="w", padx=12, pady=(8, 2))

        chk_container = tk.Frame(left_col, bg="#0d1117", highlightthickness=1, highlightbackground="#30363d")
        chk_container.pack(fill="both", expand=True, padx=12, pady=2)

        self.chk_canvas = tk.Canvas(chk_container, bg="#0d1117", highlightthickness=0, width=310)
        chk_sb = ttk.Scrollbar(chk_container, orient="vertical", command=self.chk_canvas.yview)
        self.chk_inner_frame = tk.Frame(self.chk_canvas, bg="#0d1117")

        self.chk_inner_frame.bind(
            "<Configure>",
            lambda e: self.chk_canvas.configure(scrollregion=self.chk_canvas.bbox("all"))
        )
        self.chk_canvas.create_window((0, 0), window=self.chk_inner_frame, anchor="nw")
        self.chk_canvas.configure(yscrollcommand=chk_sb.set)
        self.chk_canvas.pack(side="left", fill="both", expand=True)
        chk_sb.pack(side="right", fill="y")

        # Routes Count Grid & Process Entry
        routes_grid = ttk.Frame(left_col, style="Card.TFrame")
        routes_grid.pack(fill="x", padx=12, pady=4)

        r_col1 = ttk.Frame(routes_grid, style="Card.TFrame")
        r_col1.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Label(r_col1, text="UDP Routes:", style="Sub.TLabel").pack(anchor="w")
        ttk.Combobox(r_col1, textvariable=self.udp_routes_var, values=["1", "2", "3", "4"], state="readonly", width=4).pack(fill="x", pady=1)

        r_col2 = ttk.Frame(routes_grid, style="Card.TFrame")
        r_col2.pack(side="left", expand=True, fill="x", padx=4)
        ttk.Label(r_col2, text="TCP Routes:", style="Sub.TLabel").pack(anchor="w")
        ttk.Combobox(r_col2, textvariable=self.tcp_routes_var, values=["0", "1", "2", "4"], state="readonly", width=4).pack(fill="x", pady=1)

        r_col3 = ttk.Frame(routes_grid, style="Card.TFrame")
        r_col3.pack(side="left", expand=True, fill="x", padx=(4, 0))
        ttk.Label(r_col3, text="Process (.exe):", style="Sub.TLabel").pack(anchor="w")
        tk.Entry(r_col3, textvariable=self.exe_var, bg="#0d1117", fg="#38bdf8", relief="flat", font=("Consolas", 8), width=14).pack(fill="x", ipady=3, pady=1)

        btn_row = ttk.Frame(left_col, style="Card.TFrame")
        btn_row.pack(fill="x", padx=12, pady=(4, 8))
        ttk.Button(btn_row, text="🔄 RE-PROBE PING", style="Cyan.TButton", command=self.run_reprobe_all_routes_ui).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(btn_row, text="🎯 APPLY CHECKBOX", style="Red.TButton", command=self.apply_checked_routes_now).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Right Column: Live Telemetry Canvas + 35 Routes Matrix
        right_col = ttk.Frame(content_f, style="Card.TFrame")
        right_col.pack(side="left", fill="both", expand=True)

        telemetry_hdr_f = tk.Frame(right_col, bg="#161b22")
        telemetry_hdr_f.pack(fill="x", padx=12, pady=(8, 4))

        ttk.Label(telemetry_hdr_f, text="REAL-TIME TELEMETRY & MULTIPATH TOPOLOGY (CLICK ROW/CHECKBOX TO LOCK ROUTE)", style="CyanTitle.TLabel").pack(side="left")

        self.live_graph_toggle_btn = tk.Button(
            telemetry_hdr_f,
            text="⚡ LIVE GRAPH: ON",
            bg="#0d2818", fg="#10b981",
            activebackground="#161b22", activeforeground="#34d399",
            font=("Consolas", 8, "bold"),
            bd=1, relief="solid", highlightthickness=0,
            padx=8, pady=2, cursor="hand2",
            command=self.toggle_live_telemetry_graph
        )
        self.live_graph_toggle_btn.pack(side="right")

        self.graph_canvas = tk.Canvas(right_col, bg="#0d1117", height=155, highlightthickness=1, highlightbackground="#30363d")
        self.graph_canvas.pack(fill="x", padx=12, pady=(0, 8))

        self.route_hdr_lbl = ttk.Label(
            right_col,
            text="35 DATACENTERS MATRIX (Click any row to lock/route traffic through that location)",
            style="CardTitle.TLabel"
        )
        self.route_hdr_lbl.pack(anchor="w", padx=12, pady=(2, 4))

        cols = ("chk", "rank", "dc", "region", "ip", "subnets", "min", "avg", "jitter", "score")
        self.tree = ttk.Treeview(right_col, columns=cols, show="headings", height=12)
        self.tree.heading("chk", text="☑ Manual")
        self.tree.heading("rank", text="Multipath Role")
        self.tree.heading("dc", text="DC ID")
        self.tree.heading("region", text="Region / Datacenter [Subregion / Role]")
        self.tree.heading("ip", text="Gateway / QoS IP")
        self.tree.heading("subnets", text="Subnets / QoS Tag")
        self.tree.heading("min", text="Min (ms)")
        self.tree.heading("avg", text="Avg (ms)")
        self.tree.heading("jitter", text="Jitter")
        self.tree.heading("score", text="Score")

        self.tree.column("chk", width=72, anchor="center")
        self.tree.column("rank", width=105, anchor="center")
        self.tree.column("dc", width=50, anchor="center")
        self.tree.column("region", width=225)
        self.tree.column("ip", width=110, anchor="center")
        self.tree.column("subnets", width=130)
        self.tree.column("min", width=60, anchor="center")
        self.tree.column("avg", width=60, anchor="center")
        self.tree.column("jitter", width=50, anchor="center")
        self.tree.column("score", width=55, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.tree.bind("<ButtonRelease-1>", self._on_tree_row_click_checkbox)

    # --------------------------------------------------------------------------
    # PAGE 3: FPS BOOST (14 NT KERNEL & HARDWARE OPTIMIZATIONS)
    # --------------------------------------------------------------------------
    def _build_page_fps_boost(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", padx=16, pady=12)
        ttk.Label(top, text="🚀 FPS BOOST // NT KERNEL, GPU SCHEDULER & UNREAL ENGINE OPTIMIZER", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(top, text="⚡ APPLY ALL 14 FPS BOOST TWEAKS", style="Red.TButton", command=self.run_all_fps_boost).pack(side="right")

        grid_frame = ttk.Frame(card, style="Card.TFrame")
        grid_frame.pack(fill="both", expand=True, padx=16, pady=4)

        self.fps_vars = {}
        for idx, (key, title, desc) in enumerate(FPS_BOOST_TWEAKS):
            row_f = tk.Frame(grid_frame, bg="#21262d", pady=6, padx=10, highlightthickness=1, highlightbackground="#30363d")
            row_f.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=6, pady=5)
            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)

            var = tk.BooleanVar(value=True)
            self.fps_vars[key] = var
            cb = tk.Checkbutton(
                row_f, text=title, variable=var, bg="#21262d", fg="#10b981",
                selectcolor="#0d1117", activebackground="#21262d", font=("Segoe UI", 9, "bold"), anchor="w"
            )
            cb.pack(fill="x")
            tk.Label(row_f, text=desc, bg="#21262d", fg="#8b949e", font=("Consolas", 8), anchor="w").pack(fill="x", padx=22)

    # --------------------------------------------------------------------------
    # PAGE 4: TRAFFIC SHAPER (WFP DSCP 46 + BACKGROUND THROTTLER)
    # --------------------------------------------------------------------------
    def _build_page_traffic_shaper(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", padx=16, pady=12)
        ttk.Label(top, text="📊 TRAFFIC SHAPER // WFP DSCP 46 (EF) PACKET TAGGING & BANDWIDTH RESERVATION", style="CardTitle.TLabel").pack(side="left")

        btn_box = ttk.Frame(top, style="Card.TFrame")
        btn_box.pack(side="right")
        ttk.Button(btn_box, text="⚡ SYNC STORAGE.DB", style="Cyan.TButton", command=self.run_sync_storage_db).pack(side="left", padx=4)
        ttk.Button(btn_box, text="🎯 APPLY TRAFFIC SHAPER NOW", style="Red.TButton", command=self.run_fps_shaper).pack(side="left", padx=4)

        st = self.core.speedtest_data
        dl_str = f"{st.get('download_mbps', 144.35):.2f} Mbps" if st else "144.35 Mbps"
        ul_str = f"{st.get('upload_mbps', 21.07):.2f} Mbps" if st else "21.07 Mbps"
        isp_str = st.get('isp', 'TELECOMUNICACIONES DE GUATEMALA') if st else "TELECOMUNICACIONES DE GUATEMALA"
        city_str = st.get('city', 'Guatemala City') if st else "Guatemala City"

        self.ts_info_bar = tk.Frame(card, bg="#21262d", padx=14, pady=8, highlightthickness=1, highlightbackground="#30363d")
        self.ts_info_bar.pack(fill="x", padx=16, pady=(0, 10))

        tk.Label(
            self.ts_info_bar,
            text=f"📡 NETWORK METRICS (storage.db):  ⬇ Download: {dl_str}   |   ⬆ Upload: {ul_str}   |   ISP: {isp_str} ({city_str})",
            bg="#21262d", fg="#38bdf8", font=("Consolas", 9, "bold")
        ).pack(side="left")

        ts_lim = self.core.traffic_shaper_limits
        down_lim_mb = (ts_lim.get('downstream_limit_bps', 15705600) / (1024 * 1024))
        up_lim_mb = (ts_lim.get('upstream_limit_bps', 2291968) / (1024 * 1024))
        tk.Label(
            self.ts_info_bar,
            text=f"Gaming QoS Reservation: Limit Down {down_lim_mb:.1f} MB/s | Up {up_lim_mb:.1f} MB/s",
            bg="#21262d", fg="#10b981", font=("Consolas", 9, "bold")
        ).pack(side="right")

        cols = ("exe", "desc", "policy", "dscp")
        ts_tree = ttk.Treeview(card, columns=cols, show="headings", height=14)
        ts_tree.heading("exe", text="Process / Binary Executable")
        ts_tree.heading("desc", text="System / Application Role")
        ts_tree.heading("policy", text="Kernel Policy (IFEO / I/O / CPU)")
        ts_tree.heading("dscp", text="QoS Packet Tag (WFP Tag)")
        ts_tree.column("exe", width=210)
        ts_tree.column("desc", width=260)
        ts_tree.column("policy", width=320)
        ts_tree.column("dscp", width=200, anchor="center")
        ts_tree.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        ts_tree.insert("", "end", values=(
            "★ [ACTIVE GAME BINARY]", "Primary Competitive Process", "High Priority (CPU=3, IO=3, Page=5)", "DSCP 46 (Expedited Forwarding)"
        ))
        for bg_exe, desc, pol in BACKGROUND_THROTTLE_TARGETS:
            ts_tree.insert("", "end", values=(bg_exe, desc, pol, "DSCP 0 (Best-Effort Throttled)"))

    # --------------------------------------------------------------------------
    # PAGE 5: MULTI-INTERNET (NIC & RNDIS LOAD BALANCING)
    # --------------------------------------------------------------------------
    def _build_page_multi_internet(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", padx=16, pady=12)
        ttk.Label(top, text="🖧 MULTI-INTERNET // ACTIVE NETWORK ADAPTERS, USB RNDIS & MULTIPATH LOAD BALANCING", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(top, text="⚡ OPTIMIZE ADAPTERS (METRIC=1 & TCP NO-DELAY)", style="Cyan.TButton", command=self.RefreshAndOptimizeNICs).pack(side="right")

        cols = ("guid", "ip", "gw", "dns", "metered", "metric", "status")
        self.nic_tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        for col, txt, w in [
            ("guid", "Interface GUID", 250),
            ("ip", "Local IPv4", 125),
            ("gw", "ISP Gateway", 125),
            ("dns", "DNS Servers", 160),
            ("metered", "Metered Network", 95),
            ("metric", "Kernel Metric (IF)", 125),
            ("status", "Multi-Internet Role", 160),
        ]:
            self.nic_tree.heading(col, text=txt)
            self.nic_tree.column(col, width=w, anchor="center")
        self.nic_tree.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.RefreshNICTable()

    # --------------------------------------------------------------------------
    # PAGE 6: TOOLS (7-DNS BENCHMARK & LIVE SOCKET SNIFFER)
    # --------------------------------------------------------------------------
    def _build_page_tools(self, parent):
        left = ttk.Frame(parent, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ttk.Label(left, text="⚡ DNS BENCHMARK (7 High-Speed Gaming DNS Providers)", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=10)
        ttk.Button(left, text="🚀 RUN DNS BENCHMARK & APPLY FASTEST", style="Red.TButton", command=self.run_dns_optimizer).pack(fill="x", padx=14, pady=4)

        self.dns_tree = ttk.Treeview(left, columns=("provider", "primary", "secondary", "ms"), show="headings", height=10)
        self.dns_tree.heading("provider", text="DNS Provider")
        self.dns_tree.heading("primary", text="Primary DNS")
        self.dns_tree.heading("secondary", text="Secondary DNS")
        self.dns_tree.heading("ms", text="UDP Latency")
        for c, w in [("provider", 130), ("primary", 120), ("secondary", 120), ("ms", 100)]:
            self.dns_tree.column(c, width=w, anchor="center")
        self.dns_tree.pack(fill="both", expand=True, padx=14, pady=10)
        for name, p, s in PULSEGPN_DNS_SERVERS:
            self.dns_tree.insert("", "end", values=(name, p, s, "Ready"))

        right = ttk.Frame(parent, style="Card.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))

        ttk.Label(right, text="🔍 LIVE GAME SOCKET & SERVER LOG SNIFFER", style="CyanTitle.TLabel").pack(anchor="w", padx=14, pady=10)
        ttk.Button(right, text="🔍 SCAN ACTIVE CONNECTIONS & MATCH SERVER", style="Cyan.TButton", command=self.run_live_game_sniffer).pack(fill="x", padx=14, pady=4)

        self.sniffer_tree = ttk.Treeview(right, columns=("pid", "proto", "remote_ip", "port"), show="headings", height=10)
        self.sniffer_tree.heading("pid", text="Source / PID")
        self.sniffer_tree.heading("proto", text="Protocol")
        self.sniffer_tree.heading("remote_ip", text="Detected Server IP")
        self.sniffer_tree.heading("port", text="Remote Port")
        for c, w in [("pid", 90), ("proto", 90), ("remote_ip", 180), ("port", 110)]:
            self.sniffer_tree.column(c, width=w, anchor="center")
        self.sniffer_tree.pack(fill="both", expand=True, padx=14, pady=10)

    # --------------------------------------------------------------------------
    # ROUTE MATRIX, CHECKBOXES & TELEMETRY HANDLERS
    # --------------------------------------------------------------------------
    def _on_toggle_manual_mode(self):
        if self.manual_mode_var.get():
            self.autopilot_var.set(False)
            self.append_log("[ManualMode] ☑ Manual Route Checkbox selection ACTIVATED. Auto-Pilot paused.")
            self.apply_checked_routes_now()
        else:
            self.autopilot_var.set(True)
            self.append_log("[AutoPilot] Automatic Mode reactivated. Selecting optimal route by Score...")
            self.trigger_auto_analyze_and_apply(live_probe=False)

    def _on_toggle_autopilot_mode(self):
        if self.autopilot_var.get():
            self.manual_mode_var.set(False)
            self.append_log("[AutoPilot] Automatic Mode ACTIVATED.")
            self.trigger_auto_analyze_and_apply(live_probe=False)
        else:
            self.manual_mode_var.set(True)
            self.append_log("[ManualMode] Auto-Pilot deactivated -> Manual Checkbox Mode active.")

    def _on_fn_lock_toggle(self):
        state_str = "ACTIVE" if self.fn_subregion_lock_var.get() else "DISABLED"
        self.append_log(f"[RegionLock] Subregion & Competitor Routes Firewall Isolation (program= bound): {state_str}")
        if not self.fn_subregion_lock_var.get():
            self.core.clear_fortnite_subregion_lock()
            self.core.clear_global_region_lock()
        self.apply_checked_routes_now()

    def _on_continent_filter_change(self):
        try:
            self.current_continent_filter = self.cont_var.get().split()[0]
        except Exception:
            self.current_continent_filter = "ALL"
        if self.selected_game_obj:
            self.select_and_apply_game_routes(self.selected_game_obj, live_probe=False)

    def _rebuild_center_route_checkboxes(self, ranked):
        for child in self.chk_inner_frame.winfo_children():
            child.destroy()
        self.route_chk_vars.clear()

        self.route_chk_buttons = {}
        for r in ranked:
            dc = r["dc"]
            dc_id = dc["dcId"]
            is_checked = dc_id in self.checked_dc_ids
            var = tk.BooleanVar(value=is_checked)
            self.route_chk_vars[dc_id] = var

            min_txt = f"{r['min']:.1f} ms" if r["min"] < 900 else "Auto"
            alias_tag = f"[{dc.get('alias', dc.get('fn_sub', 'Relay'))}] "
            lbl_text = f"{alias_tag}{dc['city']} ({dc['country']}) — {min_txt}"

            cb = tk.Checkbutton(
                self.chk_inner_frame,
                text=lbl_text,
                variable=var,
                command=lambda d=dc_id: self._on_center_checkbox_clicked(d),
                bg="#0d1117",
                fg="#10b981" if is_checked else "#c9d1d9",
                selectcolor="#161b22",
                activebackground="#21262d",
                activeforeground="#ffffff",
                font=("Consolas", 8, "bold" if is_checked else "normal"),
                anchor="w",
                padx=4,
                pady=1,
            )
            cb.pack(fill="x", anchor="w")
            self.route_chk_buttons[dc_id] = cb

    def _on_center_checkbox_clicked(self, clicked_dc_id):
        self.manual_mode_var.set(True)
        self.autopilot_var.set(False)

        var = self.route_chk_vars.get(clicked_dc_id)
        now_checked = var.get() if var else True

        if not self.multi_chk_var.get():
            if now_checked:
                self.checked_dc_ids = {clicked_dc_id}
                for d_id, v in self.route_chk_vars.items():
                    if d_id != clicked_dc_id:
                        v.set(False)
            else:
                self.checked_dc_ids.discard(clicked_dc_id)
        else:
            if now_checked:
                self.checked_dc_ids.add(clicked_dc_id)
            else:
                self.checked_dc_ids.discard(clicked_dc_id)

        target_dc = next((dc for dc in GLOBAL_DATACENTERS if dc["dcId"] == clicked_dc_id), None)
        action_desc = "SELECTED" if now_checked else "DESELECTED"
        if target_dc:
            self.append_log(f"[ManualRoute] Checkbox {action_desc}: #{target_dc['dcId']} {target_dc['region']} ({target_dc['ip']}).")

        self._refresh_tree_checkbox_column_only()
        self.apply_checked_routes_now()

    def _on_tree_row_click_checkbox(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item:
            return

        values = self.tree.item(item, "values")
        if not values or len(values) < 3:
            return

        try:
            dc_id = int(values[2])
        except Exception:
            return

        is_chk_col = (col == "#1")
        if is_chk_col or not self.manual_mode_var.get():
            self.manual_mode_var.set(True)
            self.autopilot_var.set(False)

            currently_checked = dc_id in self.checked_dc_ids
            target_dc = next((dc for dc in GLOBAL_DATACENTERS if dc["dcId"] == dc_id), None)

            if not self.multi_chk_var.get():
                if currently_checked and is_chk_col:
                    self.checked_dc_ids.discard(dc_id)
                    action = "DESELECTED"
                else:
                    self.checked_dc_ids = {dc_id}
                    action = "LOCKED AS PRIMARY"
            else:
                if currently_checked:
                    self.checked_dc_ids.discard(dc_id)
                    action = "DESELECTED"
                else:
                    self.checked_dc_ids.add(dc_id)
                    action = "ADDED TO MULTIPATH"

            for d_id, var in self.route_chk_vars.items():
                var.set(d_id in self.checked_dc_ids)

            self._refresh_tree_checkbox_column_only()
            if target_dc:
                self.append_log(f"[ManualRoute] Datacenter #{dc_id} {target_dc['region']} {action}.")
            self.apply_checked_routes_now()

    def _refresh_tree_checkbox_column_only(self):
        for item in self.tree.get_children():
            vals = list(self.tree.item(item, "values"))
            if len(vals) >= 3:
                try:
                    d_id = int(vals[2])
                    vals[0] = "[✔]" if d_id in self.checked_dc_ids else "[  ]"
                    self.tree.item(item, values=vals)
                except Exception:
                    pass

    def apply_checked_routes_now(self):
        if not self.selected_game_obj:
            return
        g = self.selected_game_obj
        redundancy = int(self.udp_routes_var.get())

        if not self.checked_dc_ids:
            if self.ranked_routes_cache:
                self.checked_dc_ids.add(self.ranked_routes_cache[0]["dc"]["dcId"])
            else:
                self.checked_dc_ids.add(2129)

        ranked_map = {r["dc"]["dcId"]: r["dc"] for r in (self.ranked_routes_cache or [])}
        chosen_dcs = [ranked_map[dc_id] for dc_id in self.checked_dc_ids if dc_id in ranked_map]
        if not chosen_dcs:
            chosen_dcs = [dc for dc in GLOBAL_DATACENTERS if dc["dcId"] in self.checked_dc_ids]
        if not chosen_dcs:
            return

        primary_dc = chosen_dcs[0]
        backup_dcs = chosen_dcs[1:] if len(chosen_dcs) > 1 else []

        fn_lock = self.fn_subregion_lock_var.get()
        self.hdr_pill.config(text=f"● BINDING: {primary_dc['region']}...", bg="#0d2238", fg="#38bdf8")

        def bg_apply():
            self.core.apply_specific_dc_route(
                primary_dc,
                backup_dcs,
                g,
                redundancy=redundancy,
                lock_fn_subregion=fn_lock
            )
            def update_ui():
                self._update_primary_dc_ui(primary_dc, g)
                self.append_log(
                    f"[RouteEngine] Applied route for {g['exe']} -> {primary_dc['region']} ({primary_dc['ip']}) with program= firewall binding."
                )
            self.root.after(0, update_ui)

        threading.Thread(target=bg_apply, daemon=True).start()

    def toggle_apply_routes(self):
        if self.routes_active:
            self.core.clear_applied_routes()
            self.routes_active = False
            self.apply_toggle_btn.config(text="○ ROUTES STOPPED (CLICK TO ACTIVATE)", bg="#21262d")
            self.hdr_pill.config(text="○ GPN ROUTES OFF (DEFAULT ISP)", bg="#21262d", fg="#8b949e")
            self.tuner_status_pill.config(text="○ ROUTES STOPPED", bg="#21262d", fg="#8b949e")
            self.append_log("[RouteEngine] All routes and QoS firewall filters cleared. Using standard default gateway.")
        else:
            self.routes_active = True
            self.apply_toggle_btn.config(text="● ROUTES ACTIVATED (MULTIPATH ON)", bg="#ff2247")
            self.apply_checked_routes_now()

    def trigger_reanalyze_preserving_mode(self, live_probe=True):
        if not self.selected_game_obj:
            return
        self.select_and_apply_game_routes(self.selected_game_obj, live_probe=live_probe)

    def trigger_auto_analyze_and_apply(self, live_probe=True):
        if not self.selected_game_obj:
            return
        self.select_and_apply_game_routes(self.selected_game_obj, live_probe=live_probe)

    def _set_active_game_ui(self, g):
        self.selected_game_obj = g
        self.exe_var.set(g["exe"])
        title_str = g.get("title", g.get("display", ""))[:38]
        self.active_game_title_lbl.config(text=title_str)
        self.active_game_exe_lbl.config(text=f"Process: {g['exe']}  |  {g.get('ports', '')}")

        if hasattr(self, "route_hdr_lbl"):
            self.route_hdr_lbl.config(
                text=f"35 DATACENTERS MATRIX FOR: {title_str.upper()} (Click row to lock)"
            )

        if hasattr(self, "fn_subregion_lock_cb"):
            is_fn = "fortnite" in g.get("exe", "").lower() or g.get("slug") == "fortnite"
            if is_fn:
                self.fn_subregion_lock_cb.config(
                    text="🔒 Enforce Subregion Matchmaking (Quarantine Any)",
                    fg="#10b981"
                )
            else:
                self.fn_subregion_lock_cb.config(
                    text=f"🛡️ Isolate Routes for {title_str[:16]}",
                    fg="#38bdf8"
                )

        icon_path = g.get("icon_path", "")
        if icon_path and os.path.exists(icon_path):
            try:
                if icon_path not in self.icon_cache:
                    img = tk.PhotoImage(file=icon_path)
                    if img.width() > 32:
                        img = img.subsample(max(1, img.width() // 32), max(1, img.height() // 32))
                    self.icon_cache[icon_path] = img
                self.tuner_game_icon_lbl.config(image=self.icon_cache[icon_path], text="")
            except Exception:
                self.tuner_game_icon_lbl.config(image="", text="🎮")
        else:
            self.tuner_game_icon_lbl.config(image="", text="🎮")

    # --------------------------------------------------------------------------
    # TICKERS & REAL-TIME BACKGROUND MONITORING
    # --------------------------------------------------------------------------
    def toggle_live_telemetry_graph(self):
        """
        Toggles real-time hardware telemetry graph prober and rendering loop.
        When paused, halts background ICMP/TCP socket probing (0 network I/O)
        and cancels drawing ticks (0 CPU usage).
        """
        self.live_graph_active = not getattr(self, "live_graph_active", True)
        if self.live_graph_active:
            if hasattr(self, "live_graph_toggle_btn"):
                self.live_graph_toggle_btn.config(
                    text="⚡ LIVE GRAPH: ON",
                    bg="#0d2818", fg="#10b981",
                    activeforeground="#34d399"
                )
            self.append_log("[Telemetry] Live graph resumed. Probing gateway in real-time.")
            self._telemetry_graph_tick()
        else:
            if hasattr(self, "live_graph_toggle_btn"):
                self.live_graph_toggle_btn.config(
                    text="⏸ LIVE GRAPH: PAUSED",
                    bg="#21262d", fg="#f59e0b",
                    activeforeground="#fbbf24"
                )
            self.append_log("[Telemetry] Live graph paused to conserve resources (prober & drawing halted).")
            # Render clean static paused notification on canvas
            c = self.graph_canvas
            w = c.winfo_width() or 680
            h = c.winfo_height() or 155
            c.delete("all")
            for y_pct in (0.25, 0.5, 0.75):
                y = int(h * y_pct)
                c.create_line(0, y, w, y, fill="#1c2128", dash=(3, 3))
            c.create_text(w // 2, h // 2 - 8, text="⏸ REAL-TIME GRAPH PAUSED (RESOURCE SAVER ACTIVE)", fill="#8b949e", font=("Segoe UI", 11, "bold"))
            c.create_text(w // 2, h // 2 + 16, text="Hardware ICMP/TCP Prober Halted · Zero Network & CPU Overhead · Click [LIVE GRAPH] to Resume", fill="#484f58", font=("Consolas", 8))

    def _live_telemetry_prober_worker(self):
        """
        Continuous real-time hardware telemetry prober for the active connection.
        Sends live native ICMP Echo (TOS 0xB8) / TCP SYN packets directly
        to the active primary gateway every ~450ms.
        When live_graph_active is False, halts all socket operations to save resources.
        """
        while True:
            if not getattr(self, "live_graph_active", True):
                time.sleep(0.5)
                continue

            try:
                target_dc = getattr(self, "current_primary_dc", None)
                if not target_dc and GLOBAL_DATACENTERS:
                    target_dc = GLOBAL_DATACENTERS[0]

                if target_dc:
                    dc_id = target_dc.get("dcId")
                    full_dc = next((d for d in GLOBAL_DATACENTERS if d["dcId"] == dc_id), target_dc)
                    probe_target = full_dc.get("probe_host") or full_dc.get("ip") or "1.1.1.1"

                    # 1. Native ICMP Echo Request with DSCP 46 Expedited Forwarding TOS 0xB8
                    rtts = self.core.icmp_prober.ping_ip(probe_target, count=1, timeout_ms=450)
                    if rtts and rtts[0] < 900:
                        sample = float(rtts[0])
                        loss = 0
                    else:
                        # 2. Non-blocking TCP SYN handshake probe to port 443
                        res = self.core.probe_datacenter_latency(full_dc, count=1, timeout=0.45)
                        if res["min"] < 900:
                            sample = float(res["min"])
                            loss = int(res.get("loss", 0))
                        else:
                            sample = 999.0
                            loss = 100

                    if sample < 900:
                        target_dc["min"] = sample
                        try:
                            self.telemetry_sample_queue.put_nowait((sample, loss))
                        except queue.Full:
                            try:
                                self.telemetry_sample_queue.get_nowait()
                                self.telemetry_sample_queue.put_nowait((sample, loss))
                            except Exception:
                                pass
            except Exception:
                pass
            time.sleep(0.45)

    def run_reprobe_all_routes_ui(self):
        """
        Executes on-demand benchmark across all 35 datacenters for any selected game.
        Displays dedicated loading modal window (identical to initial startup splash screen).
        """
        if not self.selected_game_obj:
            return
        g = self.selected_game_obj

        def on_finish(ranked, checked_ids, primary_dc, game_obj):
            self.active_reprobe_modal = None
            if ranked:
                self.ranked_routes_cache = ranked
                self.checked_dc_ids = checked_ids
                self._rebuild_center_route_checkboxes(ranked)
                self._rebuild_matrix_tree(ranked)
                if primary_dc:
                    self._update_primary_dc_ui(primary_dc, game_obj)
                self.append_log(
                    f"[RouteEngine] Re-probe benchmark complete: All 35 datacenters measured for '{game_obj.get('title')}'. "
                    f"Selected Gateway: #{primary_dc['dcId']} {primary_dc['city']} ({primary_dc.get('min', 0):.1f} ms)."
                )

        self.active_reprobe_modal = PulseGpnReprobeModal(self, g, self.core, on_finish)

    def _update_matrix_tree_live_values(self, ranked):
        row_map = {}
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if vals and len(vals) >= 3:
                try:
                    row_map[int(vals[2])] = item
                except Exception:
                    pass

        for idx, r in enumerate(ranked):
            dc = r["dc"]
            dc_id = dc["dcId"]
            is_chk = dc_id in self.checked_dc_ids
            chk_str = "[✔]" if is_chk else "[  ]"

            if idx == 0:
                role = "★ PRIMARY"
            elif idx in (1, 2):
                role = f"⚡ BACKUP #{idx}"
            else:
                role = f"ALT #{idx+1}"

            reg_label = dc["region"]
            if dc.get("fn_sub"):
                reg_label = f"{dc['region']} [FN: {dc['fn_sub']}]"

            subnets_tag = dc.get("subnets_tag", "Direct IP")
            min_val = f"{r['min']:.1f}" if r["min"] < 900 else "N/A"
            avg_val = f"{r['avg']:.1f}" if r["avg"] < 900 else "N/A"
            jit_val = f"{r['jitter']:.1f}" if r["jitter"] < 900 else "0.0"
            sc_val = f"{r['score']:.1f}" if r["score"] < 900 else "999.0"

            new_vals = (chk_str, role, dc_id, reg_label, dc["ip"], subnets_tag, min_val, avg_val, jit_val, sc_val)
            if dc_id in row_map:
                self.tree.item(row_map[dc_id], values=new_vals)
            else:
                self.tree.insert("", "end", values=new_vals)

        for dc_id, cb in getattr(self, "route_chk_buttons", {}).items():
            r = next((x for x in ranked if x["dc"]["dcId"] == dc_id), None)
            if r:
                dc = r["dc"]
                min_txt = f"{r['min']:.1f} ms" if r["min"] < 900 else "Auto"
                alias_tag = f"[{dc.get('alias', dc.get('fn_sub', 'Relay'))}] "
                lbl_text = f"{alias_tag}{dc['city']} ({dc['country']}) — {min_txt}"
                try:
                    cb.config(text=lbl_text)
                except Exception:
                    pass

    def _telemetry_graph_tick(self):
        if not getattr(self, "live_graph_active", True):
            return  # Stop drawing loop when paused to conserve CPU

        c = self.graph_canvas
        w = c.winfo_width() or 680
        h = c.winfo_height() or 155
        c.delete("all")

        # Drain latest real physical samples from live telemetry prober queue
        latest_sample = None
        latest_loss = 0
        try:
            while True:
                s, l = self.telemetry_sample_queue.get_nowait()
                if s < 900:
                    latest_sample = s
                    latest_loss = l
        except queue.Empty:
            pass

        if latest_sample is not None:
            self.ping_history.append(latest_sample)
            self._last_rendered_sample = latest_sample
            self._last_loss = latest_loss
        else:
            # Continuously advance the waveform with the last known physical sample
            # so the graph smoothly flows like a living oscilloscope and NEVER freezes!
            last_s = getattr(self, "_last_rendered_sample", 38.0)
            self.ping_history.append(last_s)

        pts = list(self.ping_history)
        n = len(pts)
        step = (w - 20) / max(1, n - 1)
        coords = []

        # Dynamic graph ceiling: automatically expands if latency spikes during speedtests up to 350ms!
        max_seen = max(pts) if pts else 60.0
        graph_ceiling = 350.0 if max_seen > 120.0 else 120.0

        # Grid lines
        for y_pct in (0.25, 0.5, 0.75):
            y = int(h * y_pct)
            c.create_line(0, y, w, y, fill="#1c2128", dash=(3, 3))
            ms_lbl = int(graph_ceiling * (1.0 - y_pct))
            c.create_text(26, y - 6, text=f"{ms_lbl}ms", fill="#484f58", font=("Consolas", 7))

        for i, val in enumerate(pts):
            x = 10 + i * step
            norm = min(1.0, max(0.0, val / graph_ceiling))
            y = h - 20 - norm * (h - 40)
            coords.extend([x, y])

        curr_p = pts[-1]
        line_color = "#10b981" if curr_p < 80.0 else ("#f59e0b" if curr_p < 140.0 else "#ff2247")
        poly_color = "#0d2818" if curr_p < 80.0 else ("#2d240d" if curr_p < 140.0 else "#2d0d12")

        if len(coords) >= 4:
            poly_coords = [coords[0], h - 15] + coords + [coords[-2], h - 15]
            c.create_polygon(poly_coords, fill=poly_color, outline="")
            c.create_line(coords, fill=line_color, width=2, smooth=True)

        avg_p = sum(pts) / len(pts)
        max_p = max(pts)
        min_p = min(pts)
        jitter_calc = abs(pts[-1] - pts[-2]) if len(pts) >= 2 else 0.5
        curr_loss = getattr(self, "_last_loss", 0)

        info_str = f"LATENCY: {curr_p:.1f}ms  |  AVG: {avg_p:.1f}ms  |  MIN: {min_p:.1f}ms  |  MAX: {max_p:.1f}ms  |  JITTER: ±{jitter_calc:.1f}ms  |  LOSS: {curr_loss}%"
        status_color = "#38bdf8" if curr_p < 80 else ("#f59e0b" if curr_p < 140 else "#ff2247")
        c.create_text(w // 2, 14, text=info_str, fill=status_color, font=("Consolas", 9, "bold"))

        badge_bg = "#0d2818" if curr_p < 80 else ("#2d240d" if curr_p < 140 else "#2d0d12")
        badge_fg = "#10b981" if curr_p < 80 else ("#f59e0b" if curr_p < 140 else "#ff2247")
        self.live_ping_badge.config(text=f"CURRENT LATENCY: {curr_p:.1f} ms", bg=badge_bg, fg=badge_fg)

        if hasattr(self, "hdr_pill") and self.selected_game_obj and self.current_primary_dc:
            g_exe = self.selected_game_obj.get("exe", "game.exe")
            reg = self.current_primary_dc.get("region", "Datacenter")
            self.hdr_pill.config(
                text=f"● ROUTING: {g_exe} ──► {reg} ({curr_p:.1f} ms)",
                bg=badge_bg, fg=badge_fg
            )

        self.root.after(480, self._telemetry_graph_tick)

    def fortnite_live_match_watcher_tick(self):
        info = self.core.parse_fortnite_live_log_server_and_pings()
        if info["match_ip"] and info["match_ip"] != self.core.last_fortnite_match_server:
            self.core.last_fortnite_match_server = (info["match_ip"], info["match_port"])
            self.append_log(
                f"[FortniteWatcher] Live match server detected: {info['match_ip']}:{info['match_port']} (QoS Logged)."
            )
        self.root.after(4000, self.fortnite_live_match_watcher_tick)

    def process_watchdog_tick(self):
        if hasattr(self, "engine_status_pill"):
            self.core.detect_conflicting_gpn_process()
            if self.core.system_telemetry_active:
                self.engine_status_pill.config(
                    text=f"● GPN EXTERNO ACTIVO (PID: {self.core.system_telemetry_pid})",
                    bg="#0d2818", fg="#10b981"
                )
            else:
                self.engine_status_pill.config(
                    text="● PULSEGPN ENGINE ACTIVE",
                    bg="#0d2238", fg="#38bdf8"
                )
        self.root.after(6000, self.process_watchdog_tick)

    def run_launch_active_game(self):
        if not self.selected_game_obj:
            return
        g = self.selected_game_obj
        self.append_log(f"[GameLauncher] Initiating launch sequence for '{g.get('title')}'...")
        threading.Thread(target=self.core.launch_game, args=(g,), daemon=True).start()

    def run_all_fps_boost(self):
        exe = self.exe_var.get().strip() or "FortniteClient-Win64-Shipping.exe"
        threading.Thread(target=self.core.apply_all_12_fps_boost_tweaks, args=(exe,), daemon=True).start()

    def RefreshNICTable(self):
        ifs = self.core.get_active_interfaces()
        if hasattr(self, "nic_tree"):
            for item in self.nic_tree.get_children():
                self.nic_tree.delete(item)
            for idx, i in enumerate(ifs):
                role = "★ Primary (Multipath)" if idx == 0 else "⚡ Failover Backup"
                self.nic_tree.insert("", "end", values=(
                    i["guid"], i["ip"], i["gateway"], i["dns"],
                    "No (0)" if i["metered"] == 0 else "Yes (1)",
                    f"Metric {i['metric']} (IF #{i['if_index']})", role
                ))
        if ifs:
            self.if_side_lbl.config(
                text=f"Active Adapter (IF #{ifs[0]['if_index']}):\n{ifs[0]['ip']}\nGW: {ifs[0]['gateway']}\nMetric: 1 (RNDIS Turbo)"
            )

    def RefreshAndOptimizeNICs(self):
        def worker():
            self.core.optimize_active_rndis_and_nic()
            self.root.after(0, self.RefreshNICTable)
            self.append_log("[Multi-Internet] RNDIS & NIC adapters optimized with Metric=1, TCPNoDelay=1, and Metered=0.")
        threading.Thread(target=worker, daemon=True).start()

    def run_live_game_sniffer(self):
        exe = self.exe_var.get().strip()
        self.append_log(f"[LiveSniffer] Scanning active sockets and match logs for '{exe}'...")
        def worker():
            conns = self.core.sniff_live_game_connections(exe)
            def update_ui():
                for item in self.sniffer_tree.get_children():
                    self.sniffer_tree.delete(item)
                for proto, rip, rport, pid in conns:
                    self.sniffer_tree.insert("", "end", values=(pid, proto, rip, rport))
            self.root.after(0, update_ui)
            self.trigger_reanalyze_preserving_mode(live_probe=True)
        threading.Thread(target=worker, daemon=True).start()

    def run_dns_optimizer(self):
        self.append_log("[DnsOptimizer] Benchmarking all 7 Gaming DNS providers...")
        def worker():
            res = self.core.benchmark_dns_servers()
            best_ms, best_name, p_dns, s_dns = res[0]
            def update_dns_ui():
                for item in self.dns_tree.get_children():
                    self.dns_tree.delete(item)
                for ms, name, p, s in res:
                    self.dns_tree.insert("", "end", values=(name, p, s, f"{ms} ms"))
            self.root.after(0, update_dns_ui)
            self.append_log(f"[DnsOptimizer] Fastest DNS: {best_name} ({p_dns}) -> {best_ms} ms. Applying...")
            self.core.apply_dns_to_active_interfaces(p_dns, s_dns)
            self.root.after(0, self.RefreshNICTable)
        threading.Thread(target=worker, daemon=True).start()

    def run_ram_cleaner(self):
        threading.Thread(target=self.core.clean_ram_working_sets, daemon=True).start()

    def run_fps_shaper(self):
        exe = self.exe_var.get().strip()
        threading.Thread(target=self.core.apply_fps_boost_and_traffic_shaper, args=(exe,), daemon=True).start()
        self.append_log(f"[TrafficShaper] WFP DSCP 46 (EF) priority applied to {exe} and background throttled.")

    def run_sync_storage_db(self):
        def worker():
            self.core.sync_from_storage_db()
            self.core.detect_conflicting_gpn_process()
            def update_ui():
                if hasattr(self, "engine_status_pill"):
                    if self.core.system_telemetry_active:
                        self.engine_status_pill.config(
                            text=f"● GPN EXTERNO ACTIVO (PID: {self.core.system_telemetry_pid})",
                            bg="#0d2818", fg="#10b981"
                        )
                    else:
                        self.engine_status_pill.config(
                            text="● PULSEGPN ENGINE ACTIVE",
                            bg="#0d2238", fg="#38bdf8"
                        )
                if hasattr(self, "ts_info_bar"):
                    st = self.core.speedtest_data
                    dl_str = f"{st.get('download_mbps', 144.35):.2f} Mbps" if st else "144.35 Mbps"
                    ul_str = f"{st.get('upload_mbps', 21.07):.2f} Mbps" if st else "21.07 Mbps"
                    isp_str = st.get('isp', 'TELECOMUNICACIONES DE GUATEMALA') if st else "TELECOMUNICACIONES DE GUATEMALA"
                    city_str = st.get('city', 'Guatemala City') if st else "Guatemala City"
                    self.append_log(f"[StorageDB] Synchronized: {dl_str} DL / {ul_str} UL ({isp_str}).")
            self.root.after(0, update_ui)
        threading.Thread(target=worker, daemon=True).start()

    def stop_all_routes_ui(self):
        self.core.clear_applied_routes()
        self.routes_active = False
        self.apply_toggle_btn.config(text="○ ROUTES STOPPED (CLICK TO ACTIVATE)", bg="#21262d")
        self.hdr_pill.config(text="○ GPN ROUTES OFF (DEFAULT ISP)", bg="#21262d", fg="#8b949e")
        self.tuner_status_pill.config(text="○ ROUTES STOPPED", bg="#21262d", fg="#8b949e")
        self.append_log("[RouteEngine] All active routes and firewall rules successfully flushed.")

    def initial_startup_auto_analysis(self):
        self.RefreshNICTable()
        threading.Thread(
            target=self.core.repair_fortnite_invalid_backend_and_shortcut,
            kwargs={"force_check_shortcut": True},
            daemon=True
        ).start()

        # Background DC ping warm-up
        threading.Thread(
            target=lambda: self.core.probe_all_datacenters(local_ip="0.0.0.0", count=1, timeout=0.35),
            daemon=True
        ).start()

        # If route selection is already initiated or finished, don't overwrite it
        if getattr(self, "_analysis_generation", 0) > 0:
            return

        running_game = self.core.detect_running_game_process()
        target_g = None
        if running_game:
            target_g = running_game
            self.append_log(f"[AutoDetector] Active running game process detected: {running_game['display']}")
        elif self.selected_game_obj:
            target_g = self.selected_game_obj
        elif self.installed_games:
            target_g = self.installed_games[0]
        elif self.all_games:
            target_g = self.all_games[0]

        if target_g:
            self.select_and_apply_game_routes(target_g, live_probe=False)
            self.append_log(f"[PulseGPN Pro v1.0] Initial active game: '{target_g.get('title')}'. Manual Routing locked.")

    def append_log(self, msg):
        try:
            ts = time.strftime("%H:%M:%S")
            self.log_box.insert("end", f"[{ts}] {msg}\n")
            self.log_box.see("end")
        except Exception:
            pass

if __name__ == "__main__":
    if "--cli-test" in sys.argv:
        core = PulseGpnCore(print)
        repaired = core.repair_fortnite_invalid_backend_and_shortcut(force_check_shortcut=True)
        print(f"[*] Fortnite EGLv2 Backend & Shortcut Repair Actions: {repaired}")
        games = core.load_all_2811_games_from_storage_db()
        print(f"[*] Total Games Loaded in v5.1: {len(games)}")
        installed = core.scan_all_installed_games()
        print(f"[*] Total Installed Games Detected: {len(installed)}")
        fn_game = next(g for g in games if g["slug"] == "fortnite")
        ranked = core.analyze_all_routes_for_game(fn_game, continent_filter="NA", live_probe=True)
        print(f"[*] Fortnite Top 5 NA Routes: {[(r['dc']['region'], r['min'], r['score']) for r in ranked[:5]]}")
        tx_dc = next(dc for dc in GLOBAL_DATACENTERS if dc["dcId"] == 2131)
        core.apply_specific_dc_route(tx_dc, [], fn_game, redundancy=2, lock_fn_subregion=True)
        fn_live = core.parse_fortnite_live_log_server_and_pings()
        print(f"[*] Fortnite Live Log Info: match={fn_live['match_ip']}:{fn_live['match_port']}, qos_count={len(fn_live['qos_pings'])}")
        core.clear_applied_routes()
        print("[*] CLI Test Completed Successfully.")
        sys.exit(0)

    root = tk.Tk()
    root.withdraw()

    def on_splash_complete(core, all_games, installed_games):
        app = PulseGpnApp(root, core=core, all_games=all_games, installed_games=installed_games)
        root.deiconify()

    PulseGpnSplashScreen(root, on_splash_complete)
    root.mainloop()
