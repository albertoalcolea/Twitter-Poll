from tabulate import tabulate

from storage import Storage


storage = Storage()
results = storage.get_results()

if not results:
    print 'There are not results'
else:
    table_body = [(u'#{0}'.format(r[0]), r[1]) for r in results]
    print tabulate(table_body, headers=('hashtag', 'votes'), numalign="right")
