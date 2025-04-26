#!/usr/bin/env python3

""" Module for generating 6-digit otp """
import random


def generate_otp():
    return str(random.randint(100000, 999999))
