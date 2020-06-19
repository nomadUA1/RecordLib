from __future__ import annotations
from RecordLib.crecord import Person
from RecordLib.crecord import Case
from .re_parse_cp_pdf import parse_cp_pdf
from .re_parse_mdj_pdf import parse_mdj_pdf
from typing import Union, BinaryIO, List, Tuple


class Docket:
    @staticmethod
    def from_pdf(pdf: Union[BinaryIO, str], court="CP") -> Tuple[Docket, List[str]]:
        """ Create a Docket from a pdf file. """
        if court == "CP":
            defendant, cases, errors = parse_cp_pdf(pdf)
        elif court == "MDJ":
            defendant, cases, errors = parse_mdj_pdf(pdf)
        else:
            # if no court is identified, try them all, and see what works best.
            d_cp, cases_cp, err_cp = parse_cp_pdf(pdf)
            d_mdj, cases_mdj, err_mdj = parse_mdj_pdf(pdf)
            cases_cp[0].completeness()
            if cases_cp[0] is None and cases_mdj[0] is None:
                return Docket(None, None), ["Could not determine the parser to use."]
            elif cases_cp[0] is None:
                defendant, cases, errors = d_mdj, cases_mdj, err_mdj
            elif cases_mdj[0] is None:
                defendant, cases, errors = d_cp, cases_cp, err_cp
            elif cases_cp[0].completeness() > cases_mdj[0].completeness():
                defendant, cases, errors = d_cp, cases_cp, err_cp
            else:
                defendant, cases, errors = d_mdj, cases_mdj, err_mdj
        # parse functions always return a 4-tuple, (defendant, a list of cases, a list of errors, and optionally some raw parsed source.)
        # a docket, by definition, is only about one case, so we take the 0th element of the case list that this parser returns.
        return Docket(defendant, cases[0]), errors

    def __init__(self, defendant: Person, case: Case) -> None:
        self._defendant = defendant
        self._case = case
