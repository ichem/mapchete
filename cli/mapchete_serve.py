#!/usr/bin/env python

import os
import sys
import argparse
from flask import Flask, send_file, make_response
from functools import update_wrapper
import threading


from mapchete import *
from tilematrix import TilePyramid, MetaTilePyramid

import pkgutil

process_host = None

def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument("mapchete_file", type=str)
    parser.add_argument("--zoom", "-z", type=int, nargs='*', )
    parser.add_argument("--bounds", "-b", type=float, nargs='*')
    parser.add_argument("--log", action="store_true")
    parsed = parser.parse_args(args)

    try:
        print "preparing process ..."
        process_host = MapcheteHost(
            parsed.mapchete_file,
            zoom=parsed.zoom,
            bounds=parsed.bounds
            )
    except Exception as e:
        raise

    app = Flask(__name__)


    metatile_cache = {}
    metatile_lock = threading.Lock()

    @app.route('/', methods=['GET'])
    def get_tasks():
        index_html = pkgutil.get_data('static', 'index.html')
        return index_html

    tile_base_url = '/wmts_simple/1.0.0/mapchete/default/WGS84/'
    @app.route(
        tile_base_url+'<int:zoom>/<int:row>/<int:col>.png',
        methods=['GET']
        )
    def get_tile(zoom, row, col):
        tileindex = str(zoom), str(row), str(col)
        tile = (zoom, row, col)
        try:
            metatile = process_host.tile_pyramid.tiles_from_bbox(
                process_host.tile_pyramid.tilepyramid.tile_bbox(*tile),
                tile[0]
                )[0]
            with metatile_lock:
                metatile_event = metatile_cache.get(metatile)
                if not metatile_event:
                    metatile_cache[metatile] = threading.Event()

            if metatile_event:
                metatile_event.wait()

            try:
                image = process_host.get_tile(tile)
            except:
                raise
            finally:
                if not metatile_event:
                    metatile_event = metatile_cache.get(metatile)
                    del metatile_cache[metatile]
                    metatile_event.set()

            # set no-cache header:
            resp = make_response(image)
            resp.cache_control.no_cache = True
            return resp
        except Exception as e:
            return Exception

    app.run(threaded=True, debug=True)


if __name__ == '__main__':
    main(sys.argv[1:])
