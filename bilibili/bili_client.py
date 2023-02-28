import struct
import zlib
import asyncio
import json
import websockets
import requests
import time
import hashlib
import hmac
import random
import logging
from hashlib import sha256

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Proto:
    def __init__(self, logger=logging.getLogger(__name__)):
        self.packetLen = 0
        self.headerLen = 16
        self.ver = 0
        self.op = 0
        self.seq = 0
        self.body = ''
        self.maxBody = 2048
        self.logger = logger

    def pack(self):
        self.packetLen = len(self.body) + self.headerLen
        buf = struct.pack('>i', self.packetLen)
        buf += struct.pack('>h', self.headerLen)
        buf += struct.pack('>h', self.ver)
        buf += struct.pack('>i', self.op)
        buf += struct.pack('>i', self.seq)
        buf += self.body.encode()
        return buf

    def unpack(self, buf, hooks):
        if len(buf) < self.headerLen:
            self.logger.error("包头不够")
            return
        self.packetLen = struct.unpack('>i', buf[0:4])[0]
        self.headerLen = struct.unpack('>h', buf[4:6])[0]
        self.ver = struct.unpack('>h', buf[6:8])[0]
        self.op = struct.unpack('>i', buf[8:12])[0]
        self.seq = struct.unpack('>i', buf[12:16])[0]
        if self.packetLen < 0 or self.packetLen > self.maxBody:
            self.logger.error("包体长不对", "self.packetLen:", self.packetLen,
                              " self.maxBody:", self.maxBody)
            return
        if self.headerLen != self.headerLen:
            self.logger.error("包头长度不对")
            return
        bodyLen = self.packetLen - self.headerLen
        self.body = buf[16:self.packetLen]
        if bodyLen <= 0:
            return
        if self.ver == 0:
            # 这里做回调
            res_body = self.body.decode('utf-8')
            self.logger.debug("====> callback:", res_body)
            for hook in hooks:
                hook[0](*hook[1], res_body=res_body, **hook[2])
        elif self.ver == 2:
            # 解压
            self.body = zlib.decompress(self.body)
            bodyLen = len(self.body)
            offset = 0
            while offset < bodyLen:
                cmdSize = struct.unpack('>i', self.body[offset:offset + 4])[0]
                if offset + cmdSize > bodyLen:
                    return
                newProto = Proto(self.logger)
                newProto.unpack(self.body[offset: offset + cmdSize], hooks)
                offset += cmdSize
        else:
            return


class BiliClient:
    def __init__(self, roomId, key, secret, host='live-open.biliapi.com', logger=logging.getLogger(__name__), *args, **kwargs):
        self.roomId = roomId
        self.key = key
        self.secret = secret
        self.host = host
        self.call_hook = []
        self.logger = logger

    # 注册回调钩子
    def register_hook(self, hook, *args, **kwargs):
        self.call_hook.append((hook, args, kwargs))

    # 事件循环
    def run(self):
        loop = asyncio.get_event_loop()
        websocket = loop.run_until_complete(self.connect())
        tasks = [
            asyncio.ensure_future(self.recvLoop(websocket)),
            asyncio.ensure_future(self.heartBeat(websocket)),
        ]
        loop.run_until_complete(asyncio.gather(*tasks))

    # http的签名
    def sign(self, params):
        key = self.key
        secret = self.secret
        md5 = hashlib.md5()
        md5.update(params.encode())
        ts = time.time()
        nonce = random.randint(1, 100000) + time.time()
        md5data = md5.hexdigest()
        headerMap = {
            "x-bili-timestamp": str(int(ts)),
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": str(nonce),
            "x-bili-accesskeyid": key,
            "x-bili-signature-version": "1.0",
            "x-bili-content-md5": md5data,
        }

        headerList = sorted(headerMap)
        headerStr = ''

        for key in headerList:
            headerStr = headerStr + key + ":" + str(headerMap[key]) + "\n"
        headerStr = headerStr.rstrip("\n")

        appsecret = secret.encode()
        data = headerStr.encode()
        signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
        headerMap["Authorization"] = signature
        headerMap["Content-Type"] = "application/json"
        headerMap["Accept"] = "application/json"
        return headerMap

    # 获取长链信息
    def websocketInfoReq(self, postUrl, params):
        headerMap = self.sign(params)
        r = requests.post(url=postUrl, headers=headerMap,
                          data=params, verify=False)
        data = json.loads(r.content)
        self.logger.debug(data)
        return "ws://" + data['data']['host'][0] + ":" + str(data['data']['ws_port'][0]) + "/sub", data['data']['auth_body']

    # 长链的auth包
    async def auth(self, websocket, authBody):
        req = Proto(self.logger)
        req.body = authBody
        req.op = 7
        await websocket.send(req.pack())
        buf = await websocket.recv()
        resp = Proto(self.logger)
        resp.unpack(buf, [])
        respBody = json.loads(resp.body)
        if respBody["code"] != 0:
            self.logger.debug("auth 失败")
        else:
            self.logger.debug("auth 成功")

    # 长链的心跳包
    async def heartBeat(self, websocket):
        while True:
            await asyncio.ensure_future(asyncio.sleep(20))
            req = Proto(self.logger)
            req.op = 2
            await websocket.send(req.pack())
            self.logger.debug("[BiliClient] send heartBeat success")

    # 长链的接受循环
    async def recvLoop(self, websocket):
        self.logger.debug("[BiliClient] run recv...")
        while True:
            recvBuf = await websocket.recv()
            resp = Proto(self.logger)
            resp.unpack(recvBuf)

    async def connect(self):
        postUrl = "https://%s/v1/common/websocketInfo" % self.host
        params = '{"room_id":%s}' % self.roomId
        addr, authBody = self.websocketInfoReq(postUrl, params)
        self.logger.debug(addr, authBody)
        websocket = await websockets.connect(addr)
        await self.auth(websocket, authBody)
        return websocket
