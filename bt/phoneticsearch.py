import sys

class StringGroup:
	'''A class that groups strings according to a list of sequentially applied rules'''
	
	def __init__(self):
		self.groups = {}
		self.rules = []

	def addRule(self, rule):
		'''
		Adds a new rule to the NameList system
		@param rule: A function that is appended to the list of rules for grouping
		'''
		self.rules.append(rule)

	def _get_hash(self, s):
		_hash = s
		for rule in self.rules:
			_hash = rule(_hash)
		return _hash
	
	def addGroup(self, s):
		'''
		Adds a group matching a string based on the list of existing rules
		@param string: A string that would match a given group
		''' 
		_hash = self._get_hash(s)
		if _hash not in self.groups:
			self.groups[_hash] = []
	
	def addString(self, s):
		'''
		Adds a string to an existing group based on the list of existing rules
		@param string: The string to add
		''' 
		_hash = self._get_hash(s)
		if _hash in self.groups:
			self.groups[_hash].append(s)
	
	def getGroup(self, s):
		'''
		Returns the group of strings that match the given string
		@param string: The string to match
		@return: A list containing the matching strings
		'''
		_hash = self._get_hash(s)
		return self.groups[_hash] if _hash in self.groups else []
	

if __name__ == '__main__':
	def getEquivalent(s):
		equivalents = [ 'aeiou', 'cgjkqsxyz', 'bfpvw', 'dt', 'mn' ]
		ret = ''
		for c in s:
			ec = c
			for e in equivalents:
				if c in e:
					ec = e[0]
					break
			ret += ec
		return ret
						
	phoneticSearch = StringGroup()
	
	#Rules are added in the order they will be applied.
	phoneticSearch.addRule(lambda s: ''.join([ c for c in s if c.isalpha() ]))
	phoneticSearch.addRule(lambda s: s.lower())
	phoneticSearch.addRule(lambda s: s[0] + ''.join( c for c in s[1:] if c not in 'aeihouwy' ))
	phoneticSearch.addRule(getEquivalent)
	phoneticSearch.addRule(lambda s: s[0] + ''.join( s[i] for i in range(1,len(s)) if s[i] != s[i-1] ))
	
	for surname in sys.argv[1:]:
		phoneticSearch.addGroup(surname.strip())

	for surname in sys.stdin:
		phoneticSearch.addString(surname.strip())
	
	for surname in sys.argv[1:]:
		print surname + ': ' + ', '.join(phoneticSearch.getGroup(surname.strip()))
