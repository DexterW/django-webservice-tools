import os
print os.getcwd()
from ap_streamer.core import Indexer, Decoder, Segmenter
import py_ilbc
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet, service
from twisted.internet import task
import py_ffmpeg
ONE_MB = 1024 * 1000

def ilbc_decoder(data):
    return py_ilbc.decode(20,data)


    
class ByteReceiver(Protocol):
        
    def __init__(self):
        
        self._indexer = Indexer('/var/www/web/audio_test/index.m3u', active_limit=0, target_duration=5, delete_inactive_segments=False)
        self._encoder = Decoder(decoder=py_ffmpeg.mp3_encode, callback=self._indexer.data_received)
        self._decoder = Decoder(decoder=ilbc_decoder, callback=self._encoder.data_recieved)
        self._segmenter = core.Segmenter(5 * 50 * 38, self._decoder.data_received)
        self.file_index = 1
    
    def connectionMade(self):
        print 'Connected to client.'
    
    def connectionLost(self, reason):
        print "Connection Lost"
    
    def dataReceived(self, data):
        """
         Protocol.dataReceived.
        Translates bytes into lines, and calls lineReceived (or
        rawDataReceived, depending on mode.)
        """
        self._segmenter.data_received(data)
        
class ClientFactory(Factory):
    protocol = ByteReceiver
    
    
# application object
application = service.Application("Demo application")
internet.TCPServer(11921, ClientFactory()).setServiceParent(application)

