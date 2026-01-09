from dataclasses import dataclass
from typing import Callable, Never


type Pierce[P, Q] = Callable[[Callable[[Callable[[P], Q]], P]], P]


@dataclass(repr=True)
class LEMLeft[P]:
    p: P


@dataclass(repr=True)
class LEMRight[P]:
    np: Callable[[P], Never]


type LEM[P] = LEMLeft[P] | LEMRight[P]


type DNE[P] = Callable[[Callable[[Callable[[P], Never]], Never]], P]


def absurd[P](n: Never) -> P:
    return n


def dne_to_pierce[P, Q](dnep: DNE[P]) -> Pierce[P, Q]:
    def piercep(funcp: Callable[[Callable[[P], Q]], P]) -> P:
        def nnp(np: Callable[[P], Never]) -> Never:
            def ccp(p: P) -> Q:
                return absurd(np(p))

            p = funcp(ccp)
            return np(p)

        return dnep(nnp)

    return piercep


def pierce_to_dne[P](piercep: Pierce[P, Never]) -> DNE[P]:
    def dnep(nnp: Callable[[Callable[[P], Never]], Never]) -> P:
        def funcp(ccp: Callable[[P], Never]) -> P:
            def np(p: P) -> Never:
                return ccp(p)

            return absurd(nnp(np))

        return piercep(funcp)

    return dnep


def pierce_to_lem[P](piercel: Pierce[LEM[P], Never]) -> LEM[P]:
    def funcl(ccl: Callable[[LEM[P]], Never]) -> LEM[P]:
        def np(p: P) -> Never:
            return ccl(LEMLeft(p))

        return LEMRight(np)

    return piercel(funcl)


def lem_to_pierce[P, Q](lem: LEM[P]) -> Pierce[P, Q]:
    def piercep(funcp: Callable[[Callable[[P], Q]], P]) -> P:
        match lem:
            case LEMLeft(p):
                return p

            case LEMRight(np):

                def ccp(p: P) -> Q:
                    return absurd(np(p))

                return funcp(ccp)

    return piercep


def dne_to_lem[P](dnel: DNE[LEM[P]]) -> LEM[P]:
    def nnl(nl: Callable[[LEM[P]], Never]) -> Never:
        def np(p: P) -> Never:
            return nl(LEMLeft(p))

        return nl(LEMRight(np))

    return dnel(nnl)


def lem_to_dne[P](lem: LEM[P]) -> DNE[P]:
    def dnep(nnp: Callable[[Callable[[P], Never]], Never]) -> P:
        match lem:
            case LEMLeft(p):
                return p

            case LEMRight(np):
                return absurd(nnp(np))

    return dnep


def test_lem[P](lem: LEM[P], q: P) -> None:
    match lem:
        case LEMLeft(p):
            print(p)
        case LEMRight(np):
            np(q)
