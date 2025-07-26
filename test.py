from gi.repository import Gio

bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
print(bus.list_names())  # Можешь прямо из Python глянуть
