
class Constants(object):

  class ConstError(TypeError):
    pass

  def __init__(self, **kwargs):
    for name, value in kwargs.items():
      super(Constants, self).__setattr__(name, value)

  def __setattr__(self, name, value):
    if self.__dict__.has_key(name):
      raise self.ConstError, "Can't rebind const(%s)"%name
    self.__dict__[name] = value

  def __delattr__(self, name):
    if self.__dict__.has_key(name):
      raise self.ConstError, "Can't unbind const(%s)"%name
    raise NameError, name

Actions = Constants(
  CREATE="create",
  START="start",
  STOP="stop",
  REMOVE="remove",
  ALREADYEXISTS='warnexists',
  DOESNOTEXIST='warninexistent',
  GHOSTED='warnghost'
)
