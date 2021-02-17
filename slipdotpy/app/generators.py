#!/usr/bin/python
#File for configuring dynamic template information

from flask import url_for

def config_generators(app):
  @app.context_processor
  def get_navigation_data():
    return dict(nav_icons=[
      {"name": "Explore",   "src" : "/replays",  "img" : "header-player.png",   "class" : "home",     "click" : ""},
      {"name": "Stats",     "src" : "/stats",    "img" : "header-pr.png",       "class" : "stats",    "click" : ""},
      {"name": "Scan",      "src" : "/scan",     "img" : "header-search.png",   "class" : "scan",     "click" : ""},
      {"name": "Organize",  "src" : "/organize", "img" : "header-organize.png", "class" : "organize", "click" : ""},
      {"name": "Settings",  "src" : "/settings", "img" : "header-mush.png",     "class" : "settings", "click" : ""},
      ])

  @app.context_processor
  def get_character_data():
    chardata = [ #Listen in CSS order, Sheik in bottom left, Default in bottom right
      {"id" : 22, "name" : "Dr. Mario",        "intname" : "DOCTOR",  "csspos" : 0,  "colors" : 5,},
      {"id" : 8,  "name" : "Mario",            "intname" : "MARIO",   "csspos" : 1,  "colors" : 5,},
      {"id" : 7,  "name" : "Luigi",            "intname" : "LUIGI",   "csspos" : 2,  "colors" : 4,},
      {"id" : 5,  "name" : "Bowser",           "intname" : "BOWSER",  "csspos" : 3,  "colors" : 4,},
      {"id" : 12, "name" : "Peach",            "intname" : "PEACH",   "csspos" : 4,  "colors" : 5,},
      {"id" : 17, "name" : "Yoshi",            "intname" : "YOSHI",   "csspos" : 5,  "colors" : 6,},
      {"id" : 1,  "name" : "Donkey Kong",      "intname" : "KONG",    "csspos" : 6,  "colors" : 5,},
      {"id" : 0,  "name" : "Captain Falcon",   "intname" : "FALCON",  "csspos" : 7,  "colors" : 6,},
      {"id" : 25, "name" : "Ganondorf",        "intname" : "GANON",   "csspos" : 8,  "colors" : 5,},
      {"id" : 20, "name" : "Falco",            "intname" : "FALCO",   "csspos" : 9,  "colors" : 4,},
      {"id" : 2,  "name" : "Fox",              "intname" : "FOX",     "csspos" : 10, "colors" : 4,},
      {"id" : 11, "name" : "Ness",             "intname" : "NESS",    "csspos" : 11, "colors" : 4,},
      {"id" : 14, "name" : "Ice Climbers",     "intname" : "CLIMBER", "csspos" : 12, "colors" : 4,},
      {"id" : 4,  "name" : "Kirby",            "intname" : "KIRBY",   "csspos" : 13, "colors" : 6,},
      {"id" : 16, "name" : "Samus",            "intname" : "SAMUS",   "csspos" : 14, "colors" : 5,},
      {"id" : 18, "name" : "Zelda",            "intname" : "ZELDA",   "csspos" : 15, "colors" : 5,},
      {"id" : 6,  "name" : "Link",             "intname" : "LINK",    "csspos" : 16, "colors" : 5,},
      {"id" : 21, "name" : "Young Link",       "intname" : "YOUNG",   "csspos" : 17, "colors" : 5,},
      {"id" : 19, "name" : "Sheik",            "intname" : "SHEIK",   "csspos" : 18, "colors" : 5,},
      {"id" : 24, "name" : "Pichu",            "intname" : "PICHU",   "csspos" : 19, "colors" : 4,},
      {"id" : 13, "name" : "Pikachu",          "intname" : "PIKACHU", "csspos" : 20, "colors" : 4,},
      {"id" : 15, "name" : "Jigglypuff",       "intname" : "JIGGLY",  "csspos" : 21, "colors" : 5,},
      {"id" : 10, "name" : "Mewtwo",           "intname" : "MEWTWO",  "csspos" : 22, "colors" : 4,},
      {"id" : 3,  "name" : "Mr. Game & Watch", "intname" : "WATCH",   "csspos" : 23, "colors" : 4,},
      {"id" : 9,  "name" : "Marth",            "intname" : "MARTH",   "csspos" : 24, "colors" : 5,},
      {"id" : 23, "name" : "Roy",              "intname" : "ROY",     "csspos" : 25, "colors" : 5,},
      {"id" : -1, "name" : "All Characters",   "intname" : "UNKNOWN", "csspos" : 26, "colors" : 6,},
      ]
    intchardata = { c["id"] : c for c in chardata}
    return dict(chardata=chardata,intchardata=intchardata)

  @app.context_processor
  def get_stage_data():
    stagedata = [ #TODO: finish implementing
      { "id" :  8, "name" : "Yoshi's Story",      "intname": "STORY",     "legal" : True,},
      { "id" : 31, "name" : "Battlefield",        "intname": "BATTLE",    "legal" : True,},
      { "id" : 28, "name" : "Dream Land",         "intname": "OLD_PPP",   "legal" : True,},
      { "id" : 32, "name" : "Final Destination",  "intname": "LAST",      "legal" : True,},
      { "id" :  2, "name" : "Fountain of Dreams", "intname": "IZUMI",     "legal" : True,},
      { "id" :  3, "name" : "Pokemon Stadium",    "intname": "PSTADIUM",  "legal" : True,},

      { "id" : -1, "name" : "Any Stage",          "intname": "_NONE0",    "legal" : False,},
      { "id" :  4, "name" : "Peach's Castle",     "intname": "CASTLE",    "legal" : False,},
      { "id" :  5, "name" : "Kongo Jungle",       "intname": "KONGO",     "legal" : False,},
      { "id" :  6, "name" : "Brinstar",           "intname": "ZEBES",     "legal" : False,},
      { "id" :  7, "name" : "Corneria",           "intname": "CORNERIA",  "legal" : False,},
      { "id" :  9, "name" : "Onett",              "intname": "ONETT",     "legal" : False,},
      { "id" : 10, "name" : "Mute City",          "intname": "MUTECITY",  "legal" : False,},
      { "id" : 11, "name" : "Rainbow Cruise",     "intname": "RCRUISE",   "legal" : False,},
      { "id" : 12, "name" : "Jungle Japes",       "intname": "GARDEN",    "legal" : False,},
      { "id" : 13, "name" : "Great Bay",          "intname": "GREATBAY",  "legal" : False,},
      { "id" : 14, "name" : "Hyrule Temple",      "intname": "SHRINE",    "legal" : False,},
      { "id" : 15, "name" : "Brinstar Depths",    "intname": "KRAID",     "legal" : False,},
      { "id" : 16, "name" : "Yoshi's Island",     "intname": "YOSTER",    "legal" : False,},
      { "id" : 17, "name" : "Green Greens",       "intname": "GREENS",    "legal" : False,},
      { "id" : 18, "name" : "Fourside",           "intname": "FOURSIDE",  "legal" : False,},
      { "id" : 19, "name" : "Mushroom Kingdom",   "intname": "INISHIE1",  "legal" : False,},
      { "id" : 20, "name" : "Mushroom Kingdom 2", "intname": "INISHIE2",  "legal" : False,},
      { "id" : 22, "name" : "Venom",              "intname": "VENOM",     "legal" : False,},
      { "id" : 23, "name" : "Poke Floats",        "intname": "PURA",      "legal" : False,},
      { "id" : 24, "name" : "Big Blue",           "intname": "BIGBLUE",   "legal" : False,},
      { "id" : 25, "name" : "Summit",             "intname": "ICEMT",     "legal" : False,},
      { "id" : 27, "name" : "Flat Zone",          "intname": "FLATZONE",  "legal" : False,},
      { "id" : 29, "name" : "Yoshi's Island 64",  "intname": "OLD_YOSH",  "legal" : False,},
      { "id" : 30, "name" : "Kongo Jungle 64",    "intname": "OLD_KONG",  "legal" : False,},

      { "id" :  0, "name" : "Dummy",              "intname": "DUMMY",     "legal" : False,},
      { "id" :  1, "name" : "Test",               "intname": "TEST",      "legal" : False,},
      { "id" : 21, "name" : "Arcania",            "intname": "AKANEIA",   "legal" : False,},
      { "id" : 26, "name" : "Ice Top",            "intname": "ICETOP",    "legal" : False,},
      ]
    intstagedata = { s["id"] : s for s in stagedata}
    return dict(stagedata=stagedata,intstagedata=intstagedata)

  @app.context_processor
  def get_sort_data():
    sortdata = [
      { "name" : "Newly Played",    "intname": "play"     },
      { "name" : "Newly Uploaded",  "intname": "upload"   },
      ]
    return dict(sortdata=sortdata)

  @app.context_processor
  def get_costume_data():
    costdata = [
      {"id" : -1, "name" : "Any",       },
      {"id" : 0,  "name" : "Default",   },
      {"id" : 1,  "name" : "Alt 1",     },
      {"id" : 2,  "name" : "Alt 2",     },
      {"id" : 3,  "name" : "Alt 3",     },
      {"id" : 4,  "name" : "Alt 4",     },
      {"id" : 5,  "name" : "Alt 5",     },
      ]
    return dict(costdata=costdata)

  @app.context_processor
  def get_stock_data():
    stockdata = [
      {"id" : "-1",   "name" : "Any",  },
      {"id" : "0",    "name" : "0",    },
      {"id" : "gt0",  "name" : "> 0",   },
      {"id" : "lt1",  "name" : "< 1",   },
      {"id" : "1",    "name" : "1",    },
      {"id" : "gt1",  "name" : "> 1",   },
      {"id" : "lt2",  "name" : "< 2",   },
      {"id" : "2",    "name" : "2",    },
      {"id" : "gt2",  "name" : "> 2",   },
      {"id" : "lt3",  "name" : "< 3",   },
      {"id" : "3",    "name" : "3",    },
      {"id" : "gt3",  "name" : "> 3",   },
      {"id" : "lt4",  "name" : "< 4",   },
      {"id" : "4",    "name" : "4",    },
      {"id" : "gt4",  "name" : "> 4",   },
      ]
    return dict(stockdata=stockdata)

  @app.context_processor
  def get_length_data():
    lengthdata = [
      {"id" :    -1,    "name" : "Any Time",    },
      {"id" :  3600,    "name" : "1 minutes",    },
      {"id" :  7200,    "name" : "2 minutes",    },
      {"id" : 10800,    "name" : "3 minutes",    },
      {"id" : 14400,    "name" : "4 minutes",    },
      {"id" : 18000,    "name" : "5 minutes",    },
      {"id" : 21600,    "name" : "6 minutes",    },
      {"id" : 25200,    "name" : "7 minutes",    },
      {"id" : 28800,    "name" : "8 minutes",    },
      ]
    return dict(lengthdata=lengthdata)

  @app.context_processor
  def get_interaction_data():
    interactions = [
      "EDGEGUARDING",
      "TECHCHASING",
      "PUNISHING",
      "SHARKING",
      "PRESSURING",
      # "OFFENSIVE",
      "FOOTSIES",
      "POSITIONING",
      # "NEUTRAL",
      "POKING",
      # "TRADING",
      # "DEFENSIVE",
      "PRESSURED",
      "GROUNDING",
      "PUNISHED",
      "ESCAPING",
      "RECOVERING",
      ]
    return dict(interactions=interactions)

  @app.context_processor
  def utility_functions():
    #Dummy no highlight function
    def no_hl(replay,index,key):
      return ""
    #Check if P1 / P2 has a higher value for a statistic and highlight if so
    def hl_if_higher(replay,index,key):
      try:
        return "hl-green" if replay["p"][index-1][key] > replay["p"][2-index][key] else ""
      except:
        return""
    #Check if P1 / P2 has a lower value for a statistic and highlight if so
    def hl_if_lower(replay,index,key):
      try:
        return "hl-green" if replay["p"][index-1][key] < replay["p"][2-index][key] else ""
      except:
        return""
    #Check if P1 / P2 has a nonzero stat
    def red_if_nonzero(replay,index,key):
      try:
        return 'hl-red' if replay["p"][index-1][key] > 0 else ""
      except:
        return""
    def frame_to_timestamp(f):
      f -= 123
      m  = f//3600
      f -= m*3600
      s  = f//60
      f -= s*60
      c  = int(100*f/60.0)
      return f"{m}:{s:02d}.{c:02d}"
    def icon_from_filename(f):
      if len(f) == 3 and f[1:] == ":\\":
        return url_for('static',filename='icons/mimetypes/drive-harddisk.svg')
      ext = f.split(".")[-1]
      if ext in ["exe"]:
        return url_for('static',filename='icons/mimetypes/wine.svg')
      if ext in ["iso"]:
        return url_for('static',filename='icons/mimetypes/media-optical.svg')
      return url_for('static',filename='icons/mimetypes/text-x-generic.svg')

    return dict(
      no_hl              = no_hl,
      hl_if_higher       = hl_if_higher,
      hl_if_lower        = hl_if_lower,
      red_if_nonzero     = red_if_nonzero,
      frame_to_timestamp = frame_to_timestamp,
      icon_from_filename = icon_from_filename,
      )
