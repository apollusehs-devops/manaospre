import json
from jinja2 import Template
from zlib import crc32
from os import chmod
import stat

DEFAULT_SSID = "MagicModem"
HOSTAP_CONF_TEMPLATE = """# Autogenerated by hostapconfgenerator.py
#   editing ill-advised, but YMMV
interface=wlan0
bridge=br0
driver=nl80211
country_code={{country_code}}
hw_mode=g
channel={{channel}}
ieee80211d=1
ieee80211n=1
wmm_enabled=1

ssid={{ssid}}
wpa=2
auth_algs=1
rsn_pairwise=CCMP
wpa_key_mgmt=WPA-PSK
wpa_passphrase={{wpa_passphrase}}
macaddr_acl=0
"""

HOSTAP_CONF_DEFAULTS = {
        "country_code": "US",
        "channel": 10,
        "wpa_passphrase": "88888888"
    }

def is_string(o):
    # isolating the py2 str check
    return isinstance(o, str) or isinstance(o, str)

def generate_ssid():
    ssid = DEFAULT_SSID
    try:
        with open("/sys/class/net/wlan0/address") as f:
            address = f.readline()
            ssid = "%s-%x" % (DEFAULT_SSID, abs(crc32(address)))
    except IOError as e:
        pass
    return ssid

def read_config(config_filename):
    config = {}
    try:
        config = json.load(open(config_filename, "r"))
    except (IOError, ValueError) as e:
        pass
    return config

def chmod_all_readwrite(filename):
    try:
        chmod(filename, stat.S_IRUSR | stat.S_IWUSR
                | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    except OSError as e:
        pass

def write_config(config, config_filename):
    try:
        json.dump(config, open(config_filename, "w"),
                sort_keys=True, indent=4)
    except (IOError, ValueError) as e:
        pass

def build_conf_file(config):
    for confkey, confval in list(HOSTAP_CONF_DEFAULTS.items()):
        # Isn't really type safe on values
        if confkey not in config \
                or config[confkey] == "":
            config[confkey] = confval

    if "ssid" not in config:
        config["ssid"] = generate_ssid()

    template = Template(HOSTAP_CONF_TEMPLATE)
    hostapd_conf = template.render(config)
    print(hostapd_conf)
    return (config, hostapd_conf)

if __name__ == "__main__":
    apconfig_filename = "/tmp/apconfig.json"
    config = read_config(apconfig_filename)
    (config, hostapd_conf) = build_conf_file(config)
    write_config(config, apconfig_filename)
    chmod_all_readwrite(apconfig_filename)
