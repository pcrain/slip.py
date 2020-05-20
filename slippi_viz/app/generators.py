#!/usr/bin/python
#File for confgiuring dynamic template information

def config_generators(app):
  @app.context_processor
  def get_nav_icons():
    return dict(nav_icons=[
      {"name": "Explore",   "src" : "/replays",  "img" : "header-player.png",   "class" : "home",   "click" : ""},
      # {"name": "Upload",    "src" : "/upload",   "img" : "header-matchups.png", "class" : "mu",     "click" : ""},
      {"name": "Scan",      "src" : "/scan",     "img" : "header-search.png",   "class" : "scan",   "click" : ""},
      ])

  @app.context_processor
  def get_characters():
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
      {"id" : 15, "name" : "Jigglypyff",       "intname" : "JIGGLY",  "csspos" : 21, "colors" : 5,},
      {"id" : 10, "name" : "Mewtwo",           "intname" : "MEWTWO",  "csspos" : 22, "colors" : 4,},
      {"id" : 3,  "name" : "Mr. Game & Watch", "intname" : "WATCH",   "csspos" : 23, "colors" : 4,},
      {"id" : 9,  "name" : "Marth",            "intname" : "MARTH",   "csspos" : 24, "colors" : 5,},
      {"id" : 23, "name" : "Roy",              "intname" : "ROY",     "csspos" : 25, "colors" : 5,},
      {"id" : -1, "name" : "All Characters",   "intname" : "_NONE",   "csspos" : 26, "colors" : 6,},
      ]
    intchardata = { c["id"] : c for c in chardata}
    return dict(chardata=chardata,intchardata=intchardata)

  @app.context_processor
  def get_stages():
    stagedata = [ #TODO: finish implementing
      { "id" :  8, "name" : "Yoshi's Story",      "intname": "STORY",     "legal" : True,},
      { "id" : 31, "name" : "Battlefield",        "intname": "BATTLE",    "legal" : True,},
      { "id" : 28, "name" : "Dream Land",         "intname": "OLD_PPP",   "legal" : True,},
      { "id" : 32, "name" : "Final Destination",  "intname": "LAST",      "legal" : True,},
      { "id" :  2, "name" : "Fountain of Dreams", "intname": "IZUMI",     "legal" : True,},
      { "id" :  3, "name" : "Pokemon Stadium",    "intname": "PSTADIUM",  "legal" : True,},

      # { "id" :  0, "name" : "Dummy",              "intname": "DUMMY",     "legal" : False,},
      # { "id" :  1, "name" : "Test",               "intname": "TEST",      "legal" : False,},
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
      # { "id" : 21, "name" : "Arcania",            "intname": "AKANEIA",   "legal" : False,},
      { "id" : 22, "name" : "Venom",              "intname": "VENOM",     "legal" : False,},
      { "id" : 23, "name" : "Poke Floats",        "intname": "PURA",      "legal" : False,},
      { "id" : 24, "name" : "Big Blue",           "intname": "BIGBLUE",   "legal" : False,},
      { "id" : 25, "name" : "Summit",             "intname": "ICEMT",     "legal" : False,},
      # { "id" : 26, "name" : "Ice Top",            "intname": "ICETOP",    "legal" : False,},
      { "id" : 27, "name" : "Flat Zone",          "intname": "FLATZONE",  "legal" : False,},
      { "id" : 29, "name" : "Yoshi's Island 64",  "intname": "OLD_YOSH",  "legal" : False,},
      { "id" : 30, "name" : "Kongo Jungle 64",    "intname": "OLD_KONG",  "legal" : False,},
      ]
    intstagedata = { s["id"] : s for s in stagedata}
    return dict(stagedata=stagedata,intstagedata=intstagedata)

  @app.context_processor
  def get_sorts():
    sortdata = [
      { "name" : "Newly Played",    "intname": "play"     },
      { "name" : "Newly Uploaded",  "intname": "upload"   },
      ]
    return dict(sortdata=sortdata)

  @app.context_processor
  def get_costumes():
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
  def get_stockdata():
    stockdata = [
      {"id" : -1, "name" : "Any", },
      {"id" : 0,  "name" : "0",   },
      {"id" : 1,  "name" : "1",   },
      {"id" : 2,  "name" : "2",   },
      {"id" : 3,  "name" : "3",   },
      {"id" : 4,  "name" : "4",   },
      ]
    return dict(stockdata=stockdata)

  @app.context_processor
  def utility_functions():
    #Check if P1 / P2 has a higher value for a statistic and highlight if so
    def hl_if_higher(replay,index,key):
      return "hl-green" if replay["p"][index-1][key] > replay["p"][2-index][key] else ""
    #Check if P1 / P2 has a lower value for a statistic and highlight if so
    def hl_if_lower(replay,index,key):
      return "hl-green" if replay["p"][index-1][key] < replay["p"][2-index][key] else ""
    return dict(hl_if_higher=hl_if_higher,hl_if_lower=hl_if_lower)
