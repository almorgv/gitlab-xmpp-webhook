import aioxmpp
import asyncio
import json
import os


from jinja2 import Environment, PackageLoader, TemplateNotFound


class Config:
    def __init__(self, config_dir='config'):
        self._config_default_path = os.path.join(config_dir, 'config.default.json')
        self._config_path = os.path.join(config_dir, 'config.json')
        self._config = None

    def _read(self):
        with open(self._config_default_path) as f:
            self._config = json.load(f)
        try:
            with open(self._config_path) as f:
                self._config.update(json.load(f))
        except FileNotFoundError:
            pass

        for k, v in self._config.items():
            self._config[k] = os.getenv(k.upper(), v)

    def get(self, key):
        if self._config is None:
            self._read()
        return self._config.get(key)


class TemplateRegistry:
    template_environment = Environment(loader=PackageLoader('app', 'templates'), trim_blocks=True, lstrip_blocks=False)

    @staticmethod
    def render(name, data):
        template = TemplateRegistry.template_environment.get_template(name)
        return template.render(data=data).replace('    ', '')


class ParsedRequest:
    def __init__(self, jids, muc_jids, data, kind='unknown'):
        self.jids = jids
        self.muc_jids = muc_jids
        self.data = data
        self.kind = kind


class RequestParser:
    @staticmethod
    async def parse(req) -> ParsedRequest:
        jids = req.rel_url.query.getall('jid', [])
        muc_jids = req.rel_url.query.getall('muc_jid', [])
        if not len(jids) and not len(muc_jids):
            raise RuntimeError("No jids specified. "
                               "Pass `jid` (or `muc_jid` for group chat) in GET parameters. "
                               "Multiple jid parameters are available")
        try:
            data = await req.json()
            print(data)
        except Exception as e:
            raise RuntimeError("Request data is not valid json: {}".format(e)) from e
        else:
            return ParsedRequest(jids, muc_jids, data, data.get('object_kind'))


class JabberClient:
    def __init__(self, jid: str, password: str, nick_name=None):
        self._jid = jid
        self._nick_name = nick_name
        if self._nick_name is None:
            self._nick_name = jid.split('@')[0] if '@' in jid else 'tcgl_bot'
        self._client = aioxmpp.PresenceManagedClient(
            aioxmpp.JID.fromstr(jid),
            aioxmpp.make_security_layer(password, no_verify=True)
        )
        self._muc = self._client.summon(aioxmpp.muc.MUCClient)
        self._stream = None

    async def _get_stream(self):
        if self._stream is None or not self._client.established:
            self._stream = await self._client.connected().__aenter__()
        return self._stream

    async def send_message(self, jid, message):
        stream = await self._get_stream()
        msg = JabberClient._make_message(jid, aioxmpp.MessageType.CHAT, message)
        await stream.send(msg)

    async def send_chat_message(self, jid, message):
        stream = await self._get_stream()
        room, _ = self._muc.join(aioxmpp.JID.fromstr(jid), self._nick_name)
        msg = JabberClient._make_message(jid, aioxmpp.MessageType.GROUPCHAT, message)
        await stream.send(msg)

    @staticmethod
    def _make_message(jid, type, data):
        msg = aioxmpp.Message(to=aioxmpp.JID.fromstr(jid), type_=type)
        # None is for "default language"
        msg.body[None] = data
        return msg


class Executor:
    def __init__(self, jabber_client: JabberClient):
        self._jabber_client = jabber_client

    async def execute(self, parsed_request: ParsedRequest):
        try:
            msg = TemplateRegistry.render(parsed_request.kind, parsed_request.data)
        except TemplateNotFound:
            pass
        else:
            if not len(msg):
                return
            cor = []
            for j in parsed_request.jids:
                cor.append(self._jabber_client.send_message(j, msg))
            for j in parsed_request.muc_jids:
                cor.append(self._jabber_client.send_chat_message(j, msg))
            await asyncio.gather(*cor)
