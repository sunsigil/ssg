table = {};

def register(key, value):
	table[key] = value;

def process(text):
	for pair in table.items():
		a, b = pair;
		text = text.replace(f"${a}", b);
	return text;