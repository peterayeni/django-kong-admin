# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from enum import Enum, unique


@unique
class Plugins(Enum):
    ssl = 0
    keyauth = 1
    basicauth = 2
    oauth2 = 3
    ratelimiting = 4
    tcplog = 5
    udplog = 6
    filelog = 7
    httplog = 8
    cors = 9
    request_transformer = 10
    response_transformer = 11
    requestsizelimiting = 12

    @staticmethod
    def choices():
        return [(key, key) for key in sorted(Plugins.__members__.keys())]
