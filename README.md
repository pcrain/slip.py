# Slip.py - A Slippi replay browser, search engine, and analyzer

## Screenshots (click to zoom)
<span>
  <img title="Slip.py Index"   src="https://i.imgur.com/PvQkHQh.jpg" alt="alt text" width="200">
  <img title="Slip.py Replay1" src="https://i.imgur.com/D1NNFwq.png" alt="alt text" width="200">
  <img title="Slip.py Replay2" src="https://i.imgur.com/7wEzbE5.png" alt="alt text" width="200">
  <img title="Slip.py Stats"   src="https://i.imgur.com/WVnjri2.png" alt="alt text" width="200">
</span>

## Overview
Slip.py is designed to be a full-featured tool for managing your Slippi replays.
I created this tool in my free time so I could find replays I was looking for more easily and quickly than was possible using the standard replay browser, which suffered from slow load times and an index that made replays difficult to tell apart from one another.
The project eventually grew to include replay stats, replay analyses, and a full-fledged search engine as well, with several improvements planned for the future.

## Features
  - Fully indexed replay database with a clean visual presentation for quickly finding your matches. Thumbnails give you as much pertinent information about each replay as possible without overwhelming you with details.
  - Per-player game stats. Detailed information on your most frequent opponents, most recent opponents, and summary statistics of game wins and losses broken down by character
  - Full-featured replay search engine. Looking for that game last week where you 4-stocked a Fox with your sick DK? No problem!
  - Stats for each replay. Wondering what your average ledgedash GALINT was? Want to know how many times you accidentally full hopped instead of short hopped? Slip.py will show you all of that and much more.
  - Punish analyses. Detailed breakdowns of every move in every punish you landed + when and how you landed them, color coded for your convenience!
  - Replay organization options. Want to get rid of all of those replays where your opponent quits out in the middle of your combo on the first stock? Click one button and it's as good as done!

## Installation
  Check out the [installation instructions here](INSTALL.md)!

## Usage Tips
  - Before being able to browse replays, you need to add folders to scan. Click on the "Scan" button in the navigation bar, add at least one folder using the "Add Folder" button and navigating to a directory containing slippi files, and click "Begin Scan". The default Slippi replay location is added by default if it exists.
  - Before being able to view replays, you will need to configure the path to your Melee 1.02 ISO and Slippi Playback emulator on the "Settings" page. If you have the [Slippi Desktop app](https://slippi.gg/downloads) installed, your playback Dolphin is likely at "```C:\Users\[your login name]\AppData\Roaming\Slippi Desktop App\dolphin```".
  - Clicking the search button at the top will allow you to filter replays by a number of attributes, including characters, costumes, stage, stock counts, and game length. Additionally, you can also enter keywords into the search bar to search for specific file names, player names, and player tags.
  - The stats / analysis page for each replay shows color-coded interaction data between players, including what moves were landed during these interactions and how much damage each player did during these interactions over the course of the game. These interactions are defined near the bottom of [this page](https://github.com/pcrain/slippc).
  - You can configure the maximum number of threads to use during the replay scanning process on the Settings page of the app. The default is half the number of processors your computer has; note that using too many threads may cause your system to become unresponsive, so increase at your own risk.

## Keyboard Shortcuts
  | Command     | Description                                     |
  | :---------: | :---------------------------------------------: |
  | Left Arrow  | Go to previous replay / results page            |
  | Right Arrow | Go to next replay / results page                |
  | Up Arrow    | (On replay page) Go back to last search results |
  | Backspace   | Go back to last page in history                 |
  | Alt+Left    | Go back to last page in history                 |
  | Alt+Right   | Go forward to next page in history              |
  | F5          | Refresh current page                            |
  | F12         | Reset app                                       |


## Limitations / Known Bugs
  - Slip.py cannot currently index or show stats for games with more than two players. Indexing will be possible in the future, but analysis will likely not be added due to the complexity.
  - Slip.py / slippc were designed with the analysis of tournament-legal singles games in mind. While slip.py will try to analyze any 1 vs. 1 game, don't be surprised if analyzing your 99 stock giant Melee on Temple has some weird side effects!
  - Some sources of damage will not show up properly in the move listing, such as self-damage (Roy / Pichu), items, or Kirby copy abilities. Damage from being in the bubble is represented as "(o)".

## FAQ

### What advantages does slip.py offer over the standard Slippi Browser?
The primary advantages are faster load times, the ability to search your replays, and a different visual presentation. That said, if you're happy with the standard replay browser and are asking yourself "why do I need this one?", then you probably don't!

### I found a bug! How do I report it?
Open an issue on the issue tracker and I'll try to look into it as soon as I have time!

### Will you add X feature?
Probably not, but feel free to make suggestions! :) I have limited time to work on this project, and fixing bugs is much higher priority than adding new features. If you *really* want it, you can always add it yourself! Both slip.py and slippc are open source, so go for it.

## References
- [slippc](https://github.com/pcrain/slippc), the C++ backend used for parsing and analyzing the replays
- [Project Slippi](https://github.com/project-slippi/project-slippi) on GitHub
- Character Portraits: [20XX Ultimate Texture Pack](https://modulous.net/mod/1873/20XX%20Ultimate%20Texture%20Pack) by Acryte
- File Icons: [Papirus Dark Icon Theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)
