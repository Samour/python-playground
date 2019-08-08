import random
import events
import sorting
import view.application as application


def debug():
  lst = []
  for i in range(15):
    lst.append(random.randint(0, 20))

  event_bus = events.EventBus()
  sorter = sorting.BubbleSort(sorting.ListState(lst, event_bus))
  sorter.sort()
  
  print(lst)


if __name__ == '__main__':
  application.main()
