import urwid
import sched
import math
from oath_toolkit import TOTP
from time import time
from time import gmtime, strftime, sleep


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

digits = 6
time_step = 30
oath = TOTP(b'aaaaaa', digits, time_step)
one_time_password = oath.generate(time())

# Load old secrets

# Add new

old_secrets = [['name1', 'secret1'], ['name2', 'secret2']]


def pad_time():
    return str((30-gmtime()[5]/2)*"*" + gmtime()[5]/2 * ' ' )

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    # add-new
    button = urwid.Button("Add new secret")
    urwid.connect_signal(button, 'click', add_new_secret, 'add')
    body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    for c in choices:
        digits = 6
        time_step = 30
        button = urwid.Button(c[0] + pad_time() + TOTP(bytes(c[1]), digits, time_step).generate(time()))
        urwid.connect_signal(button, 'click', exit_on_q, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def add_new_secret(a, b):
    original = main.original_widget
    name = urwid.Edit(('', u"Insert name of the new topt-token\n"))
    secret = urwid.Edit(('', u"Insert the secret\n"))
    done = urwid.Button(u'Ok')
    urwid.connect_signal(done, 'click', add_secret, [[name, secret], original])
    main.original_widget = urwid.Filler(urwid.Pile([urwid.Pile([name, secret]),
        urwid.AttrMap(done, None, focus_map='reversed')]))

def add_secret(self, parameters):
    global old_secrets
    name = parameters[0][0].get_edit_text()
    secret = parameters[0][1].get_edit_text()
    old_secrets = old_secrets + [[name, secret]]
    print(old_secrets)
    main.original_widget = menu('TOTP-authenticator', old_secrets)

def update_remaining_time(self, smt):
    global old_secrets
    main.original_widget = menu('TOTP-authenticator', old_secrets)
    main_loop.set_alarm_in(1, update_remaining_time)

palette = [
    ('banner', 'black', 'light gray'),
    ('streak', 'black', 'dark red'),
    ('bg', 'black', 'dark blue'),]

main = urwid.Padding(menu('TOTP-authenticator', old_secrets), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 60),
    valign='middle', height=('relative', 60),
    min_width=20, min_height=9)

main_loop = urwid.MainLoop(top, palette=[('reversed', 'standout', '')])
main_loop.set_alarm_in(1, update_remaining_time)
main_loop.run()
