#!/usr/bin/env python

import collections, datetime, hashlib, os, shutil

block_size=65536

def timestamp(s):
	print('{:%Y-%m-%d %H:%M:%S.%f} {}'.format(datetime.datetime.now(), s))

def attempt(f):
	try: return f()
	except:
		import traceback
		timestamp('Traceback while handling exception:')
		traceback.print_stack()
		traceback.print_exc()

def pickle_link(path):
	return 'DANSSYNC_PICKLED_LINK\n'+os.readlink(path)

def hash_contents(contents):
	hasher=hashlib.sha1()
	for i in range(0, len(contents), block_size): hasher.update(contents[i:i+block_size])
	return hasher.hexdigest()

def hash_path(path):
	import time
	last_log=time.time()
	d=collections.defaultdict(bool)
	for root, dir_names, file_names in os.walk(path):
		if time.time()-last_log>10:
			timestamp('hashing {}'.format(root))
			last_log=time.time()
		for file_name in file_names:
			file_path=os.path.join(root, file_name)
			if os.path.islink(file_path):
				contents=pickle_link(file_path)
			else:
				file=attempt(lambda: open(file_path))
				if file==None: continue
				contents=file.read()
				file.close()
			d[os.path.relpath(file_path, path)]=hash_contents(contents)
	return d

def sync_paths(src, dst, test=False):
	#get hashes
	timestamp('hashing src')
	hash_src=hash_path(src)
	timestamp('hashing dst')
	hash_dst=hash_path(dst)
	#go through src hash and make sure dst is up to date
	for path, hash in hash_src.items():
		if hash_dst[path]!=hash:
			s=os.path.join(src, path)
			d=os.path.join(dst, path)
			timestamp('{} --> {}'.format(s, d))
			x=os.path.split(d)[0]
			if not os.path.exists(x): os.makedirs(x)
			if os.path.islink(s):
				timestamp('(link to {})'.format(os.readlink(s)))
				if not test:
					with open(d, 'w') as file: file.write(pickle_link(s))
			else:
				if not test:
					attempt(lambda: shutil.copy2(s, d))
		del hash_dst[path]
	#report leftovers in dst
	if len(hash_dst): timestamp('leftovers in {}'.format(dst))
	for path, _ in hash_dst.items(): print(path)

if __name__=='__main__':
	import argparse, dateutil.parser, time
	parser=argparse.ArgumentParser()
	parser.add_argument('src')
	parser.add_argument('dst')
	parser.add_argument('--period', '-p', type=int, default=0)
	parser.add_argument('--time', '-t', default=None)
	parser.add_argument('--test', action='store_true')
	args=parser.parse_args()
	if args.test:
		timestamp('testing')
		sync_paths(args.src, args.dst, test=True)
	elif args.period:
		timestamp('running with period {}'.format(args.period))
		while True:
			attempt(lambda: sync_paths(args.src, args.dst))
			if args.period==0: break
			time.sleep(args.period)
	elif args.time:
		while(True):
			d=dateutil.parser.parse(args.time)-datetime.datetime.now()
			s_day=24*60*60
			t=(s_day*d.days+d.seconds)%s_day
			timestamp('sleeping for {}'.format(datetime.timedelta(seconds=t)))
			time.sleep(t)
			attempt(lambda: sync_paths(args.src, args.dst))
	else: sync_paths(args.src, args.dst)

