# pvc
**p**oly**v**inly**c**hloride - the stuff our beloved music discs are made of <3

Two simple Python programs for an easy start-up of [xwax](http://xwax.org/) - a vinyl emulation software for linux DJs.  
Plus: A stand-alone playlist-creation program.

This is basically a project that I used to learn some new concepts of programming, especially GUI-Programming. Don't expect a professional software for all your needs!

There are 3 scripts:

* `pvc.py`  
  CLI-Program, which uses a config to generate a start-up command. Check out the small documentation I wrote in the file.  
  (Uses Playlists created by e.g. `playlistmaker.py` or the [Amarok 2 Playlist Exporter](http://wiki.xwax.org/xwax_playlist_exporter))
* `pvc-gui.py`  
  GUI-Program with settings for the start-up command. Should be relatively self-explanatory  
  (Uses Playlists created by e.g. `playlistmaker.py` or the [Amarok 2 Playlist Exporter](http://wiki.xwax.org/xwax_playlist_exporter))
* `playlistmaker.py`  
  GUI-Program, both integrated in `pvc-gui.py` as well as stand-alone to create a playlist that is readable by xwax  
  (via `-s /bin/cat` as xwax start option)

NOTE FOR `playlistmaker.py`:
It actually adds the metadata ID3 comment tag right before the actual artist tag. I did that on purpose because I overwrite all my comment tags with musical key information (via [Keyfinder](http://www.ibrahimshaath.co.uk/keyfinder/)). This way I get an additional "column" in the xwax explorer.

However, I might change that in the master branch and give this "speciality" an own branch.
