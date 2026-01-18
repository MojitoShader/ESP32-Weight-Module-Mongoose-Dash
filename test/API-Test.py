#!/usr/bin/env python3
import requests

BASE = "http://192.168.1.221"  # IP des Moduls anpassen

def get_weight():
    r = requests.get(f"{BASE}/api/weight", timeout=2)
    r.raise_for_status()
    print("weight:", r.json())

def get_glass():
    r = requests.get(f"{BASE}/api/glass", timeout=2)
    r.raise_for_status()
    print("glass:", r.json())

def get_status():
    r = requests.get(f"{BASE}/api/status", timeout=2)
    r.raise_for_status()
    print("status:", r.json())

def post_tare():
    r = requests.post(f"{BASE}/api/tare", timeout=2)
    r.raise_for_status()
    print("tare:", r.json())

if __name__ == "__main__":
    get_weight()
    get_glass()
    get_status()
    post_tare()
    get_weight()  # nach Tare
