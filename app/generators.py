#!/usr/bin/python
#File for confgiuring dynamic template information

def config_generators(app):
  @app.context_processor
  def get_nav_icons():
    return dict(nav_icons=[
      {"name": "Home",      "src" : "/replays",  "img" : "preferences-desktop-gaming.svg",},
      # {"name": "GitHub",    "src" : "/github",   "img" : "github-desktop.svg",},
      # {"name": "Games",     "src" : "/games",    "img" : "spacefm.svg",},
      {"name": "Upload",    "src" : "/upload",   "img" : "dconf-editor.svg",},
      # {"name": "CV",        "src" : "/cv",       "img" : "scinotes.svg",},
      # {"name": "About",     "src" : "/about",    "img" : "preferences-desktop-emoticons.svg",},
      # {"name": "Settings",  "src" : "/settings", "img" : "palapeli.svg",},
      # {"name": "AJAX Test", "src" : "/thing",    "img" : "com.github.artemanufrij.hashit.svg",},
      ])

  @app.context_processor
  def get_language_proficiencies():
    return dict(lang_profs=[
      {"name": "C++",        "level" : "Proficient In",         "img" : "cplusplus-original.svg",},
      {"name": "Python",     "level" : "Proficient In",         "img" : "python-original.svg",},
      {"name": "JavaScript", "level" : "Proficient In",         "img" : "javascript-original.svg",},
      {"name": "PHP",        "level" : "Proficient In",         "img" : "php-original.svg",},
      {"name": "Bash",       "level" : "Proficient In",         "img" : "bash.png",},

      {"name": "C",          "level" : "Competent In",          "img" : "c-original.svg",},
      {"name": "SQL",        "level" : "Competent In",          "img" : "sql.png",},

      {"name": "C#",         "level" : "Have Experience With",  "img" : "csharp-original.svg",},
      {"name": "Java",       "level" : "Have Experience With",  "img" : "java-original.svg",},
      {"name": "Node.js",    "level" : "Have Experience With",  "img" : "nodejs-original.svg",},
      ])

  @app.context_processor
  def utility_functions():
    #Check if P1 / P2 has a higher value for a statistic and highlight if so
    def hl_if_higher(replay,index,key):
      return "hl-green" if replay["p"][index-1][key] > replay["p"][2-index][key] else ""
    #Check if P1 / P2 has a lower value for a statistic and highlight if so
    def hl_if_lower(replay,index,key):
      return "hl-green" if replay["p"][index-1][key] < replay["p"][2-index][key] else ""
    return dict(hl_if_higher=hl_if_higher,hl_if_lower=hl_if_lower)
