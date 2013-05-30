import os
import imaplib
import subprocess

def login(args):
    m = imaplib.IMAP4_SSL(args.server)
    m.login(args.user, args.password)
    print 'Connected to {}.'.format(args.server)

    if args.folder is None:
        status, folders = m.list()
        assert status == 'OK'
        for f in folders:
            print f 
        return m, []

    m.select(args.folder, readonly=True)
    print 'Folder {} selected.'.format(args.folder)

    result, data = m.uid('search', None, "ALL") # search and return uids instead
    assert result == 'OK'
    data = data[0]
    return m, data.split()

def new_mail(uids):

    print '{} messages found.'.format(len(uids))
    for i in uids:
        filename = os.path.join(args.repo, i)
        txtfile = filename
        zipfile = filename + '.gz'

        if os.path.exists(zipfile):
            continue

        yield i, txtfile

def download(m, i, txtfile):
        print '#{}...'.format(i),
        result, data = m.uid('fetch', i, '(RFC822)')
        data = data[0][1]
        assert result == 'OK'

        with file(txtfile, 'wt') as f:
            f.write(data)

        print '{} B'.format(len(data))
        subprocess.call(['gzip', '-f', txtfile])

def main(args):
    m, uids = login(args)
    uids = list(new_mail(uids))
    print 'Downloading {} messages.'.format(len(uids))
    for uid, txtfile in uids:
        download(m, uid, txtfile)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--server')
    p.add_argument('--folder')
    p.add_argument('--user')
    p.add_argument('--password')
    p.add_argument('--repo', default='.')
    args = p.parse_args()    

    main(args)
