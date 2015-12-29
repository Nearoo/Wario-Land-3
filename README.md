# Wario Land 3 in Pygame
A remake of the GBC-Game "Wario Land 3" using Pygame for Python.  
  
Screenshot:  
![Wario Land 3 Screenshot](http://i.imgur.com/ucCK80E.png)  
Currently, the level visible on the screenshot is the only one in existence.   
Also, even tough everything is set up for it, Wario does not interact with anything except solid blocks.  
Loading of new levels is also prepared (and tested) but no trigger that would activate it in-game is implemented.

######Tilesets and spritesheets were found on following pages:  
* [wariolandlad.eu.pn](http://wariolandland.eu.pn/wario-land-3/index.php) (take a look, this is crazy!),
* [mfgg.net](http://www.mfgg.net/index.php?act=resdb&param=01&c=1&o=&filter=4.100)
* [vg-resource.com](http://www.vg-resource.com/post-392196.html)  
* [mariouniverse.com](http://www.mariouniverse.com/sprites/gbc/wl3)
  
...and then spearated apart and ordered using the  [Pyxeledit](http://pyxeledit.com/) editor.



If you want to create your own levels you can do so easily using the [Tiled](http://www.mapeditor.org/)-map editor. Just edit the file `Forest_N1_1.tmx`, everything is perfectly set up. Moving entities like Wario or Spearheads go onto the 'game_actors', while tiles (=blocks) regarding the leveldesign belong to the layer `main`. Every tile has the property `material_group`. Change this to `solid`, `hard-break`  or `soft-break` to enable collision, or to anything else to disable it.
![Tile editor preview](http://i.imgur.com/Qprh2bY.png)

#####License:
Everything of this project that I created (which means spritesheets & tilesets are *not* included) stands under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/)-License - which means you're able to use and share my work at you liking. If you want to use this, I'd love to hear something from you!
