import time
import os
import subprocess
import logging
import logging.handlers
import yaml

# Core Paths
TEMP_FOLDER_PATH = os.path.expanduser("~")
CONNECT_FOLDER_PATH = TEMP_FOLDER_PATH + "/.core/"
DIAG_FOLDER_PATH = CONNECT_FOLDER_PATH + "diagnostics/"
CONFIG_FOLDER_PATH = CONNECT_FOLDER_PATH + "configs/"

CONFIG_PATH = CONFIG_FOLDER_PATH + "config.yaml"
SYSTEM_PATH = CONNECT_FOLDER_PATH + "system.yaml"
MONITOR_PATH = CONNECT_FOLDER_PATH + "monitor.yaml"
GEOLOCATION_PATH = CONNECT_FOLDER_PATH + "geolocation.yaml"
DIAG_FILE_PATH = DIAG_FOLDER_PATH + "diagnostic.yaml"

# Test App Paths
APP_USER_PATH = os.path.expanduser("~")
APP_TEMP_PATH = f"{APP_USER_PATH}/.test_device-monitor-app/"
APP_LOG_PATH = f"{APP_TEMP_PATH}/logs/"
APP_MONITOR_PATH = f"{APP_TEMP_PATH}/monitor"

PERIOD = 60*60

if not os.path.exists(APP_TEMP_PATH):
    os.mkdir(APP_TEMP_PATH)

if not os.path.exists(APP_LOG_PATH):
    os.mkdir(APP_LOG_PATH)

LOG_FORMAT = "%(asctime)s --> %(filename)-18s %(levelname)-8s %(message)s"
logger = logging.getLogger("test_device-monitor-app")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT)
log_file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=APP_LOG_PATH+"log", when="midnight", backupCount=6
)

# log handler (root)
log_file_handler.setFormatter(formatter)
log_file_handler.set_name("log_handler")
logger.addHandler(log_file_handler)


def read_yaml_all(file):
    with open(file) as file_object:
        data = yaml.safe_load(file_object)
        return data or {}


def shell_command(command, timeout=45):
    try:
        com = command.split(" ")
        cp = subprocess.run(
            com,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
    except Exception as error:
        logger.error("Message: %s", error)
        return ("", "", 1)
    else:
        return (cp.stdout, cp.stderr, cp.returncode)


if __name__ == "__main__":
    logger.info("Started")

    while True:
        # Get monitor and system data from CORE
        monitor_data = read_yaml_all(MONITOR_PATH)
        geolocation_data = read_yaml_all(GEOLOCATION_PATH)

        if monitor_data == {} or geolocation_data == {}:
            logger.error("Monitor or Geolocation data is empty")
            continue

        test_res = "No data"

        # Speedtest
        logger.info("Speed Test running...")
        try:
            output = shell_command("speedtest-cli --simple")
        except:
            logger.error("Error in speedtest-cli")
            logger.info("Error: %s", output[1])
            logger.info("Return Code: %s", output[2])
        else:
            logger.info("Speed Test finished")
            test_result = output[0]

            for line in test_result.split("\n"):
                if "Ping" in line:
                    ping = line.split(" ")[1]
                elif "Download" in line:
                    download = line.split(" ")[1]
                elif "Upload" in line:
                    upload = line.split(" ")[1]

        active_interface = monitor_data["active_interface"]
        active_lte_tech = monitor_data["active_lte_tech"]
        signaL_quality = monitor_data["signal_quality"]
        roaming_operator = monitor_data["roaming_operator"]

        test_res = f"TS:{time.strftime('%Y-%m-%d %H:%M:%S')};"
        test_res += f"Active Int:{active_interface};"
        test_res += f"LTE Tech:{active_lte_tech};"
        test_res += f"Signal Quality:{signaL_quality};"
        test_res += f"Roaming Operator:{roaming_operator};"
        test_res += f"Ping:{ping};"
        test_res += f"Download:{download};"
        test_res += f"Upload:{upload};"

        # get cpu temperature of raspberry pi
        logger.info("CPU Temperature running...")
        try:
            output = shell_command("sudo vcgencmd measure_temp")
        except:
            logger.error("Error in vcgencmd measure_temp")
        else:
            logger.info("CPU Temperature finished")
            cpu_temp = output[0].split("=")[1].split("'")[0]
            test_res += f"CPU Temp:{cpu_temp};"

        for data in geolocation_data:
            single_data = f"{data}:{geolocation_data[data]};"
            test_res += f"{single_data}"

        test_res += "\n"

        #print(test_res)

        with open(APP_MONITOR_PATH, 'a') as app_file:
            app_file.write(test_res)

        time.sleep(PERIOD)
        