from datetime import datetime
import netifaces as ni
import time
import os

def timenow():
    now = datetime.now()  # Pega a data e hora atual
    formatted_time = now.strftime("[%H:%M:%S %Y-%m-%d]")
    return formatted_time

def get_default_gateway():
    default_gateway = None
    gws = ni.gateways()

    if 'default' in gws and ni.AF_INET in gws['default']:
        default_gateway = gws['default'][ni.AF_INET][0]

    return default_gateway

def find_path(*args):
    """
    @args: strings que representam pastas a serem percorridas
    @return: string com o caminho completo para a pasta desejada
    """
    abpath = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(abpath, '..')
    
    for arg in args:
        path = os.path.join(path, arg)
    return path

def debug(arg):
    """
    @arg: string a ser printada no console
    @return: None
    """
    print(f"{timenow()} {arg}")