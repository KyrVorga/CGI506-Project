from backup import backup
from center_view import center_view
from create_weather import create_weather
import bpy

if __name__ == "__main__":
    # backup.register()
    # center_view.register()
    # create_weather.register()

    minimal_layout = bpy.data.libraries.new(name="Minimal", internal=False)

    # Link the layout to the startup file
    bpy.context.screen.layout_library = minimal_layout
