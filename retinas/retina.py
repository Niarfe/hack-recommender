


class Retina:
    def __init__(self, _trained_som, _word_vectors):
        self.som = _trained_som
        self.vecs = _word_vectors
        self.word_to_loc = {}
        self.fingerprint = {}
        self._generate()

    def _generate():


    def location(word):
        return self.word_to_loc[word]

    def fingerprint(word):
        return self.fingerprint[word]

    def fingerprint_x_y(word):
        xarr = []
        yarr = []
        for tup in self.fingerprint(word):
            xarr.append(tup[0])
            yarr.append(tup[1])
        
        return (xarr, yarr)
    
