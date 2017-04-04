#!/usr/bin/env python

import collections, hashlib, os, shutil

block_size=65536

def hash_path(path):
	d=collections.defaultdict(bool)
	for root, dir_names, file_names in os.walk(path):
		for file_name in file_names:
			file_path=os.path.join(root, file_name)
			with open(file_path) as file:
				hasher=hashlib.sha1()
				while True:
					x=file.read(block_size)
					if len(x)==0: break
					hasher.update(x)
				d[os.path.relpath(file_path, path)]=hasher.hexdigest()
	return d

def sync_paths(src, dst):
	#get hashes
	hash_src=hash_path(src)
	hash_dst=hash_path(dst)
	#go through src hash and make sure dst is up to date
	for path, hash in hash_src.items():
		if hash_dst[path]!=hash:
			s=os.path.join(src, path)
			d=os.path.join(dst, path)
			print('{} --> {}'.format(s, d))
			x=os.path.split(d)[0]
			if not os.path.exists(x): os.makedirs(x)
			shutil.copy2(s, d)
		del hash_dst[path]
	#report leftovers in dst
	if len(hash_dst): print('leftovers in {}'.format(dst))
	for path, _ in hash_dst.items(): print(path)

if __name__=='__main__':
	import argparse
	parser=argparse.ArgumentParser()
	parser.add_argument('src')
	parser.add_argument('dst')
	args=parser.parse_args()
	sync_paths(args.src, args.dst)
