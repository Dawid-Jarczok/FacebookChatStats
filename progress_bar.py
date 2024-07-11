
class ProgressBar:
  def  __init__(self, total : int, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
      @params:
          total       - Required  : total iterations (Int)
          prefix      - Optional  : prefix string (Str)
          suffix      - Optional  : suffix string (Str)
          decimals    - Optional  : positive number of decimals in percent complete (Int)
          length      - Optional  : character length of bar (Int)
          fill        - Optional  : bar fill character (Str)
          printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
      """
    self.total = total
    self.prefix = prefix
    self.suffix = suffix
    self.decimals = decimals
    self.length = length
    self.fill = fill
    self.printEnd = printEnd
    self.last_iteration = 0
    self.on()
  
  def on(self):
    self.on_ = True

  def off(self):
    self.on_ = False

  # Print iterations progress
  def printProgressBar(self, iteration : int = None):
      """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Optional  : current iteration (Int), default increases by 1
      """
      if not self.on_:
          return
      if iteration is None:
        self.iteration = self.last_iteration + 1
      else:
         self.iteration = iteration
         
      self.last_iteration = self.iteration
      percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
      filledLength = int(self.length * self.iteration // self.total)
      bar = self.fill * filledLength + '-' * (self.length - filledLength)
      print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end = self.printEnd)
      # Print New Line on Complete
      if self.iteration == self.total: 
          print()