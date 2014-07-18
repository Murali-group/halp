def TO_JSON(self):
	
	attrs = vars(self).keys()
	return([self._affinitize(attr) for attr in attrs])
