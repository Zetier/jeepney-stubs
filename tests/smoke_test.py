import jeepney.io.blocking
import jeepney
from jeepney.low_level import Message
from jeepney.wrappers import DBusAddress, Properties, new_method_call

from typing_extensions import assert_type

system_bus = jeepney.io.blocking.open_dbus_connection("SYSTEM")
props: Properties = Properties(jeepney.DBusAddress("/my/magic/path"))

_ty1 = assert_type(props.get(name="prop1"), Message)
_ty2 = assert_type(system_bus, jeepney.io.blocking.DBusConnection)

# This is the example from the jeepney docs
notifications = DBusAddress('/org/freedesktop/Notifications',
                            bus_name='org.freedesktop.Notifications',
                            interface='org.freedesktop.Notifications')

connection = jeepney.io.blocking.open_dbus_connection(bus='SESSION')

# Construct a new D-Bus message. new_method_call takes the address, the
# method name, the signature string, and a tuple of arguments.
msg = new_method_call(notifications, 'Notify', 'susssasa{sv}i',
                      ('jeepney_test',  # App name
                       0,   # Not replacing any previous notification
                       '',  # Icon
                       'Hello, world!',  # Summary
                       'This is an example notification from Jeepney',
                       [], {},  # Actions, hints
                       -1,      # expire_timeout (-1 = default)
                      ))

# Send the message and wait for the reply
reply = connection.send_and_get_reply(msg)
print('Notification ID:', reply.body[0]) # pyright: ignore[reportAny] # reply.body has Any as the values.
