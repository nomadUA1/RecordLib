"""
Command-line interface for conducting an automated screening of a record.
"""
from __future__ import annotations
from typing import List
from datetime import datetime
import tempfile
import os
import re
import json
import logging
import shutil
import requests
import click
from csv import DictReader
from ujs_search.services.searchujs import search_by_docket, search_by_name
from RecordLib.utilities.serializers import to_serializable
from RecordLib.crecord import CRecord, Person
from RecordLib.sourcerecords import SourceRecord
from RecordLib.sourcerecords.docket.re_parse_cp_pdf import parse_cp_pdf_text
from RecordLib.sourcerecords.docket.re_parse_mdj_pdf import parse_mdj_pdf_text
from RecordLib.sourcerecords.parsingutilities import get_text_from_pdf
from RecordLib.analysis import Analysis
from RecordLib.analysis import ruledefs as rd
from RecordLib.utilities.email_builder import EmailBuilder
from RecordLib.utilities.cleanslate_screen import by_name


logger = logging.getLogger(__name__)


def pick_pdf_parser(docket_num):
    if "CP" in docket_num or "MC" in docket_num:
        parser = parse_cp_pdf_text
    elif "MJ" in docket_num:
        parser = parse_mdj_pdf_text
    else:
        logger.error(f"   Cannot determine the right parser for: {docket_num}")
        parser = None
    return parser


def communicate_results(
    sourcerecords: List[SourceRecord],
    analysis: Analysis,
    output_json_path: str,
    output_html_path: str,
    email_address,
) -> None:
    """
    Communicate the results of the record screening.

    Right now, this just means print them out.
    """
    sources = []
    for sr in to_serializable(sourcerecords):
        sr.pop("raw_source")
        sources.append(sr)
    results = {"sourcerecords": sources, "analysis": to_serializable(analysis)}
    message_builder = EmailBuilder(sources, analysis)
    if output_json_path is not None:
        with open(output_json_path, "w") as f:
            f.write(json.dumps(results, indent=4))
        logger.info(f"    Analysis written to {output_json_path}.")
    if output_html_path is not None:
        with open(output_html_path, "w") as f:
            html_message = message_builder.html()
            f.write(html_message)
    if email_address is not None:
        message_builder.email(email_address)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--first-name", "-fn", help="First Name", required=True)
@click.option("--last-name", "-ln", help="Last Name", required=True)
@click.option("--dob", "-d", help="Date of Birth", required=True)
@click.option(
    "--date-format",
    help="Date format",
    default=r"%m/%d/%Y",
    required=False,
    show_default=True,
)
@click.option("--output-json", "-oj", help="Path to ouput the json data", default=None)
@click.option("--output-html", "-oh", help="Path to write html output", default=None)
@click.option("--email", "-e", help="Email address to send to (optional)", default=None)
@click.option(
    "--output-dir",
    "-od",
    help="Path to a directory to write downloaded pdfs.",
    default=None,
)
@click.option(
    "--log-level", help="Log Level", default="INFO", required=False, show_default=True
)
def name(*args, **kwargs):
    """
    Screen a person's public criminal record for charges that can be expunged or sealed.
    """
    __name(*args, **kwargs)


def __name(
    first_name,
    last_name,
    dob,
    date_format,
    output_json,
    output_dir,
    output_html,
    email,
    log_level,
):
    #    if output_dir is not None and not os.path.exists(output_dir):
    #        raise (ValueError(f"Directory {output_dir} does not exist."))
    logger.setLevel(log_level)
    click.echo(f"Screening {last_name}, {first_name}")
    starttime = datetime.now()
    dob = datetime.strptime(dob, date_format).date()
    by_name(first_name, last_name, dob, email, output_dir, output_json, output_html)
    endtime = datetime.now()
    elapsed = endtime - starttime
    click.echo(f"Completed csscreen in {elapsed.seconds} seconds.")


@cli.command()
@click.option(
    "--input-dir",
    "-i",
    help="Path to directory containing docket_sheet files to parse.",
)
@click.option("--output-json", "-oj", help="Path to ouput the json data", default=None)
@click.option("--output-html", "-oh", help="Path to write html output", default=None)
@click.option("--email", "-e", help="Email address to send to (optional)", default=None)
@click.option(
    "--log-level", help="Log Level", default="INFO", required=False, show_default=True
)
def dir(input_dir, output_json, output_html, email, log_level):
    """
    Analyze a record given a directory of dockets relating to a single person and write a plain-english 
    explanation of the analysis.
    """
    if not os.path.exists(input_dir):
        raise ValueError(f"Directory {input_dir} doesn't exist.")

    logger.setLevel(log_level)
    docket_files = [f for f in os.listdir(input_dir) if "docket_sheet" in f]

    source_records = []
    for df in docket_files:
        parser = pick_pdf_parser(df)
        if parser is None:
            continue
        source_records.append(
            SourceRecord(get_text_from_pdf(os.path.join(input_dir, df)), parser)
        )

    crecord = CRecord()
    for source_rec in source_records:
        crecord.add_sourcerecord(source_rec, override_person=True)

    analysis = (
        Analysis(crecord)
        .rule(rd.expunge_deceased)
        .rule(rd.expunge_over_70)
        .rule(rd.expunge_nonconvictions)
        .rule(rd.expunge_summary_convictions)
        .rule(rd.seal_convictions)
    )

    # email the results.
    communicate_results(source_records, analysis, output_json, output_html, email)

    click.echo("Finished.")


def check_exists(path):
    assert os.path.exists(path)


@cli.command()
@click.option("--input-data", "-i", help="Path to csv file with test data")
@click.option("--output", "-o", help="Path to output directory")
@click.option(
    "--num",
    "-n",
    help="Number (from top of file) to screen",
    default=None,
    required=False,
    type=int,
)
def csv(input_data: str, output: str, num: int):
    """
    Process requests for screenings in a csv file, and write the resulting screening emails into
    a directory. 

    This is for testing the screener with many names.
    """
    check_exists(input_data)
    check_exists(output)
    counter = 0
    toscreen = []
    with open(input_data, "r") as f:
        reader = DictReader(f)
        for row in reader:
            first_name = row["first_name"]
            last_name = row["last_name"]
            dob = row["dob"]
            # the data seems to have lots of duplicates, so lets remove those to avoid screening the same person multiple times.
            to_add = (first_name, last_name, dob)
            if to_add not in toscreen:
                toscreen.append(to_add)

        for (first_name, last_name, dob) in toscreen:
            __name(
                first_name,
                last_name,
                dob,
                date_format=r"%Y-%m-%d",
                output_json=None,
                output_dir=None,
                output_html=os.path.join(output, f"{first_name}_{last_name}.html"),
                email=None,
                log_level="INFO",
            )
            if num:
                counter += 1
                if counter >= num:
                    break

