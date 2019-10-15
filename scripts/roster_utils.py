from dataclasses import dataclass
from typing import List


@dataclass
class DeviceInfo:
    username: str
    hostname: str


class CouldNotReadDeviceList(Exception):
    pass


def get_device_list(input_file) -> List[DeviceInfo]:
    device_list = []

    try:
        # TODO: Check if file exists and has entries
        with open(input_file, 'r') as filestream:

            count = 0

            for line in filestream:
                device_info = line.split(',')
                if len(device_info) != 2:
                    msg = 'Invalid line %r in %s' % (line, input_file)
                    raise CouldNotReadDeviceList(msg)
                count += 1

                device_info = [item.rstrip() for item in device_info]

                d = DeviceInfo(username=device_info[0], hostname=device_info[1])
                device_list.append(d)

        if len(device_list) == 0:
            msg = 'Could not find any device in %s' % input_file
            raise CouldNotReadDeviceList(msg)

        return device_list

    except IOError as e:
        msg = 'Could not read from %s' % input_file
        raise CouldNotReadDeviceList(msg) from e


def show_status(device_list: List[DeviceInfo], results: List[str]):
    print('\t {:<4}{:<20}|{:<4}{:<20} '.format('=' * 4, '=' * 20, '=' * 4, '=' * 20))
    print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format('', 'Device', '', 'Status'))
    print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format('=' * 4, '=' * 20, '=' * 4, '=' * 20))

    for (res, device) in zip(results, device_list):
        status = res.rstrip()

        print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format('', device.hostname, '', status))

    print('\t {:<4}{:<20}|{:<4}{:<20} '.format('=' * 4, '=' * 20, '=' * 4, '=' * 20))
