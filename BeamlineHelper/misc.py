#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 15:22:42 2021

@author: kai
"""

class Commands:
    def __init__(self, command):
        self.command = command

    def minimize(self):
        command = self.command.replace(".", "").replace(",", "").split()
        out = ""
        for character in command:
            try:
                float(character)
                out += "$"
            except:
                out += character
            out += " "
        return out[:-1]

    def get_motors(self, list_of_motors):
        command = self.minimize().replace("$", "").split()
        motors = []
        for substring in command:
            for motor in list_of_motors:
                if substring.replace("_", "").lower() == motor.replace("_", "").lower():
                    motors.append(motor)
                    break
            if len(substring) == 1:  # try to guess appreviations
                motors.append(f"0{substring}")
        # try to guess appreviations
        for i, axis in enumerate(motors):
            if axis[0] == "0":
                for motor in list_of_motors:
                    if motor[0].lower() == axis[1].lower() and not motor in motors:
                        motors[i] = motor
                        break
        return motors
