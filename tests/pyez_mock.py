"""PyEZ Device Mock
:Author:  Christian Giese
:Date:    08/03/2016
:Based on: https://github.com/GIC-de/Juniper-PyEZ-Unit-Testing.git
"""
from __future__ import unicode_literals
from mock import MagicMock, patch
from jnpr.junos import Device
from ncclient.manager import Manager, make_device_handler
from ncclient.transport import SSHSession
from ncclient.xml_ import NCElement
import os


# ------------------------------------------------------------------------------
# pytest fixtures
# ------------------------------------------------------------------------------

def rpc_reply_dict():
    """Dynamic Generated rpc-replys"""
    return {}


@patch('ncclient.manager.connect')
def mocked_device(rpc_reply_dict, mock_connect):
    """Juniper PyEZ Device Fixture"""
    def mock_manager(*args, **kwargs):
        if 'device_params' in kwargs:
            # open connection
            device_params = kwargs['device_params']
            device_handler = make_device_handler(device_params)
            session = SSHSession(device_handler)
            return Manager(session, device_handler)
        elif args:
            # rpc request
            rpc_request = args[0].tag
            rpc_command = str(args[0].text)
            rpc_command = rpc_command.strip()
            rpc_command = rpc_command.replace(" ", "_")
            if rpc_request in rpc_reply_dict:
                xml = rpc_reply_dict[rpc_request]
            elif 'dir' in rpc_reply_dict:
                fname = os.path.join(rpc_reply_dict['dir'], 'rpc-reply', rpc_command, rpc_request + '.xml')
                with open(fname, 'r') as f:
                    xml = f.read()
            else:
                _rpc_reply_dict['dir']
                fname = os.path.join(os.path.dirname(__file__), 'rpc-reply', rpc_command, rpc_request + '.xml')
                with open(fname, 'r') as f:
                    xml = f.read()
            rpc_reply = NCElement(xml, dev._conn._device_handler.transform_reply())
            return rpc_reply
    mock_connect.side_effect = mock_manager
    dev = Device(host='1.1.1.1', user='juniper', gather_facts=False)
    dev.open()
    dev._conn.rpc = MagicMock(side_effect=mock_manager)
    return dev
