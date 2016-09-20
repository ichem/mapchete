#!/usr/bin/env python

from mapchete import MapcheteProcess

class Process(MapcheteProcess):
    """Main process class"""
    def __init__(self, **kwargs):
        """Process initialization"""
        # init process
        MapcheteProcess.__init__(self, **kwargs)
        self.identifier = "my_process_id",
        self.title="My long process title",
        self.version = "0.1",
        self.abstract="short description on what my process does"

    def execute(self):
        """User defined process"""
        # insert magic here

        # Reading and writing data works like this:
        with self.open(
            self.params["input_files"]["raster_file"],
            resampling="bilinear"
            ) as my_raster_rgb_file:
            if my_raster_rgb_file.is_empty():
                return "empty" # this assures a transparent tile instead of a
                # pink error tile is returned when using mapchete_serve
            r, g, b = my_raster_rgb_file.read()

        self.write((r, g, b))
