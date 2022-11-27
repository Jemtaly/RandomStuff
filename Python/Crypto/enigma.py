#!/usr/bin/python3
class Rotor:
    def __init__(self, wiring, position):
        assert set(wiring) == set(range(26))
        assert position in range(26)
        self._dec = wiring.__getitem__
        self._enc = wiring.index
        self._pos = position
        self._rec = 0
    def reset(self, position):
        self._pos = position
        self._rec = 0
    def rotate(self):
        self._pos = (self._pos - 1) % 26
        self._rec = (self._rec + 1) % 26
        return self._rec == 0
    def encrypt(self, ordr):
        return (self._enc((ordr + self._pos) % 26) - self._pos) % 26
    def decrypt(self, ordr):
        return (self._dec((ordr + self._pos) % 26) - self._pos) % 26
class Reflector:
    def __init__(self, wiring):
        assert set(wiring) == set(range(26))
        assert all(wiring[wiring[i]] == i for i in range(26))
        self._ref = wiring.__getitem__
    def reflect(self, char):
        return self._ref(char)
class Plugboard:
    def __init__(self, wiring):
        assert set(wiring) == set(range(26))
        self._dec = wiring.__getitem__
        self._enc = wiring.index
    def encrypt(self, char):
        return self._enc(char)
    def decrypt(self, char):
        return self._dec(char)
class Enigma:
    def __init__(self, rotors, reflector, plugboard):
        self._rotors = rotors
        self._reflector = reflector
        self._plugboard = plugboard
    def crypt(self, ordr):
        ordr = self._plugboard.encrypt(ordr)
        for rotor in self._rotors[::+1]:
            ordr = rotor.encrypt(ordr)
        ordr = self._reflector.reflect(ordr)
        for rotor in self._rotors[::-1]:
            ordr = rotor.decrypt(ordr)
        ordr = self._plugboard.decrypt(ordr)
        for rotor in self._rotors:
            if not rotor.rotate():
                break
        return ordr
def main():
    Q = [0, 18, 24, 10, 12, 20, 8, 6, 14, 2, 11, 15, 22, 3, 25, 7, 17, 13, 1, 5, 23, 9, 16, 21, 19, 4]
    M = [0, 10, 4, 2, 8, 1, 18, 20, 22, 19, 13, 6, 17, 5, 9, 3, 24, 14, 12, 25, 21, 11, 7, 16, 15, 23]
    S = [24, 22, 7, 10, 12, 19, 23, 0, 14, 6, 9, 15, 8, 25, 20, 17, 3, 1, 18, 4, 21, 5, 11, 13, 16, 2]
    T = [10, 20, 14, 8, 25, 15, 16, 21, 3, 18, 0, 23, 13, 12, 2, 5, 6, 19, 9, 17, 1, 7, 24, 11, 22, 4]
    P = [1, 0, 2, 4, 3, 5, 13, 7, 8, 9, 24, 11, 20, 6, 14, 15, 16, 17, 22, 19, 12, 21, 18, 23, 10, 25]
    enigma_en = Enigma([Rotor(Q, 4), Rotor(M, 4), Rotor(S, 16)], Reflector(T), Plugboard(P))
    enigma_de = Enigma([Rotor(Q, 4), Rotor(M, 4), Rotor(S, 16)], Reflector(T), Plugboard(P))
    msg = 'HELLOWORLD'
    enc = ''.join(chr(enigma_en.crypt(ord(c) - 65) + 65) for c in msg)
    dec = ''.join(chr(enigma_de.crypt(ord(c) - 65) + 65) for c in enc)
    print('Msg:', msg)
    print('Enc:', enc)
    print('Dec:', dec)
if __name__ == '__main__':
    main()
