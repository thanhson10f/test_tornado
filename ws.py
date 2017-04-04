import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, Application, url
import tornadis


clients = []


class GetHandler(RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        self.render("websocket.html")

    @tornado.gen.coroutine
    def post(self):
        mess = self.get_argument("mess",None)
        result = yield client.call("PUBLISH","channel1",mess)
        print mess 
        if not isinstance(result,tornadis.TornadisException):
            self.write("post: %s" % mess)        
        self.finish()


class WSHandler(WebSocketHandler):

    @tornado.gen.coroutine
    def initialize(self):
        self.redis = tornadis.PubSubClient(autoconnect=False)
        yield self.redis.connect()
        result = yield self.redis.pubsub_subscribe("channel1")
        print result
        loop = tornado.ioloop.IOLoop.current()
        loop.add_callback(self.watch_redis)

    @tornado.gen.coroutine
    def watch_redis(self):
        while True:
            print "..."
            msg = yield self.redis.pubsub_pop_message()
            if isinstance(msg, tornadis.TornadisException):
                break
            else:
                self.write_message(msg[-1])
        self.redis.disconnect()

    def open(self, *args):
        pass

    @tornado.gen.coroutine
    def on_message(self, message):
        pass

    def on_close(self):
        print "close"
        self.redis.disconnect()


app = Application([
    url(r"/", GetHandler),
    url(r"/ws", WSHandler)
])

client = tornadis.Client(host="localhost",port=6379, autoconnect=True)
if __name__ == '__main__':
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
