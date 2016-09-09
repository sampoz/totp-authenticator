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

old_secrets = [['name', 'secret1'], ['name2', 'secret2']]


def pad_time():
    return str((30-gmtime()[5]/2)*"*" + gmtime()[5]/2 * ' ' )

def pad_to_max(to_pad, whole):
    max_length = 0
    print(whole)
    for tpl in whole:
        print(tpl)
        if len(tpl[0]) > max_length:
            max_length = len(tpl[0])
    while (len(to_pad) <= max_length):
        print(to_pad)
        to_pad = to_pad + ' '
    return to_pad

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    button = urwid.Button("Add new secret")
    urwid.connect_signal(button, 'click', add_new_secret, 'add')
    body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    for c in choices:
        digits = 6
        time_step = 30
        button = urwid.Button(pad_to_max(c[0], choices) + ': ' + pad_time() + TOTP(bytes(c[1]), digits, time_step).generate(time()))
        urwid.connect_signal(button, 'click', exit_on_q, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def add_new_secret(a, b):
    global timer_handle
    global main_loop
    main_loop.remove_alarm(timer_handle)
    original = main.original_widget
    name = urwid.Edit(('', u"Insert name of the new topt-token\n"))
    secret = urwid.Edit(('', u"Insert the secret\n"))
    done_btn = urwid.Button(u'Ok')
    urwid.connect_signal(done_btn, 'click', add_secret, [[name, secret]])
    main.original_widget = urwid.Filler(urwid.Pile([urwid.Pile([name, secret]),
        urwid.AttrMap(done_btn, None, focus_map='reversed')]))

def add_secret(self, parameters):
    global main_loop
    global timer_handle
    global old_secrets
    name = parameters[0][0].get_edit_text()
    secret = parameters[0][1].get_edit_text()
    old_secrets = old_secrets + [[name, secret]]
    timer_handle = main_loop.set_alarm_in(1, update_remaining_time)
    main.original_widget = menu('TOTP-authenticator', old_secrets)

def update_remaining_time(self, smt):
    global old_secrets
    global timer_handle
    main.original_widget = menu('TOTP-authenticator', old_secrets)
    timer_handle = main_loop.set_alarm_in(1, update_remaining_time)

palette = [
    ('banner', 'black', 'light gray'),
    ('streak', 'black', 'dark red'),
    ('bg', 'black', 'dark blue'),]

main = urwid.Padding(menu('TOTP-authenticator', old_secrets), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
                    align='center', width=('relative', 80),
                    valign='middle', height=('relative', 80),
    min_width=20, min_height=9)
timer_handle = None
main_loop = urwid.MainLoop(top, palette=[('reversed', 'standout', '')])
main_loop.set_alarm_in(1, update_remaining_time)
main_loop.run()
