# -*- coding: utf-8 -*-

import logging

import netifaces

from .base import IPDetector, AF_INET, AF_INET6, AF_UNSPEC
from ..common.six import ipaddress, ipnetwork

log = logging.getLogger(__name__)


def _default_interface():
    """
    Convenience function to return the default interface name for common
    operating systems.
    """
    import platform
    system = platform.system()
    if system == 'Linux':
        return 'eth0'
    elif system == 'Darwin':
        return 'en0'
    else:
        return None


class IPDetector_Iface(IPDetector):
    """
    IPDetector to detect any ip address of a local interface.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        @param options: dictionary

        available kwargs:

        iface: name of interface
        family: IP address family (default: INET, possible: INET6)
        netmask: netmask to be matched if multiple IPs on interface (default:
                none (match all)", example for teredo: "2001:0000::/32")
        """
        super(IPDetector_Iface, self).__init__(*args, **kwargs)

        self.opts_iface = kwargs.get('iface', _default_interface())
        self.opts_netmask = kwargs.get('netmask')

        # ensure an interface name was specified:
        if self.opts_iface is None:
            raise ValueError("No network interface specified!")
        # parse/validate given netmask:
        if self.opts_netmask is not None:  # if a netmask was given
            # This might fail here, but that's OK since we must avoid sending
            # an IP to the outside world that should be hidden (because in a
            # "private" netmask)
            self.netmask = ipnetwork(self.opts_netmask)
        else:
            self.netmask = None

    @staticmethod
    def names():
        return ("iface",)

    def can_detect_offline(self):
        """Returns true, as this detector only queries local data"""
        return True

    def _detect(self):
        """uses the netifaces module to detect ifconfig information"""
        theip = None
        try:
            if self.opts_family == AF_INET6:
                addrlist = netifaces.ifaddresses(self.opts_iface)[netifaces.AF_INET6]
            else:
                addrlist = netifaces.ifaddresses(self.opts_iface)[netifaces.AF_INET]
        except ValueError as exc:
            log.error("netifaces choked while trying to get network interface"
                      " information for interface '%s'", self.opts_iface,
                      exc_info=exc)
        else:  # now we have a list of addresses as returned by netifaces
            for pair in addrlist:
                try:
                    detip = ipaddress(pair['addr'])
                except (TypeError, ValueError) as exc:
                    log.debug("Found invalid IP '%s' on interface '%s'!?",
                              pair['addr'], self.opts_iface, exc_info=exc)
                    continue
                if self.netmask is not None:
                    if detip in self.netmask:
                        theip = pair['addr']
                    else:
                        continue
                else:
                    theip = pair['addr']
                break  # we use the first IP found
        # theip can still be None at this point!
        self.set_current_value(theip)
        return theip

    def detect(self):
        return self._detect()
