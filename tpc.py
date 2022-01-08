# Based on http://domoticx.com/kaku-tpc-300-laten-schakelen-via-linux/

import usb.core
import usb.util

# TPC-300
dev = usb.core.find(idVendor=0xFEFF, idProduct=0x0802)

if dev is None:
    raise ValueError("Device not found")

print("%r" % (dev,))

if dev.is_kernel_driver_active(0) is True:
    dev.detach_kernel_driver(0)
    print("Now reading data")
dev.set_configuration()

cfg = dev.get_active_configuration()
interface_number = cfg[(0, 0)].bInterfaceNumber

intf = usb.util.find_descriptor(
    cfg,
    bInterfaceNumber=interface_number,
)

ep = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
    == usb.util.ENDPOINT_OUT,
)
assert ep is not None


def control_channel(channel, state):
    assert 0 <= channel <= 255
    result = [0x5A, channel, 0x23 if state else 1, 0x05]
    ep.write(result)
