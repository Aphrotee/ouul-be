#!/usr/bin/env python3

"""Module for generating custom html templates for specific emails"""

import time
import datetime

def verificaiton_otp_html(otp: str):
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Onboarding Verification</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .email-container {
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                padding: 20px;
                border: 1px solid #dddddd;
                border-radius: 5px;
            }
            .otp {
                font-size: 24px;
            }
            h1 {
                color: #000000;
                font-size: 24px;
                margin-bottom: 20px;
            }
            p {
                font-size: 16px;
                color: #333333;
                line-height: 1.6;
            }
            .footer {
                margin-top: 40px;
                font-size: 14px;
                color: #777777;
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <p>Hello,</p>
            <p>Thank you for signing up to Ouul!</p>

            <p>To complete the signup proess, please use the following One-Time-Pin.</p>

            <p><strong class="otp">o-t-p</strong><br>

            <p>Please note that this OTP will expire by expiry-time, please ensure to use it before that time.</p>

            <p>Thanks.<br>
            Ouul company</p>

            <div class="footer">
                <p>&copy; year, Ouul. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>"""
    return content\
    .replace("o-t-p", otp)\
    .replace("expiry-time", str(datetime.datetime.fromtimestamp(int(time.time()+600)).strftime('%a %d %b %Y, %I:%M:%S%p')))\
    .replace("year", str(datetime.datetime.now().year))

def pin_reset_otp_html(otp: str):
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PIN Reset</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .email-container {
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                padding: 20px;
                border: 1px solid #dddddd;
                border-radius: 5px;
            }
            .otp {
                font-size: 24px;
            }
            h1 {
                color: #000000;
                font-size: 24px;
                margin-bottom: 20px;
            }
            p {
                font-size: 16px;
                color: #333333;
                line-height: 1.6;
            }
            .footer {
                margin-top: 40px;
                font-size: 14px;
                color: #777777;
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <p>Hello,</p>
            <p>You made a request to reset your Ouul PIN.</p>
            <p>If this wasn't you, please ignore this eamil.</p>

            <p>To complete the PIN reset proess, please use the following One-Time-Pin.</p>

            <p><strong class="otp">o-t-p</strong><br>

            <p>Please note that this OTP will expire by expiry-time, please ensure to use it before that time.</p>

            <p>Thanks.<br>
            Ouul company</p>

            <div class="footer">
                <p>&copy; year, Ouul. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>"""
    return content\
    .replace("o-t-p", otp)\
    .replace("expiry-time", str(datetime.datetime.fromtimestamp(int(time.time()+600)).strftime('%a %d %b %Y, %I:%M:%S%p')))\
    .replace("year", str(datetime.datetime.now().year))

def password_reset_otp_html(otp: str):
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .email-container {
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                padding: 20px;
                border: 1px solid #dddddd;
                border-radius: 5px;
            }
            .otp {
                font-size: 24px;
            }
            h1 {
                color: #000000;
                font-size: 24px;
                margin-bottom: 20px;
            }
            p {
                font-size: 16px;
                color: #333333;
                line-height: 1.6;
            }
            .footer {
                margin-top: 40px;
                font-size: 14px;
                color: #777777;
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <p>Hello,</p>
            <p>You made a request to reset your Ouul password.</p>
            <p>If this wasn't you, please ignore this eamil.</p>

            <p>To complete the password reset proess, please use the following One-Time-Pin.</p>

            <p><strong class="otp">o-t-p</strong><br>

            <p>Please note that this OTP will expire by expiry-time, please ensure to use it before that time.</p>

            <p>Thanks.<br>
            Ouul company</p>

            <div class="footer">
                <p>&copy; year, Ouul. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>"""
    return content\
    .replace("o-t-p", otp)\
    .replace("expiry-time", str(datetime.datetime.fromtimestamp(int(time.time()+600)).strftime('%a %d %b %Y, %I:%M:%S%p')))\
    .replace("year", str(datetime.datetime.now().year))