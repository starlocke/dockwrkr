import os
from datetime import datetime
from pkg_resources import require
import yaml

try:  # py3
    from shlex import quote
except ImportError:  # py2
    from pipes import quote


def getPackageVersion():
  return require('dockwrkr')[0].version

def ensureList(v):
  if v:
    return [ x for x in (v if isinstance(v, (list, tuple)) else [v]) ]
  else:
    return []


def expandLocalPath(path):
  if not os.path.isabs(path):
    path = os.path.normpath(path)
    basedir = os.path.dirname(self.confFile)
    path = os.path.join(basedir, path)
  return os.path.abspath(os.path.expanduser(os.path.realpath(path)))


def walkUpForFile(self, root, findfile):
  lastRoot = root
  fileLocation = None
  while fileLocation is None and root:
    pruned = False
    for root, dirs, files in os.walk(root):
      if not pruned:
        try:
          del dirs[dirs.index(os.path.basename(lastRoot))]
          pruned = True
        except ValueError:
         pass
      if findfile in files:
        fileLocation = os.path.join(root, findfile)
        return fileLocation
    lastRoot = root
    root = os.path.dirname(lastRoot)


def dateToAgo(self, time=False):
  """
  Get a datetime object or a int() Epoch timestamp and return a
  pretty string like 'an hour ago', 'Yesterday', '3 months ago',
  'just now', etc
  """
  now = datetime.now()
  if type(time) is int:
    diff = now - datetime.fromtimestamp(time)
  elif isinstance(time,datetime):
    diff = now - time
  elif not time:
    diff = now - now
  second_diff = diff.seconds
  day_diff = diff.days

  if day_diff < 0:
    return ''

  if day_diff == 0:
    if second_diff < 10:
      return "just now"
    if second_diff < 60:
      return str(second_diff) + " seconds ago"
    if second_diff < 120:
      return "a minute ago"
    if second_diff < 3600:
      return str(second_diff / 60) + " minutes ago"
    if second_diff < 7200:
      return "an hour ago"
    if second_diff < 86400:
      return str(second_diff / 3600) + " hours ago"
  if day_diff == 1:
    return "Yesterday"
  if day_diff < 7:
    return str(day_diff) + " days ago"
  if day_diff < 31:
    return str(day_diff / 7) + " weeks ago"
  if day_diff < 365:
    return str(day_diff / 30) + " months ago"
  return str(day_diff / 365) + " years ago"

import sys
import yaml
import tempfile
import shutil
import logging
import collections
import os, errno
import hashlib
import tarfile
from time import time
from pkg_resources import Requirement, resource_filename, require
from substance.exceptions import (
  ConfigSyntaxError,
  FileSystemError,
  FileDoesNotExist
)

logger = logging.getLogger(__name__)

_yaml_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

def _dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())

def _dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))

yaml.add_representer(collections.OrderedDict, _dict_representer)
yaml.add_constructor(_yaml_mapping_tag, _dict_constructor)

def writeToFile(filename, data):
  try:
    with open(filename, "wb") as fh:
      fh.write(data)
  except Exception as err:
    raise FileSystemError("Failed to write to %s : %s" % (filename, err))
 
def writeYAML(filename, data):
  try:
    with open(filename, "w") as fileh:
      fileh.write(yaml.dump(data, default_flow_style=False))
  except Exception as err:
    raise FileSystemError("Failed to write to %s : %s" % (filename, err))

def readYAML(filename):
  try:
    stream = open(filename, "r")
    contents = yaml.load(stream)
    return contents
  except yaml.YAMLError, exc:
    msg = "Syntax error in file %s"
    if hasattr(exc, 'problem_mark'):
      mark = exc.problem_mark
      msg += " Error position: (%s:%s)" % (mark.line+1, mark.column+1)
    raise ConfigSyntaxError(msg)
  except Exception as err:
    raise FileSystemError("Failed to read configuration file %s : %s" % (filename, err))

def humanReadableBytes(num):
  for x in ['bytes','KB','MB','GB']:
    if num < 1024.0:
      return "%3.1f%s" % (num, x)
    num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def sha1sum(filename):
  sha = hashlib.sha1()
  bufsize = 65536
  with open(filename, 'rb') as fd:
    while True:
      data = fd.read(bufsize)
      if not data:
        break
      sha.update(data)
  return sha.hexdigest()

def pathComponents(path):
  folders = []
  path = os.path.normpath(path)
  while 1:
    path, folder = os.path.split(path)
  
    if folder != "":
      folders.append(folder)
    else:
      if path != "":
        folders.append(path)
      break

  folders.reverse()  
  return folders

def mergeDict(a, b, path=None):
  if path is None: path = []
  for key in b:
    if key in a:
      if isinstance(a[key], dict) and isinstance(b[key], dict):
        mergeDict(a[key], b[key], path + [str(key)])
      elif a[key] == b[key]:
        pass # same leaf value
      else:
        a[key] = b[key]
    else:
      a[key] = b[key]
  return a

def safeQuote(string):
  return quote(str(string))
 
