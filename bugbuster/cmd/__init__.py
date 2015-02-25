import sys

from oslo.config import cfg

from bugbuster.utils import gerrit


CONF = cfg.CONF

opts = [
    cfg.StrOpt('exceptions',
               default='./exceptions.txt',
               help='Exceptions file'),
]

CONF.register_opts(opts)


EXCEPTIONS = ["128497"]


def main():
    gerrit_api = gerrit.GerritAPI()
    url = ('message:Closes+NOT+label:Verified<=-1+'
           'label:Verified+status:open+'
           'NOT+label:Code-Review<=-1+'
           'project:openstack/nova+'
           'branch:master')
    changes = gerrit_api.get_changes(url)
    easieast = []
    for change in changes:
        if (change['_number'] not in EXCEPTIONS
                and not infile(str(change['_number']))
                and easy_review(change)):
            easieast.append(change)
    easieast = sorted(easieast, key=lambda k: k['_number'])
    for easy in easieast:
        print_out(easy)


def infile(word):
    # We should cache the stream...
    with open(CONF.exceptions, 'r+') as f:
        out = f.read()
    return word in out


def easy_review(change):
    score = 0
    files = change['revisions'].values()[0]['files']
    for name in files:
        score += 10
        ld = files[name].get('lines_deleted', 0)
        li = files[name].get('lines_inserted', 0)
        score = score + li + ld
    return True if score < 100 else False


def print_out(change):
    subject = change['subject']
    url = "https://review.openstack.org/#/c/%d/" % change['_number']
    print "%s - %s" % (subject, url)


if __name__ == 'main':
    sys.exit(main())
