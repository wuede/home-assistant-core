"""Validate integration quality scale files."""

from __future__ import annotations

from dataclasses import dataclass

import voluptuous as vol
from voluptuous.humanize import humanize_error

from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import load_yaml_dict

from .model import Config, Integration, ScaledQualityScaleTiers
from .quality_scale_validation import (
    RuleValidationProtocol,
    config_entry_unloading,
    config_flow,
    diagnostics,
    discovery,
    parallel_updates,
    reauthentication_flow,
    reconfiguration_flow,
    runtime_data,
    strict_typing,
    unique_config_entry,
)

QUALITY_SCALE_TIERS = {value.name.lower(): value for value in ScaledQualityScaleTiers}


@dataclass
class Rule:
    """Quality scale rules."""

    name: str
    tier: ScaledQualityScaleTiers
    validator: RuleValidationProtocol | None = None


ALL_RULES = [
    # BRONZE
    Rule("action-setup", ScaledQualityScaleTiers.BRONZE),
    Rule("appropriate-polling", ScaledQualityScaleTiers.BRONZE),
    Rule("brands", ScaledQualityScaleTiers.BRONZE),
    Rule("common-modules", ScaledQualityScaleTiers.BRONZE),
    Rule("config-flow", ScaledQualityScaleTiers.BRONZE, config_flow),
    Rule("config-flow-test-coverage", ScaledQualityScaleTiers.BRONZE),
    Rule("dependency-transparency", ScaledQualityScaleTiers.BRONZE),
    Rule("docs-actions", ScaledQualityScaleTiers.BRONZE),
    Rule("docs-high-level-description", ScaledQualityScaleTiers.BRONZE),
    Rule("docs-installation-instructions", ScaledQualityScaleTiers.BRONZE),
    Rule("docs-removal-instructions", ScaledQualityScaleTiers.BRONZE),
    Rule("entity-event-setup", ScaledQualityScaleTiers.BRONZE),
    Rule("entity-unique-id", ScaledQualityScaleTiers.BRONZE),
    Rule("has-entity-name", ScaledQualityScaleTiers.BRONZE),
    Rule("runtime-data", ScaledQualityScaleTiers.BRONZE, runtime_data),
    Rule("test-before-configure", ScaledQualityScaleTiers.BRONZE),
    Rule("test-before-setup", ScaledQualityScaleTiers.BRONZE),
    Rule("unique-config-entry", ScaledQualityScaleTiers.BRONZE, unique_config_entry),
    # SILVER
    Rule("action-exceptions", ScaledQualityScaleTiers.SILVER),
    Rule(
        "config-entry-unloading", ScaledQualityScaleTiers.SILVER, config_entry_unloading
    ),
    Rule("docs-configuration-parameters", ScaledQualityScaleTiers.SILVER),
    Rule("docs-installation-parameters", ScaledQualityScaleTiers.SILVER),
    Rule("entity-unavailable", ScaledQualityScaleTiers.SILVER),
    Rule("integration-owner", ScaledQualityScaleTiers.SILVER),
    Rule("log-when-unavailable", ScaledQualityScaleTiers.SILVER),
    Rule("parallel-updates", ScaledQualityScaleTiers.SILVER, parallel_updates),
    Rule(
        "reauthentication-flow", ScaledQualityScaleTiers.SILVER, reauthentication_flow
    ),
    Rule("test-coverage", ScaledQualityScaleTiers.SILVER),
    # GOLD: [
    Rule("devices", ScaledQualityScaleTiers.GOLD),
    Rule("diagnostics", ScaledQualityScaleTiers.GOLD, diagnostics),
    Rule("discovery", ScaledQualityScaleTiers.GOLD, discovery),
    Rule("discovery-update-info", ScaledQualityScaleTiers.GOLD),
    Rule("docs-data-update", ScaledQualityScaleTiers.GOLD),
    Rule("docs-examples", ScaledQualityScaleTiers.GOLD),
    Rule("docs-known-limitations", ScaledQualityScaleTiers.GOLD),
    Rule("docs-supported-devices", ScaledQualityScaleTiers.GOLD),
    Rule("docs-supported-functions", ScaledQualityScaleTiers.GOLD),
    Rule("docs-troubleshooting", ScaledQualityScaleTiers.GOLD),
    Rule("docs-use-cases", ScaledQualityScaleTiers.GOLD),
    Rule("dynamic-devices", ScaledQualityScaleTiers.GOLD),
    Rule("entity-category", ScaledQualityScaleTiers.GOLD),
    Rule("entity-device-class", ScaledQualityScaleTiers.GOLD),
    Rule("entity-disabled-by-default", ScaledQualityScaleTiers.GOLD),
    Rule("entity-translations", ScaledQualityScaleTiers.GOLD),
    Rule("exception-translations", ScaledQualityScaleTiers.GOLD),
    Rule("icon-translations", ScaledQualityScaleTiers.GOLD),
    Rule("reconfiguration-flow", ScaledQualityScaleTiers.GOLD, reconfiguration_flow),
    Rule("repair-issues", ScaledQualityScaleTiers.GOLD),
    Rule("stale-devices", ScaledQualityScaleTiers.GOLD),
    # PLATINUM
    Rule("async-dependency", ScaledQualityScaleTiers.PLATINUM),
    Rule("inject-websession", ScaledQualityScaleTiers.PLATINUM),
    Rule("strict-typing", ScaledQualityScaleTiers.PLATINUM, strict_typing),
]

SCALE_RULES = {
    tier: [rule.name for rule in ALL_RULES if rule.tier == tier]
    for tier in ScaledQualityScaleTiers
}

VALIDATORS = {rule.name: rule.validator for rule in ALL_RULES if rule.validator}

RULE_URL = (
    "Please check the documentation at "
    "https://developers.home-assistant.io/docs/core/"
    "integration-quality-scale/rules/{rule_name}/"
)

INTEGRATIONS_WITHOUT_QUALITY_SCALE_FILE = [
    "abode",
    "accuweather",
    "acer_projector",
    "acmeda",
    "actiontec",
    "adax",
    "adguard",
    "ads",
    "advantage_air",
    "aemet",
    "aftership",
    "agent_dvr",
    "airly",
    "airnow",
    "airq",
    "airthings",
    "airthings_ble",
    "airtouch4",
    "airtouch5",
    "airvisual",
    "airvisual_pro",
    "airzone",
    "airzone_cloud",
    "aladdin_connect",
    "alarmdecoder",
    "alert",
    "alexa",
    "alpha_vantage",
    "amazon_polly",
    "amberelectric",
    "ambient_network",
    "ambient_station",
    "amcrest",
    "ampio",
    "analytics",
    "analytics_insights",
    "android_ip_webcam",
    "androidtv",
    "androidtv_remote",
    "anel_pwrctrl",
    "anova",
    "anthemav",
    "anthropic",
    "aosmith",
    "apache_kafka",
    "apcupsd",
    "apple_tv",
    "apprise",
    "aprilaire",
    "aprs",
    "apsystems",
    "aquacell",
    "aqualogic",
    "aquostv",
    "aranet",
    "arcam_fmj",
    "arest",
    "arris_tg2492lg",
    "aruba",
    "arve",
    "arwn",
    "aseko_pool_live",
    "assist_pipeline",
    "asterisk_mbox",
    "asuswrt",
    "atag",
    "aten_pe",
    "atome",
    "august",
    "aurora",
    "aurora_abb_powerone",
    "aussie_broadband",
    "avea",
    "avion",
    "awair",
    "aws",
    "axis",
    "azure_data_explorer",
    "azure_devops",
    "azure_event_hub",
    "azure_service_bus",
    "backup",
    "baf",
    "baidu",
    "balboa",
    "bang_olufsen",
    "bayesian",
    "bbox",
    "beewi_smartclim",
    "bitcoin",
    "bizkaibus",
    "blackbird",
    "blebox",
    "blink",
    "blinksticklight",
    "blockchain",
    "blue_current",
    "bluemaestro",
    "bluesound",
    "bluetooth",
    "bluetooth_adapters",
    "bluetooth_le_tracker",
    "bluetooth_tracker",
    "bmw_connected_drive",
    "bond",
    "bosch_shc",
    "braviatv",
    "broadlink",
    "brother",
    "brottsplatskartan",
    "browser",
    "brunt",
    "bryant_evolution",
    "bsblan",
    "bt_home_hub_5",
    "bt_smarthub",
    "bthome",
    "buienradar",
    "caldav",
    "canary",
    "cast",
    "ccm15",
    "cert_expiry",
    "chacon_dio",
    "channels",
    "circuit",
    "cisco_ios",
    "cisco_mobility_express",
    "cisco_webex_teams",
    "citybikes",
    "clementine",
    "clickatell",
    "clicksend",
    "clicksend_tts",
    "climacell",
    "cloud",
    "cloudflare",
    "cmus",
    "co2signal",
    "coinbase",
    "color_extractor",
    "comed_hourly_pricing",
    "comelit",
    "comfoconnect",
    "command_line",
    "compensation",
    "concord232",
    "control4",
    "coolmaster",
    "cppm_tracker",
    "cpuspeed",
    "crownstone",
    "cups",
    "currencylayer",
    "daikin",
    "danfoss_air",
    "datadog",
    "ddwrt",
    "deako",
    "debugpy",
    "deconz",
    "decora",
    "decora_wifi",
    "delijn",
    "deluge",
    "demo",
    "denon",
    "denonavr",
    "derivative",
    "devialet",
    "device_sun_light_trigger",
    "devolo_home_control",
    "devolo_home_network",
    "dexcom",
    "dhcp",
    "dialogflow",
    "digital_ocean",
    "directv",
    "discogs",
    "discord",
    "dlib_face_detect",
    "dlib_face_identify",
    "dlink",
    "dlna_dmr",
    "dlna_dms",
    "dnsip",
    "dominos",
    "doods",
    "doorbird",
    "dormakaba_dkey",
    "dovado",
    "downloader",
    "dremel_3d_printer",
    "drop_connect",
    "dsmr",
    "dsmr_reader",
    "dublin_bus_transport",
    "duckdns",
    "duke_energy",
    "dunehd",
    "duotecno",
    "dwd_weather_warnings",
    "dweet",
    "dynalite",
    "eafm",
    "easyenergy",
    "ebox",
    "ebusd",
    "ecoal_boiler",
    "ecobee",
    "ecoforest",
    "econet",
    "ecovacs",
    "ecowitt",
    "eddystone_temperature",
    "edimax",
    "edl21",
    "efergy",
    "egardia",
    "eight_sleep",
    "electrasmart",
    "electric_kiwi",
    "elevenlabs",
    "eliqonline",
    "elkm1",
    "elmax",
    "elv",
    "elvia",
    "emby",
    "emoncms",
    "emoncms_history",
    "emonitor",
    "emulated_hue",
    "emulated_kasa",
    "emulated_roku",
    "energenie_power_sockets",
    "energy",
    "energyzero",
    "enigma2",
    "enocean",
    "enphase_envoy",
    "entur_public_transport",
    "environment_canada",
    "envisalink",
    "ephember",
    "epic_games_store",
    "epion",
    "epson",
    "eq3btsmart",
    "escea",
    "esphome",
    "etherscan",
    "eufy",
    "eufylife_ble",
    "everlights",
    "evil_genius_labs",
    "evohome",
    "ezviz",
    "faa_delays",
    "facebook",
    "fail2ban",
    "familyhub",
    "fastdotcom",
    "feedreader",
    "ffmpeg_motion",
    "ffmpeg_noise",
    "fibaro",
    "fido",
    "file",
    "filesize",
    "filter",
    "fints",
    "fireservicerota",
    "firmata",
    "fivem",
    "fixer",
    "fjaraskupan",
    "fleetgo",
    "flexit",
    "flexit_bacnet",
    "flic",
    "flick_electric",
    "flipr",
    "flo",
    "flock",
    "flume",
    "flux",
    "flux_led",
    "folder",
    "folder_watcher",
    "foobot",
    "forecast_solar",
    "forked_daapd",
    "fortios",
    "foscam",
    "foursquare",
    "free_mobile",
    "freebox",
    "freedns",
    "freedompro",
    "fritzbox",
    "fritzbox_callmonitor",
    "fronius",
    "frontier_silicon",
    "fujitsu_fglair",
    "fujitsu_hvac",
    "futurenow",
    "garadget",
    "garages_amsterdam",
    "gardena_bluetooth",
    "gc100",
    "gdacs",
    "generic",
    "generic_hygrostat",
    "generic_thermostat",
    "geniushub",
    "geo_json_events",
    "geo_rss_events",
    "geocaching",
    "geofency",
    "geonetnz_quakes",
    "geonetnz_volcano",
    "gios",
    "github",
    "gitlab_ci",
    "gitter",
    "glances",
    "go2rtc",
    "goalzero",
    "gogogate2",
    "goodwe",
    "google",
    "google_assistant",
    "google_assistant_sdk",
    "google_cloud",
    "google_domains",
    "google_generative_ai_conversation",
    "google_mail",
    "google_maps",
    "google_pubsub",
    "google_sheets",
    "google_tasks",
    "google_translate",
    "google_travel_time",
    "google_wifi",
    "govee_ble",
    "govee_light_local",
    "gpsd",
    "gpslogger",
    "graphite",
    "gree",
    "greeneye_monitor",
    "greenwave",
    "group",
    "growatt_server",
    "gstreamer",
    "gtfs",
    "guardian",
    "habitica",
    "harman_kardon_avr",
    "harmony",
    "hassio",
    "haveibeenpwned",
    "hddtemp",
    "hdmi_cec",
    "heatmiser",
    "heos",
    "here_travel_time",
    "hikvision",
    "hikvisioncam",
    "hisense_aehw4a1",
    "history_stats",
    "hitron_coda",
    "hive",
    "hko",
    "hlk_sw16",
    "holiday",
    "home_connect",
    "homekit",
    "homekit_controller",
    "homematic",
    "homematicip_cloud",
    "homeworks",
    "honeywell",
    "horizon",
    "hp_ilo",
    "html5",
    "http",
    "huawei_lte",
    "hue",
    "huisbaasje",
    "hunterdouglas_powerview",
    "husqvarna_automower_ble",
    "huum",
    "hvv_departures",
    "hydrawise",
    "hyperion",
    "ialarm",
    "iammeter",
    "iaqualink",
    "ibeacon",
    "icloud",
    "idasen_desk",
    "idteck_prox",
    "ifttt",
    "iglo",
    "ign_sismologia",
    "ihc",
    "imgw_pib",
    "improv_ble",
    "incomfort",
    "influxdb",
    "inkbird",
    "insteon",
    "integration",
    "intellifire",
    "intesishome",
    "ios",
    "iotawatt",
    "iotty",
    "iperf3",
    "ipma",
    "ipp",
    "iqvia",
    "irish_rail_transport",
    "isal",
    "iskra",
    "islamic_prayer_times",
    "israel_rail",
    "iss",
    "isy994",
    "itach",
    "itunes",
    "izone",
    "jellyfin",
    "jewish_calendar",
    "joaoapps_join",
    "juicenet",
    "justnimbus",
    "jvc_projector",
    "kaiterra",
    "kaleidescape",
    "kankun",
    "keba",
    "keenetic_ndms2",
    "kef",
    "kegtron",
    "keyboard",
    "keyboard_remote",
    "keymitt_ble",
    "kira",
    "kitchen_sink",
    "kiwi",
    "kmtronic",
    "knocki",
    "knx",
    "kodi",
    "konnected",
    "kostal_plenticore",
    "kraken",
    "kulersky",
    "kwb",
    "lacrosse",
    "lacrosse_view",
    "lametric",
    "landisgyr_heat_meter",
    "lannouncer",
    "lastfm",
    "launch_library",
    "laundrify",
    "lcn",
    "ld2410_ble",
    "leaone",
    "led_ble",
    "lektrico",
    "lg_netcast",
    "lg_soundbar",
    "lg_thinq",
    "lidarr",
    "life360",
    "lifx",
    "lifx_cloud",
    "lightwave",
    "limitlessled",
    "linear_garage_door",
    "linkplay",
    "linksys_smart",
    "linode",
    "linux_battery",
    "lirc",
    "litejet",
    "litterrobot",
    "livisi",
    "llamalab_automate",
    "local_calendar",
    "local_file",
    "local_ip",
    "local_todo",
    "location",
    "locative",
    "logentries",
    "logi_circle",
    "london_air",
    "london_underground",
    "lookin",
    "loqed",
    "luci",
    "luftdaten",
    "lupusec",
    "lutron",
    "lutron_caseta",
    "lw12wifi",
    "lyric",
    "madvr",
    "mailbox",
    "mailgun",
    "manual",
    "manual_mqtt",
    "map",
    "marytts",
    "matrix",
    "matter",
    "maxcube",
    "mazda",
    "mealie",
    "meater",
    "medcom_ble",
    "media_extractor",
    "mediaroom",
    "melcloud",
    "melissa",
    "melnor",
    "meraki",
    "message_bird",
    "met",
    "met_eireann",
    "meteo_france",
    "meteoalarm",
    "meteoclimatic",
    "metoffice",
    "mfi",
    "microbees",
    "microsoft",
    "microsoft_face",
    "microsoft_face_detect",
    "microsoft_face_identify",
    "mikrotik",
    "mill",
    "min_max",
    "minecraft_server",
    "minio",
    "mjpeg",
    "moat",
    "mobile_app",
    "mochad",
    "modbus",
    "modem_callerid",
    "modern_forms",
    "moehlenhoff_alpha2",
    "mold_indicator",
    "monarch_money",
    "monoprice",
    "monzo",
    "moon",
    "mopeka",
    "motion_blinds",
    "motionblinds_ble",
    "motioneye",
    "motionmount",
    "mpd",
    "mqtt_eventstream",
    "mqtt_json",
    "mqtt_room",
    "mqtt_statestream",
    "msteams",
    "mullvad",
    "music_assistant",
    "mutesync",
    "mvglive",
    "mycroft",
    "myq",
    "mysensors",
    "mystrom",
    "mythicbeastsdns",
    "nad",
    "nam",
    "namecheapdns",
    "nanoleaf",
    "nasweb",
    "neato",
    "nederlandse_spoorwegen",
    "ness_alarm",
    "netatmo",
    "netdata",
    "netgear",
    "netgear_lte",
    "netio",
    "network",
    "neurio_energy",
    "nexia",
    "nextbus",
    "nextcloud",
    "nextdns",
    "nfandroidtv",
    "nibe_heatpump",
    "nice_go",
    "nightscout",
    "niko_home_control",
    "nilu",
    "nina",
    "nissan_leaf",
    "nmap_tracker",
    "nmbs",
    "no_ip",
    "noaa_tides",
    "nobo_hub",
    "norway_air",
    "notify_events",
    "notion",
    "nsw_fuel_station",
    "nsw_rural_fire_service_feed",
    "nuheat",
    "nuki",
    "numato",
    "nut",
    "nws",
    "nx584",
    "nyt_games",
    "nzbget",
    "oasa_telematics",
    "obihai",
    "octoprint",
    "oem",
    "ohmconnect",
    "ollama",
    "ombi",
    "omnilogic",
    "oncue",
    "ondilo_ico",
    "onewire",
    "onvif",
    "open_meteo",
    "openai_conversation",
    "openalpr_cloud",
    "openerz",
    "openevse",
    "openexchangerates",
    "opengarage",
    "openhardwaremonitor",
    "openhome",
    "opensensemap",
    "opensky",
    "opentherm_gw",
    "openuv",
    "openweathermap",
    "opnsense",
    "opower",
    "opple",
    "oralb",
    "oru",
    "orvibo",
    "osoenergy",
    "osramlightify",
    "otbr",
    "otp",
    "ourgroceries",
    "overkiz",
    "ovo_energy",
    "owntracks",
    "p1_monitor",
    "panasonic_bluray",
    "panasonic_viera",
    "pandora",
    "panel_iframe",
    "peco",
    "pegel_online",
    "pencom",
    "permobil",
    "persistent_notification",
    "person",
    "philips_js",
    "pi_hole",
    "picnic",
    "picotts",
    "pilight",
    "ping",
    "pioneer",
    "pjlink",
    "plaato",
    "plant",
    "plex",
    "plum_lightpad",
    "pocketcasts",
    "point",
    "poolsense",
    "powerwall",
    "private_ble_device",
    "profiler",
    "progettihwsw",
    "proliphix",
    "prometheus",
    "prosegur",
    "prowl",
    "proximity",
    "proxmoxve",
    "prusalink",
    "ps4",
    "pulseaudio_loopback",
    "pure_energie",
    "purpleair",
    "push",
    "pushbullet",
    "pushover",
    "pushsafer",
    "pvoutput",
    "pvpc_hourly_pricing",
    "pyload",
    "qbittorrent",
    "qingping",
    "qld_bushfire",
    "qnap",
    "qnap_qsw",
    "qrcode",
    "quantum_gateway",
    "qvr_pro",
    "qwikswitch",
    "rabbitair",
    "rachio",
    "radarr",
    "radio_browser",
    "radiotherm",
    "raincloud",
    "rainforest_eagle",
    "rainforest_raven",
    "rainmachine",
    "random",
    "rapt_ble",
    "raspyrfm",
    "rdw",
    "recollect_waste",
    "recorder",
    "recswitch",
    "reddit",
    "refoss",
    "rejseplanen",
    "remember_the_milk",
    "remote_rpi_gpio",
    "renson",
    "repetier",
    "rest",
    "rest_command",
    "rflink",
    "rfxtrx",
    "rhasspy",
    "ridwell",
    "ring",
    "ripple",
    "risco",
    "rituals_perfume_genie",
    "rmvtransport",
    "roborock",
    "rocketchat",
    "roku",
    "romy",
    "roomba",
    "roon",
    "route53",
    "rova",
    "rpi_camera",
    "rpi_power",
    "rss_feed_template",
    "rtorrent",
    "rtsp_to_webrtc",
    "ruckus_unleashed",
    "russound_rnet",
    "ruuvi_gateway",
    "ruuvitag_ble",
    "rympro",
    "sabnzbd",
    "saj",
    "samsungtv",
    "sanix",
    "satel_integra",
    "schlage",
    "schluter",
    "scrape",
    "screenlogic",
    "scsgate",
    "season",
    "sendgrid",
    "sense",
    "sensibo",
    "sensirion_ble",
    "sensorpro",
    "sensorpush",
    "sensoterra",
    "sentry",
    "senz",
    "serial",
    "serial_pm",
    "sesame",
    "seven_segments",
    "seventeentrack",
    "sfr_box",
    "sharkiq",
    "shell_command",
    "shelly",
    "shodan",
    "shopping_list",
    "sia",
    "sigfox",
    "sighthound",
    "signal_messenger",
    "simplefin",
    "simplepush",
    "simplisafe",
    "simulated",
    "sinch",
    "sisyphus",
    "sky_hub",
    "sky_remote",
    "skybeacon",
    "skybell",
    "slack",
    "sleepiq",
    "slide",
    "slimproto",
    "sma",
    "smappee",
    "smart_meter_texas",
    "smartthings",
    "smarttub",
    "smarty",
    "smhi",
    "smlight",
    "sms",
    "smtp",
    "snapcast",
    "snips",
    "snmp",
    "snooz",
    "solaredge",
    "solaredge_local",
    "solax",
    "soma",
    "somfy_mylink",
    "sonarr",
    "songpal",
    "sonos",
    "sony_projector",
    "soundtouch",
    "spaceapi",
    "spc",
    "speedtestdotnet",
    "spider",
    "splunk",
    "spotify",
    "sql",
    "squeezebox",
    "srp_energy",
    "ssdp",
    "starline",
    "starlingbank",
    "starlink",
    "startca",
    "statistics",
    "statsd",
    "steam_online",
    "steamist",
    "stiebel_eltron",
    "stream",
    "streamlabswater",
    "subaru",
    "sun",
    "sunweg",
    "supervisord",
    "supla",
    "surepetcare",
    "swiss_hydrological_data",
    "swiss_public_transport",
    "swisscom",
    "switch_as_x",
    "switchbee",
    "switchbot",
    "switchbot_cloud",
    "switcher_kis",
    "switchmate",
    "syncthing",
    "syncthru",
    "synology_chat",
    "synology_dsm",
    "synology_srm",
    "syslog",
    "system_bridge",
    "systemmonitor",
    "tado",
    "tailscale",
    "tailwind",
    "tami4",
    "tank_utility",
    "tankerkoenig",
    "tapsaff",
    "tasmota",
    "tautulli",
    "tcp",
    "technove",
    "ted5000",
    "telegram",
    "telegram_bot",
    "tellduslive",
    "tellstick",
    "telnet",
    "temper",
    "template",
    "tensorflow",
    "tesla_fleet",
    "tesla_wall_connector",
    "teslemetry",
    "tessie",
    "tfiac",
    "thermobeacon",
    "thermopro",
    "thermoworks_smoke",
    "thethingsnetwork",
    "thingspeak",
    "thinkingcleaner",
    "thomson",
    "thread",
    "threshold",
    "tibber",
    "tikteck",
    "tile",
    "tilt_ble",
    "time_date",
    "tmb",
    "tod",
    "todoist",
    "tolo",
    "tomato",
    "tomorrowio",
    "toon",
    "torque",
    "touchline",
    "touchline_sl",
    "tplink",
    "tplink_lte",
    "tplink_omada",
    "traccar",
    "traccar_server",
    "tractive",
    "tradfri",
    "trafikverket_camera",
    "trafikverket_ferry",
    "trafikverket_train",
    "trafikverket_weatherstation",
    "transmission",
    "transport_nsw",
    "travisci",
    "trend",
    "triggercmd",
    "tuya",
    "twilio",
    "twilio_call",
    "twilio_sms",
    "twinkly",
    "twitch",
    "twitter",
    "ubus",
    "uk_transport",
    "ukraine_alarm",
    "unifi",
    "unifi_direct",
    "unifiled",
    "unifiprotect",
    "universal",
    "upb",
    "upc_connect",
    "upcloud",
    "upnp",
    "uptime",
    "uptimerobot",
    "usb",
    "usgs_earthquakes_feed",
    "utility_meter",
    "uvc",
    "v2c",
    "vallox",
    "vasttrafik",
    "velux",
    "venstar",
    "vera",
    "verisure",
    "versasense",
    "version",
    "vesync",
    "viaggiatreno",
    "vilfo",
    "vivotek",
    "vizio",
    "vlc",
    "vlc_telnet",
    "vodafone_station",
    "voicerss",
    "voip",
    "volkszaehler",
    "volumio",
    "volvooncall",
    "vulcan",
    "vultr",
    "w800rf32",
    "wake_on_lan",
    "wallbox",
    "waqi",
    "waterfurnace",
    "watson_iot",
    "watson_tts",
    "watttime",
    "waze_travel_time",
    "weatherflow",
    "weatherflow_cloud",
    "weatherkit",
    "webmin",
    "webostv",
    "weheat",
    "wemo",
    "whirlpool",
    "whois",
    "wiffi",
    "wilight",
    "wirelesstag",
    "withings",
    "wiz",
    "wled",
    "wmspro",
    "wolflink",
    "workday",
    "worldclock",
    "worldtidesinfo",
    "worxlandroid",
    "ws66i",
    "wsdot",
    "wyoming",
    "x10",
    "xbox",
    "xeoma",
    "xiaomi",
    "xiaomi_aqara",
    "xiaomi_ble",
    "xiaomi_miio",
    "xiaomi_tv",
    "xmpp",
    "xs1",
    "yale",
    "yale_smart_alarm",
    "yalexs_ble",
    "yamaha",
    "yamaha_musiccast",
    "yandex_transport",
    "yandextts",
    "yardian",
    "yeelight",
    "yeelightsunflower",
    "yi",
    "yolink",
    "youless",
    "youtube",
    "zabbix",
    "zamg",
    "zengge",
    "zeroconf",
    "zerproc",
    "zestimate",
    "zeversolar",
    "zha",
    "zhong_hong",
    "ziggo_mediabox_xl",
    "zodiac",
    "zoneminder",
    "zwave_js",
    "zwave_me",
]

NO_QUALITY_SCALE = [
    *{platform.value for platform in Platform},
    "api",
    "application_credentials",
    "auth",
    "automation",
    "blueprint",
    "config",
    "configurator",
    "counter",
    "default_config",
    "device_automation",
    "device_tracker",
    "diagnostics",
    "ffmpeg",
    "file_upload",
    "frontend",
    "hardkernel",
    "hardware",
    "history",
    "homeassistant",
    "homeassistant_alerts",
    "homeassistant_green",
    "homeassistant_hardware",
    "homeassistant_sky_connect",
    "homeassistant_yellow",
    "image_upload",
    "input_boolean",
    "input_button",
    "input_datetime",
    "input_number",
    "input_select",
    "input_text",
    "intent_script",
    "intent",
    "logbook",
    "logger",
    "lovelace",
    "media_source",
    "my",
    "onboarding",
    "panel_custom",
    "proxy",
    "python_script",
    "raspberry_pi",
    "recovery_mode",
    "repairs",
    "schedule",
    "script",
    "search",
    "system_health",
    "system_log",
    "tag",
    "timer",
    "trace",
    "webhook",
    "websocket_api",
    "zone",
]

SCHEMA = vol.Schema(
    {
        vol.Required("rules"): vol.Schema(
            {
                vol.Optional(rule.name): vol.Any(
                    vol.In(["todo", "done"]),
                    vol.Schema(
                        {
                            vol.Required("status"): vol.In(["todo", "done"]),
                            vol.Optional("comment"): str,
                        }
                    ),
                    vol.Schema(
                        {
                            vol.Required("status"): "exempt",
                            vol.Required("comment"): str,
                        }
                    ),
                )
                for rule in ALL_RULES
            }
        )
    }
)


def validate_iqs_file(config: Config, integration: Integration) -> None:
    """Validate quality scale file for integration."""
    if not integration.core:
        return

    declared_quality_scale = QUALITY_SCALE_TIERS.get(integration.quality_scale)

    iqs_file = integration.path / "quality_scale.yaml"
    has_file = iqs_file.is_file()
    if not has_file:
        if (
            integration.domain not in INTEGRATIONS_WITHOUT_QUALITY_SCALE_FILE
            and integration.domain not in NO_QUALITY_SCALE
            and integration.integration_type != "virtual"
        ):
            integration.add_error(
                "quality_scale",
                "Quality scale definition not found. New integrations are required to at least reach the Bronze tier.",
            )
            return
        if declared_quality_scale is not None:
            integration.add_error(
                "quality_scale",
                "Quality scale definition not found. Integrations that set a manifest quality scale must have a quality scale definition.",
            )
            return
        return
    if integration.integration_type == "virtual":
        integration.add_error(
            "quality_scale",
            "Virtual integrations are not allowed to have a quality scale file.",
        )
        return
    if integration.domain in NO_QUALITY_SCALE:
        integration.add_error(
            "quality_scale",
            "This integration is not supposed to have a quality scale file.",
        )
        return
    if integration.domain in INTEGRATIONS_WITHOUT_QUALITY_SCALE_FILE:
        integration.add_error(
            "quality_scale",
            "Quality scale file found! Please remove from script/hassfest/quality_scale.py",
        )
        return
    name = str(iqs_file)

    try:
        data = load_yaml_dict(name)
    except HomeAssistantError:
        integration.add_error("quality_scale", "Invalid quality_scale.yaml")
        return

    try:
        SCHEMA(data)
    except vol.Invalid as err:
        integration.add_error(
            "quality_scale", f"Invalid {name}: {humanize_error(data, err)}"
        )

    rules_done = set[str]()
    rules_met = set[str]()
    for rule_name, rule_value in data.get("rules", {}).items():
        status = rule_value["status"] if isinstance(rule_value, dict) else rule_value
        if status not in {"done", "exempt"}:
            continue
        rules_met.add(rule_name)
        if status == "done":
            rules_done.add(rule_name)

    for rule_name in rules_done:
        if (validator := VALIDATORS.get(rule_name)) and (
            errors := validator.validate(config, integration, rules_done=rules_done)
        ):
            for error in errors:
                integration.add_error("quality_scale", f"[{rule_name}] {error}")
            integration.add_error("quality_scale", RULE_URL.format(rule_name=rule_name))

    # An integration must have all the necessary rules for the declared
    # quality scale, and all the rules below.
    if declared_quality_scale is None:
        return

    for scale in ScaledQualityScaleTiers:
        if scale > declared_quality_scale:
            break
        required_rules = set(SCALE_RULES[scale])
        if missing_rules := (required_rules - rules_met):
            friendly_rule_str = "\n".join(
                f"  {rule}: todo" for rule in sorted(missing_rules)
            )
            integration.add_error(
                "quality_scale",
                f"Quality scale tier {scale.name.lower()} requires quality scale rules to be met:\n{friendly_rule_str}",
            )


def validate(integrations: dict[str, Integration], config: Config) -> None:
    """Handle YAML files inside integrations."""
    for integration in integrations.values():
        validate_iqs_file(config, integration)
