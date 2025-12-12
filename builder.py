from html_writer import HTMLWriter;
import pages;

class Builder:
	def __init__(self, html: HTMLWriter):
		self.html = html;
	
	def navigator(self, page: pages.NodePage):
		self.html.start_list();
		children = [c for c in page.children if isinstance(c, pages.LeafPage) or isinstance(c, pages.NodePage) and c.is_navigable()];
		children = sorted(children, key = lambda x: x.title);
		for child in children:
			if child.in_path.name == "index.py":
				continue;
			self.html.list_item(f"<a href={child.rel_path}>{child.title}</a>");
		self.html.end_list();
	
	def bank(self, page: pages.NodePage):
		self.html.start_list();
		children = [c for c in page.children if isinstance(c, pages.Resource)];
		children = sorted(children, key = lambda x: x.title);
		for child in children:
			if child.in_path.name == "index.py":
				continue;
			self.html.list_item(f"<a href={child.rel_path}>{child.title}</a>");
		self.html.end_list();

	def banner(self, image, height):
		self.html.image(image, style=f"display: block; margin: auto; height: {height*100}vh;");

	def gallery(self, images, height=0, borderless=False):
		self.html.open_tag("div", _class="gallery_row");
		for image in images:
			self.html.open_tag("div", _class="gallery_column");
			style = "";
			if height > 0:
				style += f"height:{height*100}vh;";
			if borderless:
				style += "border:none;";
			self.html.one_tag(
				"img", src=image, _class="gallery_image",
				style=style
			);
			self.html.close_tag();
		self.html.close_tag();