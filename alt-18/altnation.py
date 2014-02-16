import httplib2
import os
import sys
import urllib,re

from apiclient.discovery import build
from apiclient.errors import HttpError
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
CLIENT_SECRETS_FILE = "alt18_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the %s file
found at: %s
""" % (CLIENT_SECRETS_FILE, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE)))

def word_difference(a,b):
	if not hasattr(word_difference, "memo"):
		word_difference.memo = {}
	if (a,b) in word_difference.memo: return word_difference.memo[(a,b)]
	if len(a) == 0:
		ret = len(b)
	elif len(b) == 0:
		ret = len(a)
	else:
		ret = min(word_difference(a,b[1:]) + 1, word_difference(a[1:], b) + 1,
			word_difference(a[1:], b[1:]) + (0 if a[0] == b[0] else 1))
	word_difference.memo[(a,b)] = ret
	return ret

class YouTube:
	YOUTUBE_API_SERVICE_NAME = "youtube"
	YOUTUBE_API_VERSION = "v3"
	YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
	def __init__(self,pid):
		self.playlistId = pid
		flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
		  message=MISSING_CLIENT_SECRETS_MESSAGE,
		  scope=YouTube.YOUTUBE_READ_WRITE_SCOPE)

		storage = Storage("%s-oauth2.json" % sys.argv[0])
		credentials = storage.get()

		if credentials is None or credentials.invalid:
			flags = argparser.parse_args()
			credentials = run_flow(flow, storage, flags)
		self.youtube = build(YouTube.YOUTUBE_API_SERVICE_NAME, YouTube.YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
	
	def search(self, song):
		search_response = self.youtube.search().list(q=song, part="snippet",maxResults=2).execute()
		score = 100
		best_match = None
		for result in search_response.get("items", []):
			if result["id"]["kind"] == "youtube#video":
				wd = word_difference(song.lower(),result["snippet"]["title"].lower())
				if (wd < score):
					best_match = result["id"]["videoId"]
					score = wd
		return best_match
	
	def update_playlist(self, date, countdown_video_ids):
		playlist = self.youtube.playlistItems().list(part="id,snippet", playlistId=self.playlistId, maxResults=50).execute()
		playlist_video_ids = [ item["snippet"]["resourceId"]["videoId"] for item in playlist["items"] ]
		playlist_item_ids = dict([ (item["snippet"]["resourceId"]["videoId"], item["id"]) for item in playlist["items"] ])
		old_video_ids = set(playlist_video_ids) - set(countdown_video_ids)
		new_list = countdown_video_ids + list(old_video_ids)
		for position,video_id in enumerate(new_list):
			if video_id not in playlist_item_ids:
				print "Inserting ",video_id
				self.youtube.playlistItems().insert(part="snippet",
						body={
						'snippet': {
							'playlistId': self.playlistId, 
							'resourceId': {
								'kind': 'youtube#video',
								'videoId': video_id,
							},
							'position': position
						}
					}
				).execute()
			else:
				print "Updating ",video_id
				self.youtube.playlistItems().update(part="id,snippet",
						body={
						'snippet': {
							'playlistId': self.playlistId, 
							'resourceId': {
								'kind': 'youtube#video',
								'videoId': video_id,
							},
							'position': position,
						},
						'id': playlist_item_ids[video_id],
					}
				).execute()
		self.youtube.playlists().update(
			part="id,snippet",
				body={
					'snippet': {
						'title': "AltNation: The Alt-18 Countdown",
						'description':"This playlist was last generated for the week of %s" % date,
					},
					'id': self.playlistId,
				}
		).execute()
class AltNationScraper:
	source = "http://www.siriusxm.com/altnation"
	song_regex = re.compile("\d+. (.+) &ndash; &ldquo;(.+)&rdquo;")
	week_regex = re.compile("Week of (.+)")
	def scrape(self):
		f = urllib.urlopen(AltNationScraper.source)
		self.soup = BeautifulSoup(f.read())
		week = self.soup.find("strong", text=AltNationScraper.week_regex)
		week_match = AltNationScraper.week_regex.search(week)
		self.week = week_match.group(1)
		scrape_list = self.soup.findAll(text=AltNationScraper.song_regex)
		self.songs_list = []
		for txt in scrape_list:
			song_match = AltNationScraper.song_regex.search(txt)
			song = '{artist} {title} OFFICIAL'.format(artist=song_match.group(1), title=song_match.group(2))
			self.songs_list += [ song ]
	
yt = YouTube("PLxoiiHIlEHP644dlUDpn1zfzYH6MzPrvR")
scraper = AltNationScraper()
video_id_list = []
scraper.scrape()
for song in scraper.songs_list:
	vid = yt.search(song)
	if vid:
		video_id_list += [ vid ]
yt.update_playlist(scraper.week, video_id_list)	
