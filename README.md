# VLIVE-Subs
Command-line cript to download ALL non-auto subtitles from VLIVE URLs.  
Options:  
1. `-h`: Shows help information
2. `-v`: Download video as well
3. `-d`: Only download subtitles for languages that have multiple official and/or fan subs
Files are saved in the same directory as where the script was called from.  
You can open a terminal in a directory where you want to save the files, and provide the full path to the script to run it.
# Examples
On Windows use `py`, on Mac/Linux use `python3`.  
These examples assume the terminal was opened in the same folder as the script.
## Windows
All subs from a channel:  
`py archive_vlive.py https://www.vlive.tv/channel/EF0205`  
All subs and videos from a list of URLs:  
`py archive_vlive.py -v https://www.vlive.tv/video/33627 https://www.vlive.tv/video/34247 https://www.vlive.tv/video/37518`  
Only the subtitles where a language has multiple official and/or fan subs:  
`py archive_vlive.py -d https://www.vlive.tv/video/908`
