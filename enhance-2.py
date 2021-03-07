#!/usr/bin/env python3
import sys
import os
import json
import requests
from scipy.io import wavfile
from google.cloud import speech, storage
from pydub import AudioSegment

storage_bucket = 'kep-stt-clips'
storage_bucket_music = 'kep-music-clips'
storage_project = 'principal-fact-176310'
storage_client = storage.Client(project=storage_project)
bucket = storage_client.bucket(storage_bucket)
music_bucket = storage_client.bucket(storage_bucket_music)

auddio_token = sys.argv[1]

client = speech.SpeechClient()
for file_name in sys.argv[2:len(sys.argv)]:
    print('Processing: %s' % (file_name))
    file_name_s = os.path.splitext(file_name)
    file_name_ya = os.path.basename(file_name_s[0])
    print('Base name: %s' % (file_name_ya))
    mp3_file = 'output/%s.mp3' % (file_name_ya)
    audio_file = 'output-wav/%s.wav' % (file_name_ya)
    file_info = None
    with open(file_name, 'r') as infile:
        file_info = json.load(infile)
    print('Reading WAV file: %s' % (audio_file))
    samplerate, data = wavfile.read(audio_file)
    audio_length = data.shape[0] / samplerate
    samples_per_second = data.shape[0] / audio_length
    if 'captions' not in file_info:
        file_info['captions'] = {} 
    if 'songs' not in file_info:
        file_info['songs'] = {} 
    print('Bitrate: %d, Length: %d, Total samples: %d, Samples/second: %d' % (samplerate, audio_length, data.shape[0], samples_per_second))
    for segment in file_info['segments']['speech']:
        caption_key = '%.1f-%.1f' % (segment[0], segment[1])
        if not caption_key in file_info['captions']:
            segment_start = int(samples_per_second * segment[0])
            segment_end = int(samples_per_second * segment[1])
            speech_segment = bytes(data[segment_start:segment_end])

            storage_object_name = '%s-clip-%s.wav' % (file_name_ya, caption_key)
            storage_object_url = 'gs://%s/%s' % (storage_bucket, storage_object_name)
            blob = bucket.blob(storage_object_name)
            if not blob.exists(storage_client):
                print('Uploading object to storage: %s' % (storage_object_url))
                blob.upload_from_string(speech_segment)

            audio = speech.RecognitionAudio(uri=storage_object_url)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="fi-FI",
            )
            print('Recognizing audio: %s ' % (caption_key))
            operation = client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=120)
            for result in response.results:
                file_info['captions'][caption_key] = result.alternatives[0].transcript 
    
            json_output = 'json/%s.json' % (file_name_ya)  
            with open(json_output, 'w') as outfile:
                print('Writing to %s' % (json_output))
                json.dump(file_info, outfile, indent=4, sort_keys=True)

    for segment in file_info['segments']['music']:
        caption_key = '%.1f-%.1f' % (segment[0], segment[1])
        if not caption_key in file_info['captions']:
            segment_start = int(segment[0] * 1000)
            segment_end = int(segment[1] * 1000)
            if (segment_end - segment_start) > (20 * 1000): # cap to 20 seconds
                segment_end = segment_start + (20 * 1000)
            if (segment_end - segment_start) < (20 * 1000): # skip sub-20 second clips
                continue

            print('Exporting %d-%d (%d-%d ms) music clip to MP3' % (segment[0], segment[1], segment_start, segment_end))
            sound = AudioSegment.from_mp3(mp3_file)
            music_clip = sound[segment_start:segment_end]
            music_file = music_clip.export("temp.mp3", format="mp3")

            storage_object_name = '%s-music-%s.mp3' % (file_name_ya, caption_key)
            storage_object_url = 'gs://%s/%s' % (storage_bucket_music, storage_object_name)
            blob = music_bucket.blob(storage_object_name)
            if not blob.exists(storage_client):
                print('Uploading object to storage: %s' % (storage_object_url))
                blob.upload_from_file(music_file)
            
            music_url = 'https://storage.googleapis.com/%s/%s' % (storage_bucket_music, storage_object_name)
            print('Performing song recognition: %s' % (music_url))
            data = {
                'api_token': auddio_token,
                'url': music_url,
                'return': 'apple_music,spotify',
            }
            result = requests.post('https://api.audd.io/', data=data)
            if result.status_code != 200 and result.status_code != 404:
                print(result.text)
                sys.exit(1)
            results_json = json.loads(result.text)
            if results_json['result'] and 'artist' in results_json['result']:
                song_name = ''
                if 'artist' in results_json['result']:
                    song_name = '%s%s - ' % (song_name, results_json['result']['artist'])
                if 'title' in results_json['result']:
                    song_name = '%s%s' % (song_name, results_json['result']['title'])
                if 'album' in results_json['result']:
                    if 'release_date' in results_json['result']:
                        song_name = '%s (%s, %s)' % (song_name, results_json['result']['album'], results_json['result']['release_date'][0:4])
                    else:
                        song_name = '%s (%s)' % (song_name, results_json['result']['album'])
                file_info['captions'][caption_key] = song_name
                file_info['songs'][caption_key] = song_name

            json_output = 'json/%s.json' % (file_name_ya)  
            with open(json_output, 'w') as outfile:
                print('Writing to %s' % (json_output))
                json.dump(file_info, outfile, indent=4, sort_keys=True)