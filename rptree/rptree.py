# rptree.py

""" This module provides RP Tree main module. """

import os
import pathlib
import sys

PIPE = "|"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "

"""
Facilitates the generation of a DirectoryTree structure
"""
class DirectoryTree:
	def __init__(self, root_dir, dir_only=False, output_file=sys.stdout):
		self._output_file = output_file
		self._generator = _TreeGenerator(root_dir, dir_only)

	def generate(self):
		tree = self._generator.build_tree()
		if (self._output_file != sys.stdout):
			# Wrap the tree in a markdown code block and then write to file
			tree.insert(0, "```")
			tree.append("```")
			self._output_file = open(self._output_file, mode="w", encoding="UTF-8")

			with self._output_file as stream:
				for entry in tree:
					print(entry, file=stream)

"""
	TreeGenerator - responsible for generting a textual representation of the
	directory structure.
"""
class _TreeGenerator:
	def __init__(self, root_dir, dir_only=False):
		# init the passed in path as Path object
		self._root_dir = pathlib.Path(root_dir)
		self._dir_only = dir_only
		self._tree = [] # this array will hold full string representation of the tree

	'''
		Build a tree structure similar to the following:
		..\sample\
		|
		├── sub_folder_1\
		│   └── sub_folder_1_1\
		│
		│
		├── sub_folder_2\
		│   ├── sub_folder_2_1\
		│   │   └── file.txt
		│   │
		│   └── file_1.txt
		│
		├── file_1.txt
		└── file_2.txt
	'''
	def build_tree(self):
		self._tree_head()
		self._tree_body(self._root_dir)
		return self._tree

	''' 
		Builds the head of a tree which is the current directory we are 
		looking at
	'''
	def _tree_head(self):
		self._tree.append(f"{self._root_dir}{os.sep}")
		self._tree.append(PIPE)

	def _tree_body(self, directory, prefix=""):
		entries = self._prepare_entries(directory)
		entries_count = len(entries)
		for index, entry in enumerate(entries):
			# tee is used for any child entry that's not last and
			# elbow is for last entry
			# ├── non-last entry
			# └── last entry
			connector = ELBOW if index == entries_count - 1 else TEE
			if entry.is_dir():
				self._add_directory(entry, index, entries_count, prefix, connector)
			else:
				self._add_file(entry, prefix, connector)

	def _add_directory(self, directory, index, entries_count, prefix, connector):
		# add the current directory name to the tree
		self._tree.append(f"{prefix}{connector} {directory.name}{os.sep}")
		if index != entries_count - 1:
			prefix += PIPE_PREFIX
		else:
			prefix += SPACE_PREFIX
		
		# recursive call to above function with this directory as the root
		self._tree_body(directory=directory, prefix=prefix)
		self._tree.append(prefix.rstrip()) # removes all trailing spaces

	def _add_file(self, file, prefix, connector):
		self._tree.append(f"{prefix}{connector} {file.name}")

	def _prepare_entries(self, directory):
		entries = directory.iterdir()
		if self._dir_only:
			entries = [entry for entry in entries if entry.is_dir()]
		else:
			# sort the entries so that directories are returned first
			entries = sorted(entries, key=lambda entry: entry.is_file())
		return entries
