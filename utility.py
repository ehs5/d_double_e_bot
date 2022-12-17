import configparser
from configparser import SectionProxy


# Returns config.ini file as list
def get_config_object(config_object_name: str) -> SectionProxy:
    config = configparser.ConfigParser()
    config.read("config.ini")
    config_object = config[config_object_name]
    return config_object


def add_to_txt_file(file_name: str, text: str) -> None:
    file = open(file_name, 'a')
    file.write(text)
    file.close()


def get_txt_file_as_list(file_name: str) -> list[str]:
    txt_file_as_list = open(file_name).read().splitlines()
    return txt_file_as_list
