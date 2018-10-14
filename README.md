# Wario Land 3 in Pygame
A remake of the GBC-Game "Wario Land 3" using [Pygame] for Python. [Here's a YouTube video that shows it in action.](https://www.youtube.com/watch?v=5U0iEROjCWU&t=26s)

## Running on Ubuntu

```bash
sudo apt install python-pygame
git clone https://github.com/NSasquatch/Wario-Land-3.git
cd Wario-Land-3
./main.py
```

## Gameplay

The keys are placed so that they resemble the Gameboy Color keys:

key | action
--- | ---
A | move left
D | move right
L | attack
P | jump

![Wario Land 3 Screenshot](http://i.imgur.com/ucCK80E.png)  

Currently, the level visible on the screenshot is the only one in existence.   
Also, even tough everything is set up for it, Wario does not interact with anything except solid blocks.  
Loading of new levels is prepared (and tested) but no trigger that would activate it in-game is implemented.

## Tilesets

Tilesets and spritesheets were found on following pages:

* [wariolandlad.eu.pn](http://wariolandland.eu.pn/wario-land-3/index.php) (take a look, this is crazy!),
* [mfgg.net](http://www.mfgg.net/index.php?act=resdb&param=01&c=1&o=&filter=4.100)
* [vg-resource.com](http://www.vg-resource.com/post-392196.html)  
* [mariouniverse.com](http://www.mariouniverse.com/sprites/gbc/wl3)
* [spriters-resource.com](http://www.spriters-resource.com/search/?q=wario+land+3&c=5&o%5B%5D=s&o%5B%5D=g&o%5B%5D=ts&o%5B%5D=tg&o%5B%5D=p)
  
...and then spearated and ordered using the  [Pyxeledit](http://pyxeledit.com/)

If you want to create your own levels you can do so easily using the [Tiled](http://www.mapeditor.org/)-map editor. Just edit the file `Forest_N1_1.tmx`, everything is perfectly set up. Moving entities like Wario or Spearheads go onto the layer 'game_actors', while tiles (=blocks) regarding the leveldesign belong to the layer `main`. Every tile has the property `material_group` (editable on the bottom left of the screen). Change this to `solid`, `hard-break`  or `soft-break` to enable collision, or to anything else to disable it.
![Tile editor preview](http://i.imgur.com/Qprh2bY.png

##License:
Everything of this project that I created (which means spritesheets & tilesets are *not* included) stands under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/)-License - which means you're able to use and share my work at you liking. If you want to use this, I'd love to hear something from you!

[Pygame]: http://pygame.org/
