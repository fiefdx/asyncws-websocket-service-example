# -*- coding: utf-8 -*-
'''
Created on 2018-05-08
@summary: main application entrance
@author: YangHaitao
'''

import os
import logging
import asyncio

import asyncws

import logger


LOG = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 8081


@asyncio.coroutine
def test_websocket_service(websocket):
    LOG.info("open websocket path: %s", websocket.request.path)
    frame_id = 0
    frame_interval = 0.010  # ms
    data_path = "/home/breeze/Tmp/disk/2018-04-11_00:00:00/img"
    if "pcl_pointcloud" in websocket.request.path:
        frame_interval = 0.010
        data_path = "/home/breeze/Tmp/disk/2018-04-11_00:00:00/pcd"
    try:
        frame_names = os.listdir(data_path)
        frame_names.sort()
        frames_length = len(frame_names)
        while True:
            try:
                if frame_id == frames_length:
                    frame_id = 0
                LOG.debug("data_path: %s, frames_length: %s, frame_id: %s", data_path, frames_length, frame_id)
                fp = open(os.path.join(data_path, frame_names[frame_id]), "rb")
                content = fp.read()
                fp.close()
                yield from websocket.send(content, True)
                yield from asyncio.sleep(frame_interval)
                frame_id += 1
            except ConnectionResetError:
                LOG.info("websocket close, path: %s", websocket.request.path)
                break
    except Exception as e:
        LOG.exception(e)


if __name__ == "__main__":
    logger.config_logging(file_name = "test.log",
                          log_level = "DEBUG",
                          dir_name = "logs",
                          day_rotate = False,
                          when = "D",
                          interval = 1,
                          max_size = 20,
                          backup_count = 5,
                          console = True)
    LOG.info("websocket server start")
    LOG.info("service: %s:%s", HOST, PORT)
    server = asyncws.start_server(test_websocket_service, HOST, PORT)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
    LOG.info("websocket server end")
