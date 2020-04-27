from aiohttp import web

from app.app import Executor, JabberClient, RequestParser, Config


config = Config()
executor = Executor(JabberClient(config.get('bot_jid'), config.get('bot_pass')))


async def handle(request):
    try:
        parsed = await RequestParser.parse(request)
        await executor.execute(parsed)
    except RuntimeError as e:
        print(e)
        return web.Response(body=str(e), status=500)
    else:
        return web.Response()


app = web.Application()
app.add_routes([web.post('/', handle)])

web.run_app(app, host='0.0.0.0', port=8080)

