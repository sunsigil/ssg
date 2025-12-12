#!/usr/bin/env python3

import importlib.util
import os;
import pages;
from pathlib import Path;
import importlib;
import sys;
from html_writer import *;
import shutil;
from builder import Builder;
import postprocessor;

def _prepare_pythonpath(env):
	path = os.environ.get("PYTHONPATH", str(env["src_path"])).split(os.pathsep);
	if env["src_path"] not in path:
		path.append(str(env["src_path"]));
	os.environ["PYTHONPATH"] = os.pathsep.join(path);

def _load_module(path):
	name = path.stem;
	spec = importlib.util.spec_from_file_location(name, path);
	module = importlib.util.module_from_spec(spec);
	sys.modules[name] = module;
	spec.loader.exec_module(module);
	return module;

def _load_modules(path):
	modules = [];
	if path.exists() and path.is_dir():
		for child in path.iterdir():
			if child.suffix == ".py":
				modules.append(_load_module(child));
	return modules;

def _run_loaders(env):
	on_load = _load_modules(env["src_path"]/"__ssg_load__");
	for module in on_load:
		module.run(env);

def _load_libs():
	_load_modules(env["src_path"]/"__ssg_lib__");

def _reify_tree(env, tree):
	if isinstance(tree, pages.NodePage):
		if not tree.out_path.exists():
			print(f"Generating directory {tree.out_path}");

			os.makedirs(tree.out_path, exist_ok=True);
		
		if not tree.is_indexed():
			print(f"Generating index for directory {tree.out_path}");
			
			html = HTMLWriter(tree.out_path/"index.html", style=env["style_path"], base=env["base_url"]);
			builder = Builder(html);

			html.start(tree.title);
			html.heading(1, tree.title);
			builder.navigator(tree);
			html.end();
			
		for child in tree.children:
			_reify_tree(env, child);
	
	elif isinstance(tree, pages.LeafPage):
		print(f"Generating page {tree.out_path}");

		module = _load_module(tree.in_path);
		os.makedirs(os.path.dirname(tree.out_path), exist_ok=True);

		html = HTMLWriter(tree.out_path, style=env["style_path"], base=env["base_url"]);

		html.start(tree.title);
		module.build(env, tree, html);
		html.end();
		
		output = open(tree.out_path, "r");
		text = output.read();
		output.close();
		text = postprocessor.process(text);
		output = open(tree.out_path, "w");
		output.write(text);
		output.close();

	elif isinstance(tree, pages.Resource):
		#print(f"Generating resource {tree.out_path}");

		shutil.copy(tree.in_path, tree.out_path);

if __name__ == "__main__":
	args = sys.argv[1:];
	if len(args) < 2:
		print("usage: ssg.py src_dir dst_dir [stylesheet] [base]");
		exit();

	env = {
		"src_path" : None,
		"dst_path" : None,
		"style_path" : None,
		"base_url" : None,
		"ignore_globs" : [
			".*",
			"__*"
		]
	};

	env["src_path"] = Path(args[0]).absolute();
	env["dst_path"] = Path(args[1]).absolute();

	if len(args) > 2:
		style_path = Path(args[2]).absolute();
		if style_path.is_relative_to(env["src_path"]):
			style_path = style_path.relative_to(env["src_path"]);
			env["style_path"] = style_path;
		else:
			print("ERROR: Stylesheet path must be relative to source path");
	
	if len(args) > 3:
		env["base_url"] = args[3];

	ignore_path =  env["src_path"]/".ssgignore";
	if ignore_path.exists():
		ignore_file = open(ignore_path, "r")
		ignore_lines = ignore_file.readlines();
		for line in ignore_lines:
			env["ignore_globs"].append(line.strip());

	_prepare_pythonpath(env);
	_run_loaders(env);
	_load_libs();

	tree = pages.contruct_tree(env);

	_reify_tree(env, tree);

