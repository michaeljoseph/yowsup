import argparse, sys, os, csv
import threading,time, base64

import click

from Yowsup.Common.utilities import Utilities
from Yowsup.Common.debugger import Debugger
from Yowsup.Common.constants import Constants
from Examples.CmdClient import WhatsappCmdClient
from Examples.EchoClient import WhatsappEchoClient
from Examples.ListenerClient import WhatsappListenerClient
from Yowsup.Registration.v2.existsrequest import WAExistsRequest as WAExistsRequestV2
from Yowsup.Registration.v2.coderequest import WACodeRequest as WACodeRequestV2
from Yowsup.Registration.v2.regrequest import WARegRequest as WARegRequestV2
from Yowsup.Contacts.contacts import WAContactsSyncRequest


DEFAULT_CONFIG = os.path.expanduser("~")+"/.yowsup/auth"
COUNTRIES_CSV = "countries.csv"

def resultToString(result):
        unistr = str if sys.version_info >= (3, 0) else unicode
        out = []
        for k, v in result.items():
                if v is None:
                        continue
                out.append("%s: %s" %(k, v.encode("utf-8") if type(v) is unistr else v))

        return "\n".join(out)


def getCredentials(config = DEFAULT_CONFIG):
    if os.path.isfile(config):
        f = open(config)
        phone = ""
        idx = ""
        pw = ""
        cc = ""
        try:
            for l in f:
                line = l.strip()
                if len(line) and line[0] not in ('#',';'):
                    prep = line.split('#', 1)[0].split(';', 1)[0].split('=', 1)

                    varname = prep[0].strip()
                    val = prep[1].strip()

                    if varname == "phone":
                        phone = val
                    elif varname == "id":
                        idx = val
                    elif varname =="password":
                        pw =val
                    elif varname == "cc":
                        cc = val
            return (cc, phone, idx, pw);
        except:
                pass

    return 0


def dissectPhoneNumber(phoneNumber):
    try:
        with open(COUNTRIES_CSV, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if len(row) == 3:
                    country, cc, mcc = row
                else:
                    country,cc = row
                    mcc = "000"
                try:
                    if phoneNumber.index(cc) == 0:
                        print("Detected cc: %s"%cc)
                        return (cc, phoneNumber[len(cc):])
                except ValueError:
                        continue
    except:
            pass
    return False

def main():
   credentials = getCredentials(args["config"] or DEFAULT_CONFIG)

    if credentials:
        countryCode, login, identity, password = credentials
        identity = Utilities.processIdentity(identity)
        password = base64.b64decode(bytes(password.encode('utf-8')))
        if countryCode:
            phoneNumber = login[len(countryCode):]
        else:
            dissected = dissectPhoneNumber(login)
            if not dissected:
                sys.exit("ERROR. Couldn't detect cc, you have to manually place it your config")
            countryCode, phoneNumber = dissected

def interactive(val):
    wa = WhatsappCmdClient(val, args['keepalive'] ,args['autoack'])
    wa.login(login, password)

@click.command()
@click.argument('recipient')
@click.argument('message')
def send(phone, message):
    wa = WhatsappEchoClient(phone, message, args['wait'])
    wa.login(login, password)

def receive():
    wa = WhatsappListenerClient(args['keepalive'], args['autoack'])
    wa.login(login, password)


def broadcast(phones, mess):
    phones = args["broadcast"][0]
    message = args["broadcast"][1]
    wa = WhatsappEchoClient(phones, message, args['wait'])
    wa.login(login, password)

def code():
    method = 'sms'
    wc = WACodeRequestV2(countryCode, phoneNumber, identity, method)
    result = wc.send()

def register(code)
    code = "".join(code.split('-'))
    wr = WARegRequestV2(countryCode, phoneNumber, code, identity)
    result = wr.send()

def exists():
    we = WAExistsRequestV2(countryCode, phoneNumber, identity)
    result = we.send()
    print(resultToString(result))

    if result["pw"] is not None:
            print("\n=========\nWARNING: %s%s's has changed by server to \"%s\", you must update your config file with the new password\n=========" %(countryCode, phoneNumber, result["pw"]))

def sync(contacts):
    contacts = args["sync"].split(',')
    wsync = WAContactsSyncRequest(login, password, contacts)
    print("Syncing %s contacts" % len(contacts))
    result = wsync.send()
    print(resultToString(result))
