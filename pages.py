import re;
import glob;

class Resource:
	def __init__(self, env, path):
		self.parent = None;
		
		self.in_path = path;
		self.rel_path = path.relative_to(env["src_path"]);
		self.out_path = env["dst_path"]/self.rel_path;

		self.title = path.name;

class LeafPage:
	def __init__(self, env, path):
		self.parent = None;

		self.in_path = path;
		self.rel_path = path.relative_to(env["src_path"]).with_suffix(".html");
		self.out_path = env["dst_path"]/self.rel_path;

		text = path.read_text();
		page_line = re.search(r"#\s*PAGE\s*\(.*\)\n", text).group();
		page_expr = re.search(r"PAGE\s*\(.*\)", page_line).group();
		tokens = re.split(r"\s|\(|\)", page_expr);
		tokens = [t for t in tokens if len(t) > 0];

		self.title = " ".join(tokens[1:]);

class NodePage:
	def __init__(self, env, path):
		self.parent = None;
		
		self.in_path = path;
		self.rel_path = path.relative_to(env["src_path"]);
		self.out_path = env["dst_path"]/self.rel_path;

		self.children = [];
	
		self.title = self.rel_path.stem.title().replace("_", " ");

	def add_child(self, child):
		if child == None:
			return;
		child.parent = self;
		self.children.append(child);

	def is_indexed(self):
		for child in self.children:
			if child.out_path.name == "index.html":
				return True;
		return False;

	def is_navigable(self):
		for child in self.children:
			if isinstance(child, LeafPage):
				return True;
			elif isinstance(child, NodePage):
				return child.is_navigable();
		return False;

def _construct_tree(env, path):
	for glob_str in env["ignore_globs"]:
		matches = glob.glob(glob_str, root_dir=env["src_path"], recursive=True);
		if path.name in matches:
			return None;

	if path.is_dir():
		node = NodePage(env, path);
		for child_path in path.iterdir():
			node.add_child(_construct_tree(env, child_path));
		return node;
	elif path.suffix == ".py":
		return LeafPage(env, path);
	else:
		return Resource(env, path);

def contruct_tree(env):
	return _construct_tree(env, env["src_path"]);
