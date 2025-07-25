
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.app import App
import requests
import json
from deutsche_bahn_api.station_helper import StationHelper
from datetime import datetime
import time

from win32timezone import now

station_helper = StationHelper()
stations = station_helper.stations_list

KV = """
<CustomMarker>:
    on_release: app.show_departures(self.station)

BoxLayout:
    orientation: "vertical"
    MapView:
        id: map_view
        lat: 48.137154
        lon: 11.575421
        zoom: 13

    Button:
        text: "Finish"
        size_hint_y: 0.1
        on_release: app.finish()
"""

class CustomMarker(MapMarkerPopup):
    station = None

class SearchAndGo(App):
    def build(self):
        self.root = Builder.load_string(KV)
        self.add_stops()
        return self.root

    def add_stops(self):
        map_view = self.root.ids.map_view
        print("Stationsdaten:", stations[:10])
        for station in stations:
            if hasattr(station, "IFOPT") and "de:09162" in station.IFOPT:
                try:
                    marker = CustomMarker(
                        lat=float(station.Breite.replace(",", ".")),
                        lon=float(station.Laenge.replace(",", "."))
                    )
                    marker.station = station
                    marker.add_widget(Label(text=station.NAME, color=[0, 0, 0, 1]))
                    map_view.add_widget(marker)
                except Exception as e:
                    print(f"Fehler beim Hinzufügen eines Markers: {e}")

    def show_departures(self, station):
        try:
            response = requests.get(
                f"https://5000-vermaunzt-dbsearchandgo-lt4qc7rbj3s.ws-eu116.gitpod.io/departures?station={station.NAME}"
            )
            response.raise_for_status()
            departures = response.json()
        except Exception as e:
            print(f"Fehler beim Abrufen der Abfahrten: {e}")
            departures = []

        if not departures:
            popup = Popup(
                title=f"Abfahrten - {station.NAME}",
                content=Label(text="Keine Abfahrtsdaten verfügbar.", color=[1, 1, 1, 1]),
                size_hint=(0.8, 0.8),
            )
            popup.open()
            return

        departure_text = f"Abfahrten für {station.NAME}:
"
        sorted_deps = sorted(departures, key=lambda x: datetime.strptime(x['departure'], '%y%m%d%H%M'))
        for dep in sorted_deps[:10]:
            try:
                departure_text += f"{dep['train_type']} {dep.get('train_line', dep.get('train_number', ''))} -> "
                departure_text += f"{dep['stations'].split('|')[-1]} um "
                departure_text += f"{datetime.strptime(dep['departure'], '%y%m%d%H%M').strftime('%H:%M')}
"
            except:
                departure_text += "Fehler beim Anzeigen dieser Abfahrt
"

        popup = Popup(
            title=f"Abfahrten - {station.NAME}",
            content=Label(text=departure_text, color=[1, 1, 1, 1]),
            size_hint=(0.8, 0.8),
        )
        popup.open()

    def finish(self):
        print("App beendet.")
        self.stop()

if __name__ == "__main__":
    SearchAndGo().run()
