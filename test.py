#!/usr/bin/env python

import danssync
import os, random, shutil

src='.danssync-test-src'
dst='.danssync-test-dst'

def make_random_path():
	return ''.join([random.choice('abcd/') for i in range(8)])

shutil.rmtree(src, ignore_errors=True)
shutil.rmtree(dst, ignore_errors=True)
assert not os.path.exists(src)
assert not os.path.exists(dst)

for i in range(256):
	root, file_name=os.path.split('.danssync-test-src/'+make_random_path())
	try:
		os.makedirs(root)
		with open(os.path.join(root, file_name), 'w') as file:
			file.write(make_random_path())
	except: pass
danssync.sync_paths(src, dst)
assert danssync.hash_path(src)==danssync.hash_path(dst)
