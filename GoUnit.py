import sublime, sublime_plugin
import subprocess
import os

class gounitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = sublime.load_settings("GoUnit.sublime-settings")
		gopath = settings.get("GOPATH", "")
		if os.environ.get("GOPATH") == None:
			if gopath != "":
				# Set $GOPATH in this shell and add $GOPATH/bin to $PATH.
				os.environ["GOPATH"] = gopath
				os.environ["PATH"] += os.pathsep + os.path.join(gopath, "bin")
			else:
				sublime.message_dialog("GoUnit: GOPATH is not set.")
				return False
		fn = self.view.file_name()
		if fn and fn.endswith('.go') and not fn.endswith('_test.go'):
			lines = []
			for s in self.view.sel():
				line = self.function_line(s.begin())
				(row, col) = self.view.rowcol(line.begin())
				print(row)
				lines.append(str(row + 1))
			try:
				gounit = settings.get("gounit_cmd", "gounit")
				test_file = fn.replace('.go', '_test.go')
				cmd = [gounit, '-i', fn, '-o',test_file, '-l', ",".join(lines)]

				proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(output, err) = proc.communicate()
				exit_code = proc.wait()
				if exit_code != 0:
				    sublime.message_dialog("GoUnit error ("+str(exit_code)+") " + " ".join(cmd) + "\n" + str(err))
				    return False

				self.view.window().open_file(test_file)
			except OSError as e:
				sublime.message_dialog("GoUnit error: " + str(e) + ".")
				return False
			return True
		return False

	# Returns a function signature's line from a point in its body.
	def function_line(self, point):
		line = self.view.line(point)
		if self.is_end_bracket(line):
			return line
		above = line
		while not self.is_end_bracket(above) and not self.function_name(above) and above.begin() > 0:
			above = self.view.line(above.begin() - 1)
		return above

	# Return whether the line is an end bracket.
	def is_end_bracket(self, line):
		return self.view.substr(line.begin()) == '}'

	# Returns the name of the function if the given line is a method signature.
	def function_name(self, line):
		if self.view.substr(self.view.word(line.begin())) != "func":
			return None
		i = line.begin()
		while i <= line.end():
			word = self.view.word(i)
			i = word.end() + 1
			c = self.view.substr(word.end())
			if c.find("(") != -1:
				func = self.view.substr(word)
				r = self.view.word(word.begin() - 1)
				if self.view.substr(r).find(")") != -1:
					receiver = self.view.substr(self.view.word(r.begin() - 1))
					func = receiver + func
				return func
		return None
