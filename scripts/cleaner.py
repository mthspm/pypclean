import os
import shutil
from utils import *
from settings import *
from scan import Scan
import json
from pathlib import Path

class Cleaner:
    """
    Cleaner Class
    @param: None
    @return: None
    @methods:
        clean_folder(path, userprofile=False, systemdrive=False) -> dict, {'removed_files': [], 'memory_clean': 0}
        clean_temp() -> None
        clean_logs() -> None
        clean_install() -> None
        clean_downloads() -> None
        clean_cache() -> None
    """

    def __init__(self):
        self.scan = Scan()
        self.methods = {
            'cache' : self.clean_cache,
            'temp' : self.clean_temp,
            'logs' : self.clean_logs,
            'install' : self.clean_install,
            'downloads' : self.clean_downloads
        }
        self.cleaners = {}
        self.load_cleaners()

    def load_cleaners(self):
        father_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(father_directory)
        cleaners_path = os.path.join(parent_directory, 'cleaners')
        
        try:
            for cleaner in os.listdir(cleaners_path):
                with open(os.path.join(cleaners_path, cleaner), 'r') as file:
                    data = json.load(file)
                    self.cleaners[data['appname']] = data['paths']
        except Exception as e:
            debug(f"Erro ao carregar limpadores de arquivos... {e}")


    def run(self, key):
        try:
            self.methods[key]()
        except Exception as e:
            debug(f"Erro ao executar {key}... {e}")

    def clean_folder(self, path, userprofile=False, systemdrive=False):
        """_summary_

        Args:
            path (_type_): path to folder
            userprofile (bool, optional): configure the path to C:/user/nameuser/path. Defaults to False.
            systemdrive (bool, optional): configure the path to C:/path. Defaults to False.

        Returns:
            _type_: _description_
        """
        # Get path
        data = {'removed_files': [],
                'memory_clean': 0}
        start_memory = self.scan.get_space_on_disk()
        try:
            if userprofile:
                temp_path = os.path.join(os.environ['USERPROFILE'], path)
            elif systemdrive:
                temp_path = os.path.join((os.environ['SystemDrive'] + '\\'), path)
            else:
                temp_path = path
            
        except Exception as e:
            debug(f"Erro ao obter path de {path}...", e)
        
        # Check if temp_path exists
        if os.path.exists(temp_path):
            # Pick all files and folders inside temp_path
            for temp_file in os.listdir(temp_path):
                # Grab file path
                file_path = os.path.join(temp_path, temp_file)
                # Try to remove file
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        data['removed_files'].append(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except PermissionError as e:
                    debug(e)
            
            end_memory = self.scan.get_space_on_disk()
            data['memory_clean'] = (start_memory - end_memory)/1000000*-1 # in MB
            return data
        else:
            debug(f"Path {temp_path} não existe!")

    def clean_temp(self):
        files_deleted = 0
        memory_clean = 0

        # Windows Temp
        for path in self.cleaners['windows'].values():
            c = self.clean_folder(path, systemdrive=True)
            if c:
                files_deleted += len(c['removed_files'])
                memory_clean += c['memory_clean']

        # User Temp
        for path in self.cleaners['temp'].values():
            c = self.clean_folder(path, userprofile=True)
            if c:
                files_deleted += len(c['removed_files'])
                memory_clean += c['memory_clean']

        debug(f"Memoria liberada: {memory_clean}mb - temp")
        debug(f"Total de arquivos deletados pela varredura: {files_deleted}")

    def clean_logs(self):
        pass

    def clean_install(self):
        pass

    def clean_downloads(self):
        d1 = self.clean_folder('Downloads', userprofile=True)
        debug(f"Memoria liberada: {d1['memory_clean']}mb - downloads")
        debug(f"Total de arquivos deletados pela varredura: {len(d1['removed_files'])}")


    def clean_cache(self):
        files_deleted = 0
        memory_clean = 0
        
        #Chrome Cache
        for path in self.cleaners['chrome'].values():
            c = self.clean_folder(path, userprofile=True)
            files_deleted += len(c['removed_files'])
            memory_clean += c['memory_clean']
        
        #Discord Cache
        for path in self.cleaners['discord'].values():
            c = self.clean_folder(path, userprofile=True)
            files_deleted += len(c['removed_files'])
            memory_clean += c['memory_clean']
        
        #Firefox Cache
        mozila_path = os.path.join(os.environ['APPDATA'], 'Mozilla\\Firefox\\Profiles')
        for profile in os.listdir(mozila_path):
            if os.path.isdir(os.path.join(mozila_path, profile)):
                for path in self.cleaners['firefox'].values():
                    c = self.clean_folder(os.path.join(mozila_path, profile, path))
                    if c:
                        files_deleted += len(c['removed_files'])
                        memory_clean += c['memory_clean']

        debug(f"Memoria liberada: {memory_clean}mb - cache")
        debug(f"Total de arquivos deletados pela varredura: {files_deleted}")

if __name__ == '__main__':
    cleaner = Cleaner()
    cleaner.run('temp')
    cleaner.run('cache')
    cleaner.run('downloads')
