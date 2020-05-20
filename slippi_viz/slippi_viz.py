#!/usr/bin/python
from app import create_app, db, generators #, cli
from app.models import User, Replay

import os

app = create_app()
generators.config_generators(app)

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Replay': Replay}

@app.context_processor
def config_var():
    return app.config
