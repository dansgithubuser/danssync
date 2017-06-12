#!/usr/bin/env python

import collections, datetime, hashlib, os, shutil

block_size=65536

def pickle_link(path):
	return 'DANSSYNC_PICKLED_LINK\n'+os.readlink(path)

def hash_contents(contents):
	hasher=hashlib.sha1()
	for i in range(0, len(contents), block_size): hasher.update(contents[i:i+block_size])
	return hasher.hexdigest()

def hash_path(path):
	d=collections.defaultdict(bool)
	for root, dir_names, file_names in os.walk(path):
		for file_name in file_names:
			file_path=os.path.join(root, file_name)
			if os.path.islink(file_path):
				contents=pickle_link(file_path)
			else:
				with open(file_path) as file: contents=file.read()
			d[os.path.relpath(file_path, path)]=hash_contents(contents)
	return d

def sync_paths(src, dst):
	try:
		#get hashes
		hash_src=hash_path(src)
		hash_dst=hash_path(dst)
		#go through src hash and make sure dst is up to date
		for path, hash in hash_src.items():
			if hash_dst[path]!=hash:
				s=os.path.join(src, path)
				d=os.path.join(dst, path)
				print('{:%Y-%m-%d %H:%M:%S.%f} {} --> {}'.format(
					datetime.datetime.now(), s, d
				))
				x=os.path.split(d)[0]
				if not os.path.exists(x): os.makedirs(x)
				if os.path.islink(s):
					print('(link to {})'.format(os.readlink(s)))
					with open(d, 'w') as file: file.write(pickle_link(s))
				else:
					try: shutil.copy2(s, d)
					except:
						import traceback
						print('Traceback while handling exception:')
						traceback.print_stack()
						traceback.print_exc()
			del hash_dst[path]
		#report leftovers in dst
		if len(hash_dst): print('leftovers in {}'.format(dst))
		for path, _ in hash_dst.items(): print(path)
	except:
		import traceback
		print('Traceback while handling exception:')
		traceback.print_stack()
		traceback.print_exc()

if __name__=='__main__':
	import argparse, dateutil.parser, time
	parser=argparse.ArgumentParser()
	parser.add_argument('src')
	parser.add_argument('dst')
	parser.add_argument('--period', '-p', type=int, default=0)
	parser.add_argument('--time', '-t', default=None)
	args=parser.parse_args()
	if args.period:
		print('running with period {}'.format(args.period))
		while True:
			sync_paths(args.src, args.dst)
			if args.period==0: break
			time.sleep(args.period)
	elif args.time:
		while(True):
			d=dateutil.parser.parse(args.time)-datetime.datetime.now()
			s_day=24*60*60
			t=(s_day*d.days+d.seconds)%s_day
			print('sleeping for {}'.format(datetime.timedelta(seconds=t)))
			time.sleep(t)
			sync_paths(args.src, args.dst)
	else: sync_paths(args.src, args.dst)

