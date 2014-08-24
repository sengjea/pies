import urllib2,vlc,sys,wx,time,dbus,gobject
from threading import Thread
from random import choice
from dbus.mainloop.glib import DBusGMainLoop

media_list = [ "http://www.bbc.co.uk/radio/listen/live/r2_aaclca.pls",
               "http://media-ice.musicradio.com/XFM.m3u",
               "http://www.radioeins.de/live.m3u"
               ]

class main_window(wx.Frame):
    def __init__(self,parent,title,vlc_player):
        wx.Frame.__init__(self,parent,title=title,size=(100,100))
        self.button1 = wx.Button(self, wx.ID_OK,"Stop")
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy)
        self.Bind(wx.EVT_BUTTON, self.onClickButton,self.button1)
        self.Show(True)
        self.vlc_player = vlc_player

    def onClickButton(self, event):
        stop_radio()
        self.Destroy()

    def onDestroy(self,event):
        stop_radio()



class ui_thread(Thread):
    def run(self):
        app = wx.App(False)
        main_window(None, 'Internet Radio',vlc_player)
        app.MainLoop()

class volume_thread(Thread):
    def __init__(self):
        self.started = False
        self.stop_called = False
        super(volume_thread,self).__init__()

    def start(self):
        if not self.started:
            self.started = True;
        super(volume_thread,self).start()
    def run(self):
        print "Playing: Volume "+ str(vlc_player.audio_get_volume())
        vlc_player.audio_set_volume(0)
        vlc_player.audio_set_mute(False)
        vol = 0
        while vol < 80:
            if self.stop_called:
                break
            print "Volume "+ str(vlc_player.audio_get_volume())
            vol += 2
            vlc_player.audio_set_volume(vol)
            time.sleep(1)
            continue

def mediachanged_callback(event):
    print "Media Change: Volume "+ str(vlc_player.audio_get_volume())
    vlc_player.audio_set_mute(True)
    vlc_player.audio_set_volume(0)
    return

def playing_callback(event):
    vlc_player.audio_set_mute(True)
    vlc_player.audio_set_volume(0)
    my_volume_thread.start()
    return 

def parse_playlist_file(playlist_url):
    file_handle = urllib2.urlopen(playlist_url)
    play_list = []
    if playlist_url.endswith(".m3u"):
        play_list = [ url.strip() for url in file_handle.readlines() if not url.startswith("#") ]
    elif playlist_url.endswith(".pls"):
        play_list = [ str.join("=",url.split("=")[1:]).strip() for url in file_handle.readlines() if url.startswith("File") ]
    return play_list

def stop_radio():
    my_volume_thread.stop_called = True
    vlc_player.audio_set_volume(0)
    vlc_player.stop()
#
def get_power_state(Adapter):
    return Adapter.GetProperties()['Powered']


def polling_wait(function,args,result,frequency,timeout):
    while function(args) != result:
        time.sleep(frequency)
        timeout -= frequency
        if timeout < 0:
            return 0
    return 1

#dBus = dbus.SystemBus()
#Manager = dbus.Interface(dBus.get_object('org.bluez','/'), 'org.bluez.Manager')
#if not Manager or not Manager.DefaultAdapter():
#    sys.exit(1)
#Adapter = dbus.Interface(dBus.get_object('org.bluez', Manager.DefaultAdapter()) ,'org.bluez.Adapter')
#
#if not get_power_state(Adapter):
#    print "Bluetooth Off. Turning on"
#    Adapter.SetProperty('Powered',True)
#    print "Waiting for device to come up"
#    polling_wait(get_power_state,[ Adapter ], True, 2, 60)
#
#if not Adapter.FindDevice('00:02:3C:25:C4:28'):
#    sys.exit(1)
#WSAudioSink = dbus.Interface(dBus.get_object('org.bluez',Adapter.FindDevice('00:02:3C:25:C4:28')), 'org.bluez.AudioSink')
#if not WSAudioSink.IsConnected():
#    WSAudioSink.Connect()
#    polling_wait(WSAudioSink.IsConnected, [], True, 2, 60)
        
#
vlc_instance = vlc.Instance()
print str(vlc_instance.get_log_verbosity())
vlc_instance.set_log_verbosity(2)
vlc_player = vlc_instance.media_player_new()
vlc_event_manager = vlc_player.event_manager()
vlc_event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, mediachanged_callback)
vlc_event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, playing_callback)
for url in parse_playlist_file(choice(media_list)):
    if url == '':
        continue
    selected_media = vlc_instance.media_new_location(url)
    vlc_player.set_media(selected_media)

my_volume_thread = volume_thread()
my_ui_thread = ui_thread()
my_ui_thread.start()
vlc_player.play()
