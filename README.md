# MPD Combiner
A simple script to combine adaptation sets from multiple media presentation descriptor (MPD) files.

## Assumptions
The script will only append adaptation set tags from several MPD files into one file. It does this only through simple
XML parsing, and it does not guarantee that the result is a valid and usable MPD file.

## Usage
### Install the required tools
The requirements are [x264](http://www.videolan.org/developers/x264.html) and [GPAC](http://gpac.io).
On Ubuntu, install using:
```
sudo apt install gpac x264
```

### Create input video files
Create x264 files for the different bitrates. To create two files in 4:3 aspect ratio with 2400K and 800k bitrate, you can use the following commands:
```
x264 --output intermediate_2400k.264 --fps 24 --preset slow --bitrate 2400 --vbv-maxrate 4800 --vbv-bufsize 9600 --min-keyint 48 --keyint 48 --scenecut 0 --no-scenecut --pass 1 --video-filter "resize:width=960,height=720" inputvideo.mkv
```
```
x264 --output intermediate_800k.264 --fps 24 --preset slow --bitrate 800 --vbv-maxrate 1600 --vbv-bufsize 9600 --min-keyint 48 --keyint 48 --scenecut 0 --no-scenecut --pass 1 --video-filter "resize:width=640,height=480" inputvideo.mkv
```
Package the files into MP4 containers:
```
MP4Box -add intermediate_2400k.264 -fps 24 output_2400k.mp4
```
```
MP4Box -add intermediate_800k.264 -fps 24 output_800k.mp4
```

### Create fragments
```
MP4Box -dash 4000 -frag 4000 -rap -segment-name segment_2400k output_2400k.mp4
```
```
MP4Box -dash 4000 -frag 4000 -rap -segment-name segment_800k output_800k.mp4
```

### Combine the files
The above commands should output a bunch of files including the files `output_2400k_dash.mpd` and `output_800k_dash.mpd`. To combine these files run the following command from the same directory as this README:
```
python -m mpd_combiner -o <path to output file> <input files>
```
E.g when the MPD files are in the `~/mpd` directory:
```
python -m mpd_combiner -o ~/mpd/output.mpd ~/mpd/output_2400k_dash.mpd ~/mpd/output_800k_dash.mpd
```
You can also use wildcards for the input files, e.g:
```
python -m mpd_combiner -o ~/mpd/output.mpd ~/mpd/output_*_dash.mpd
```

### In-depth explanations of the commands
The above commands were adapted from [MPEG-DASH Content Generation with MP4Box and x264](https://bitmovin.com/mp4box-dash-content-generation-x264/), where they are explained in detail.
