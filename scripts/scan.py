import platform
import psutil
import GPUtil
import wmi
import subprocess

from utils import *

class Scan:
    def __init__(self):
        self.data = {'system': {}, 'cpu': {}, 'memory': {}, 'gpu': {}, 'disk': {}, 'network': {}}

    def setup(self):
        # System
        debug("Loading System Information...")
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.name = platform.uname().node
        self.drivers = wmi.WMI().Win32_PnPSignedDriver()   
        self.current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
        self.motherboard = subprocess.check_output('wmic baseboard get product').decode().split('\n')[1].strip()
        self.motherboard_manufacturer = subprocess.check_output('wmic baseboard get manufacturer').decode().split('\n')[1].strip()
        self.motherboard_serial = subprocess.check_output('wmic baseboard get serialnumber').decode().split('\n')[1].strip()
        self.motherboard_name = subprocess.check_output('wmic baseboard get name').decode().split('\n')[1].strip()     

        # CPU
        debug("Loading CPU Information...")
        self.cpu = platform.processor()
        self.cpu_clock = psutil.cpu_freq()
        self.cpu_cores = psutil.cpu_count()
        self.cpu_current_clock = "{}{}".format(self.cpu_clock.current / 1000, "GHz")
        self.cpu_min_clock = "{}{}".format(self.cpu_clock.min / 1000, "GHz")
        self.cpu_max_clock = "{}{}".format(self.cpu_clock.max / 1000, "GHz")
        self.cpu_percent = "{}{}".format(psutil.cpu_percent(), "%")
        self.architecture, self.sys = platform.architecture()

        # Memory
        debug("Loading Memory Information...")
        self.memory_info = psutil.virtual_memory()
        self.memory = "{}{}".format(round(self.memory_info.total / (1024 * 1024 * 1024)), "GB")
        self.memory_available = "{}{}".format(round(self.memory_info.available / (1024 * 1024 * 1024)), "GB")
        self.memory_percent = "{}{}".format(round(self.memory_info.percent), "%")
        self.memory_used = "{}{}".format(round(self.memory_info.used / (1024 * 1024 * 1024)), "GB")
        self.memory_free = "{}{}".format(round(self.memory_info.free / (1024 * 1024 * 1024)), "GB")

        # GPU
        debug("Loading GPU Information...")
        self.gpu = GPUtil.getGPUs()
        self.gpu_name = self.gpu[0].name
        self.gpu_memory = "{}{}".format(self.gpu[0].memoryTotal, "MB")
        self.gpu_memory_used = "{}{}".format(self.gpu[0].memoryUsed, "MB")
        self.gpu_temperature = "{}{}".format(self.gpu[0].temperature, "°C")

        # Main Disk
        debug("Loading Disk Information...")
        self.disk = psutil.disk_usage('/')
        self.disk_total = "{}{}".format(round(self.disk.total / (1024 * 1024 * 1024)), "GB")
        self.disk_used = "{}{}".format(round(self.disk.used / (1024 * 1024 * 1024)), "GB")
        self.disk_free = "{}{}".format(round(self.disk.free / (1024 * 1024 * 1024)), "GB")
        self.disk_percent = "{}{}".format(self.disk.percent, "%")

        # Other Disks ##TODO

        # Network
        debug("Loading Network Information...")
        self.network = psutil.net_if_addrs()
        self.ip_machine = self.network['Ethernet'][0].address
        self.ipv4 = self.network['Ethernet'][1].address
        self.ip_mask = self.network['Ethernet'][1].netmask
        self.ipv6 = self.network['Ethernet'][2].address
        self.temp_ipv6 = self.network['Ethernet'][3].address
        self.locallink_ipv6 = self.network['Ethernet'][4].address
        self.gateway = get_default_gateway()

        # Drivers
        debug("Loading Drivers Information...")
        self.drivers_data = [["Device", "Manufacturer", "DriverVersion", "DriverDate", "IsSigned"]]
        filled = []
        for driver in self.drivers:
            date = driver.DriverDate
            if driver.DeviceName != None and date != None and driver.DeviceName not in filled:
                date = f"{date[0:4]}-{date[4:6]}-{date[6:8]} {date[8:10]}:{date[10:12]}:{date[12:14]}"
                self.drivers_data.append([driver.DeviceName, driver.Manufacturer, driver.DriverVersion, date, driver.IsSigned])
                filled.append(driver.DeviceName)

    def update(self):
        debug("Updating Data...")
        self.data = {
            'system' : {'system': self.system, 'release': self.release, 'version': self.version, 'name': self.name, 'machine_id': self.current_machine_id},
            'cpu' : {'name': self.cpu, 'clock': self.cpu_current_clock, 'cores':self.cpu_cores, 'min_clock': self.cpu_min_clock, 'max_clock': self.cpu_max_clock, 'percent': self.cpu_percent, 'architecture': self.architecture},
            'memory' : {'total': self.memory, 'available': self.memory_available, 'percent': self.memory_percent, 'used': self.memory_used, 'free': self.memory_free},
            'gpu' : {'name': self.gpu_name, 'memory': self.gpu_memory, 'memory_used': self.gpu_memory_used, 'temperature': self.gpu_temperature},
            'disk' : {'total': self.disk_total, 'used': self.disk_used, 'free': self.disk_free, 'percent': self.disk_percent},
            'network' : {'ip_machine': self.ip_machine, 'ipv4': self.ipv4, 'ip_mask': self.ip_mask, 'gateway': self.gateway},
            'motherboard' : {'name': self.motherboard, 'manufacturer': self.motherboard_manufacturer, 'serial': self.motherboard_serial, 'product': self.motherboard_name},
            'drivers' : self.drivers_data
        }
    def get_space_on_disk(self):
        disk = psutil.disk_usage(os.environ['SystemDrive'])
        return disk.free

    def run(self):
        self.setup()
        self.update()
        debug("Scan Finished!")

if __name__ == '__main__':
    scan = Scan()
    scan.run()