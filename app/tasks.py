import time

def example(seconds):
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')

def status(data):
  # convert array of hex to string
  fuel_level_string = ''.join(list(map(lambda x: '%x' % x, fuel_levels)))

  cars_in_pit_string = ''.join(list(map(lambda x: '%i' % x, in_pit)))
