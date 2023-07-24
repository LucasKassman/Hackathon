import logging
import requests



def get_my_ip():
    my_ip = None
    try:
        my_ip = requests.get("http://ifconfig.me").text
    except Exception as e:
        logging.exception("Failed to determine location!")
    return my_ip

